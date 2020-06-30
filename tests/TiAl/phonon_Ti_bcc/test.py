from ase import Atoms
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
import numpy as np
import model
from ase.optimize import BFGS
import os
import sys
from ase.io import read, write

import phonopy
from phonopy.phonon.band_structure import get_band_qpoints_and_path_connections

calc = model.calculator

model_name = model.model_dir.split("/")[-1]

def get_crystal():
    at = read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bulk.xyz"))

    cell = PhonopyAtoms(symbols=at.get_chemical_symbols(),
                    cell=at.get_cell(),
                    positions=at.get_positions())

    return cell

def phonopy_pre_process(cell, supercell_matrix=None):

    smat = [[3,0,0], [0,3,0], [0,0,3]]


    phonon = Phonopy(cell,
                     smat)

    phonon.generate_displacements(distance=0.2)
    print("[Phonopy] Atomic displacements:")
    disps = phonon.get_displacements()
    for d in disps:
        print("[Phonopy] %d %s" % (d[0], d[1:]))
    return phonon

def run(calc, phonon):
    supercells = phonon.get_supercells_with_displacements()
    # Force calculations by calculator
    set_of_forces = []
    for (i,scell) in enumerate(supercells):
        ##########
        at = Atoms(symbols=scell.get_chemical_symbols(),
                      scaled_positions=scell.get_scaled_positions(),
                      cell=scell.get_cell(),
                      pbc=True)

        at.set_calculator(calc)

        energy = at.get_potential_energy()
        forces = at.get_forces()
        stress = at.get_stress(voigt=False)

        drift_force = forces.sum(axis=0)
        print(("[Phonopy] Drift force:" + "%11.5f" * 3) % tuple(drift_force))
        # Simple translational invariance
        for force in forces:
            force -= drift_force / forces.shape[0]

        at.arrays["force"] = forces
        at.info["virial"] = -1.0 * at.get_volume() * stress
        at.info["energy"] = energy

        write("{}_scell.xyz".format(i), at)
        set_of_forces.append(forces)
    return set_of_forces

cell = get_crystal()
phonon = phonopy_pre_process(cell, supercell_matrix=np.eye(3, dtype='intc'))
set_of_forces = run(calc, phonon)
phonon.produce_force_constants(forces=set_of_forces)

path = [[[0, 0, 0], [-0.5, 0.5, 0.5], [0.25, 0.25, 0.25], [0, 0, 0], [0, 0.5, 0]]]
labels = ["$\\Gamma$", "H", "P", "$\\Gamma$", "N"]
qpoints, connections = get_band_qpoints_and_path_connections(path, npoints=51)
phonon.run_band_structure(qpoints, path_connections=connections, labels=labels)

phonon.write_yaml_band_structure(filename="{}.yaml".format(model_name))
