from ase import Atoms
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from quippy import Potential
import quippy
import os
import sys
from ase.io import read, write
import pickle

import phonopy
from phonopy.phonon.band_structure import get_band_qpoints_and_path_connections

import model

calc = model.calculator

def get_crystal():
    at = read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "Ti-model-CASTEP_ASE-test-bulk_Ti_bcc-relaxed.xyz"))

    #a = 3.32
    cell = PhonopyAtoms(symbols=(['Ti'] * 2),
                    cell=at.get_cell(),
                    positions=at.get_positions())


    #smat = [[2,0,0], [0,2,0], [0,0,2]]
    return cell

def phonopy_pre_process(cell, supercell_matrix=None):

    #if supercell_matrix is None:
    smat = [[2,0,0], [0,2,0], [0,0,2]]
    #else:
    #    smat = supercell_matrix

    phonon = Phonopy(cell,
                     smat)
                     #primitive_matrix=[[0, 0.5, 0.5],
                    #                   [0.5, 0, 0.5],
                    #                   [0.5, 0.5, 0]])
    phonon.generate_displacements(distance=0.01)
    print("[Phonopy] Atomic displacements:")
    disps = phonon.get_displacements()
    for d in disps:
        print("[Phonopy] %d %s" % (d[0], d[1:]))
    return phonon

def run(calc, phonon):
    supercells = phonon.get_supercells_with_displacements()
    # Force calculations by calculator
    set_of_forces = []
    for scell in supercells:
        ##########
        qat = Atoms(symbols=scell.get_chemical_symbols(),
                      scaled_positions=scell.get_scaled_positions(),
                      cell=scell.get_cell(),
                      pbc=True)
        ###########

        #qat = read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "phonopy_bcc_config.xyz"))

        #write("cell.xyz", cell)
        #qat = quippy.AtomsList("cell.xyz")[0]

        qat.set_calculator(calc)
        forces = qat.get_forces()
        drift_force = forces.sum(axis=0)
        print(("[Phonopy] Drift force:" + "%11.5f" * 3) % tuple(drift_force))
        # Simple translational invariance
        for force in forces:
            force -= drift_force / forces.shape[0]
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
#phonon.run_band_structure(qpoints, path_connections=connections, labels=labels)
phonon.plot_band_structure().show()
#plt.savefig
#phonon.set_mesh([21, 21, 21])
#phonon.set_total_DOS(tetrahedron_method=True)

#phonon.get_total_DOS()


#print model.name

try:
    model_name = model.orig_dir.split("/")[-1].split("-")[2]
except:
    model_name = model.pot_name.split("/")[-2]#.split("-")[2]

#print split(split(model.orig_dir, "/")[-1], "-")[2]
#print vars(model)
#print dict(model)

phonon.write_yaml_band_structure(filename="{}.yaml".format(model_name))


#fig, plt = phonon.plot_band_structure_2()

#plt.savefig("test.png")



#phonon.run_mesh([20, 20, 20])
#phonon.run_thermal_properties(t_step=10,
#                              t_max=1000,
#                              t_min=0)


#band_dict = phonon.get_band_structure_dict()

#print band_dict
#print band_dict.keys()


#phonon.plot_band_structure().show()


#pickle.dump(phonon, file('phonon2.pickle', 'w'))



#plt.savefig("band.png")

#properties = { 'band_dict' : band_dict, 'set_of_forces' : set_of_forces}
