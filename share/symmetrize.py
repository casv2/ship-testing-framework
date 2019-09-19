import sys
import numpy as np
import spglib
from ase.calculators.calculator import Calculator
from ase.constraints import voigt_6_to_full_3x3_stress, full_3x3_to_voigt_6_stress

__all__ = ['refine', 'SymmetrizedCalculator']

def refine(at, symprec=0.01):
    # test orig config with desired tol
    dataset = spglib.get_symmetry_dataset(at, symprec=symprec)
    if dataset is None:
        raise ValueError("Failed to get symmetry dataset")
    print "symmetry.refine_symmetry: loose ({}) initial symmetry group number {}, international (Hermann-Mauguin) {} Hall {}".format(symprec, dataset["number"],dataset["international"],dataset["hall"])

    # symmetrize cell
    # create symmetrized rotated cell from standard lattice and transformation matrix
    symmetrized_rotated_cell = np.dot(dataset['std_lattice'].T, dataset['transformation_matrix']).T
    # SVD decompose transformation from symmetrized cell to original cell to extract rotation
    # see https://igl.ethz.ch/projects/ARAP/svd_rot.pdf Eq. 17 and 21
    # S = X Y^T, X = symm_cell.T, Y = orig_cell.T
    (u, s, v_T) = np.linalg.svd(np.dot(symmetrized_rotated_cell.T, at.get_cell()))
    rotation = np.dot(v_T.T, u.T) 
    # create symmetrized aligned cell by rotating symmetrized rotated cell
    symmetrized_aligned_cell = np.dot(rotation, symmetrized_rotated_cell.T).T
    # set new cell back to symmetrized aligned cell (approx. aligned with original directions, not axes)
    at.set_cell(symmetrized_aligned_cell, True)

    dataset = spglib.get_symmetry_dataset(at, symprec=symprec)
    if dataset is None:
        raise ValueError("Failed to get symmetry dataset")
    ## mapping_to_prim = dataset['mapping_to_primitive']

    # create primitive cell
    (prim_cell, prim_scaled_pos, prim_types) = spglib.find_primitive(at, symprec=symprec)

    #rotate to align with orig cell
    prim_cell = np.dot(rotation, prim_cell.T).T
    prim_pos = np.dot(prim_scaled_pos, prim_cell)

    # align prim cell atom 0 with atom in orig cell that maps to it
    p = at.get_positions()
    ## dp0 = p[list(mapping_to_prim).index(0),:] - prim_pos[0,:]
    real_atom_that_maps_to_prim_0 = list(dataset['mapping_to_primitive']).index(0)
    std_atom_that_maps_to_prim_0  = list(dataset['std_mapping_to_primitive']).index(0)
    dp0 = p[real_atom_that_maps_to_prim_0,:] - dataset['std_positions'][std_atom_that_maps_to_prim_0,]
    ##
    prim_pos += dp0

    # create symmetrized orig pos from prim cell pos + integer * prim cell lattice vectors
    prim_inv_cell = np.linalg.inv(prim_cell)
    for i in range(len(at)):
        # find closest primitive atom
        # there should really be a better mapping, but apparently mapping to primitive cell returned 
        # by get_symmetry_dataset() doesn't always have atom indices that actually agree with those 
        # returned by find_primitive()
        #
        # p = prim_pos + L . prim_cell
        # L = (p-prim_pos) . prim_inv_cell
        # find integer L
        L = np.dot((p[i,:]-prim_pos) , prim_inv_cell)
        i_prim = np.argmin(np.linalg.norm(L - np.round(L), axis=1))
        p[i,:] = prim_pos[i_prim,:] + np.dot(L[i_prim,:], prim_cell)
        ## dp_rounded = np.round( np.dot(p[i,:]-prim_pos[mapping_to_prim[i],:], prim_inv_cell) )
        ## p[i,:] = prim_pos[mapping_to_prim[i],:] + np.dot(dp_rounded, prim_cell)

    at.set_positions(p)

    # test final config with tight tol
    dataset = spglib.get_symmetry_dataset(at, symprec=1.0e-6)
    if dataset is None:
        raise ValueError("Failed to get symmetry dataset")
    print "symmetry.refine_symmetry: precise ({}) symmetrized symmetry group number {}, international (Hermann-Mauguin) {} Hall {}".format(1.0e-6, dataset["number"],dataset["international"],dataset["hall"])

def check(at, symprec=1.0e-6):
    dataset = spglib.get_symmetry_dataset(at, symprec=symprec)
    if dataset is None:
        print "symmetry.check failed to get symmetry"
    else:
        print "symmetry.check: prec",symprec,"got symmetry group number",dataset["number"],", international (Hermann-Mauguin)",dataset["international"],", Hall",dataset["hall"]

def prep(at, symprec=1.0e-6):
    dataset = spglib.get_symmetry_dataset(at, symprec=symprec)
    if dataset is None:
        raise ValueError("Failed to get symmetry dataset")
    print "symmetry.prep: symmetry group number",dataset["number"],", international (Hermann-Mauguin)",dataset["international"],", Hall",dataset["hall"]
    rotations = dataset['rotations'].copy()
    translations = dataset['translations'].copy()
    symm_map=[]
    scaled_pos = at.get_scaled_positions()
    for (r, t) in zip(rotations, translations):
        # print "op"
        this_op_map = [-1] * len(at)
        for i_at in range(len(at)):
            new_p = np.dot(r, scaled_pos[i_at,:]) + t
            dp = scaled_pos - new_p
            dp -= np.round(dp)
            i_at_map = np.argmin(np.linalg.norm(dp,  axis=1))
            this_op_map[i_at] = i_at_map
        symm_map.append(this_op_map)
    return (rotations, translations, symm_map)

# lattice vectors expected as row vectors (same as ASE get_cell() convention), inv_lattice is its matrix inverse (get_reciprocal_cell().T)
def forces(lattice, inv_lattice, forces, rot, trans, symm_map):
    scaled_symmetrized_forces_T = np.zeros(forces.T.shape)

    scaled_forces_T = np.dot(inv_lattice.T,forces.T)
    for (r, t, this_op_map) in zip(rot, trans, symm_map):
        # print "op "
        # print r, t, this_op_map
        transformed_forces_T = np.dot(r, scaled_forces_T)
        scaled_symmetrized_forces_T[:,this_op_map[:]] += transformed_forces_T[:,:]
    scaled_symmetrized_forces_T /= len(rot)

    symmetrized_forces = np.dot(lattice.T, scaled_symmetrized_forces_T).T

    return symmetrized_forces

# lattice vectors expected as row vectors (same as ASE get_cell() convention), inv_lattice is its matrix inverse (get_reciprocal_cell().T)
def stress(lattice, lattice_inv, stress_3_3, rot):
    scaled_stress = np.dot(np.dot(lattice, stress_3_3), lattice.T)

    symmetrized_scaled_stress = np.zeros((3,3))
    for r in rot:
        symmetrized_scaled_stress += np.dot(np.dot(r.T,scaled_stress),r)
    symmetrized_scaled_stress /= len(rot)

    symmetrized_stress = np.dot(np.dot(lattice_inv, symmetrized_scaled_stress), lattice_inv.T)
    return symmetrized_stress

class SymmetrizedCalculator(Calculator):
   implemented_properties = ['free_energy', 'energy','forces','stress']
   def __init__(self, calc, atoms, symprec=1.0e-6, *args, **kwargs):
      Calculator.__init__(self, *args, **kwargs)
      self.calc = calc
      (self.rotations, self.translations, self.symm_map) = prep(atoms, symprec=symprec)

   def get_potential_energy(self, atoms, force_consistent=True):
      return self.calc.get_potential_energy(atoms, force_consistent)

   def calculate(self, atoms, properties, system_changes):
        Calculator.calculate(self, atoms, properties, system_changes)
        if system_changes:
            self.results = {}
        if 'free_energy' in properties and 'free_energy' not in self.results:
            self.results['free_energy'] = self.calc.get_potential_energy(atoms, force_consistent=True)
        if 'energy' in properties and 'energy' not in self.results:
            self.results['energy'] = self.calc.get_potential_energy(atoms)
        if 'forces' in properties and 'forces' not in self.results:
            raw_forces = self.calc.get_forces(atoms)
            self.results['forces'] = forces(atoms.get_cell(), atoms.get_reciprocal_cell().T, raw_forces, 
                self.rotations, self.translations, self.symm_map)
        if 'stress' in properties and 'stress' not in self.results:
            raw_stress = voigt_6_to_full_3x3_stress(self.calc.get_stress(atoms))
            symmetrized_stress = stress(atoms.get_cell(), atoms.get_reciprocal_cell().T, raw_stress, self.rotations)
            self.results['stress'] = full_3x3_to_voigt_6_stress(symmetrized_stress)
