from ase import Atoms
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#from quippy import Potential
import quippy
#import juliaimport
#import julip
import os
import sys
from ase.io import read, write
import subprocess
#sys.path.insert(0, './')
import time
import phonopy
from phonopy.phonon.band_structure import get_band_qpoints_and_path_connections

import model

calculator = model.calculator

cell = PhonopyAtoms(symbols=(['Ti'] * 2),
                    cell=np.diag((6.64, 6.64, 6.64)),
                    scaled_positions=[(0, 0, 0),
                                      (0.5, 0.5, 0.5)])

smat = [[4,0,0], [0,4,0], [0,0,4]]

phonon = Phonopy(cell,smat)

phonon.generate_displacements(distance=0.03)

supercells = phonon.get_supercells_with_displacements()

set_of_forces = []
for scell in supercells:
    at = Atoms(symbols=scell.get_chemical_symbols(),
                 scaled_positions=scell.get_scaled_positions(),
                 cell=scell.get_cell(),
                 pbc=True)
    at.set_calculator(calculator)
    energy = at.get_potential_energy()
    forces = at.get_forces()
    drift_force = forces.sum(axis=0)
    print(("[Phonopy] Drift force:" + "%11.5f" * 3) % tuple(drift_force))
    # Simple translational invariance
    for force in forces:
        force -= drift_force / forces.shape[0]
    set_of_forces.append(forces)

phonon.produce_force_constants(forces=set_of_forces)

phonon.run_mesh([20, 20, 20])
phonon.run_thermal_properties(t_step=10,
                              t_max=1000,
                              t_min=0)
tp_dict = phonon.get_thermal_properties_dict()
temperatures = tp_dict['temperatures']
free_energy = tp_dict['free_energy']
entropy = tp_dict['entropy']
heat_capacity = tp_dict['heat_capacity']

# print tp_dict.keys()
#
# for t, F, S, cv in zip(temperatures, free_energy, entropy, heat_capacity):
#     print(("%12.3f " + "%15.7f" * 3) % ( t, F, S, cv ))
#
# phonon.plot_thermal_properties().show()
#plt.savefig("bla.png")

properties = {'temperatures' : temperatures.tolist(), 'free_energy' : free_energy.tolist(), 'entropy' : entropy.tolist(), 'heat_capacity' : heat_capacity.tolist() }














#model_dir = os.path.dirname(__file__)

#### CALCULATOR ####

#calculator = Potential(init_args='Potential xml_label="GAP_2017_6_17_60_4_3_56_165"',
#              param_filename=os.path.join(model_dir,'gp_iter6_sparse9k.xml'))

#model_dir = os.path.dirname(os.path.realpath(__file__))
#IP = juliaimport.import_IP(model_dir + "/Si_5BBA_all_r.json")
#calculator = julip.JulipCalculator("IP")


# i = -3
# l = ""


# for a in np.linspace(3.26, 3.37, 6):
#     cell = PhonopyAtoms(symbols=(['Ti'] * 2),
#                     cell=np.diag((a, a, a)),
#                     scaled_positions=[(0, 0, 0),
#                                       (0.5, 0.5, 0.5)])
#
#
#     smat = [[4,0,0], [0,4,0], [0,0,4]]
#     #smat = np.eye(3, dtype='intc')
#
#     phonon = Phonopy(cell,
#                  smat)
#
#     phonon.generate_displacements(distance=0.03)
#
#     supercells = phonon.get_supercells_with_displacements()
#
#     set_of_forces = []
#     for scell in supercells:
#         cell = Atoms(symbols=scell.get_chemical_symbols(),
#                  scaled_positions=scell.get_scaled_positions(),
#                  cell=scell.get_cell(),
#                  pbc=True)
#     write("cell.xyz", cell)
#     qat = quippy.AtomsList("cell.xyz")[0]
#
#
#     qat.set_calculator(calculator)
#     energy = qat.get_potential_energy()
#     forces = qat.get_forces()
#     drift_force = forces.sum(axis=0)
#     print(("[Phonopy] Drift force:" + "%11.5f" * 3) % tuple(drift_force))
#     # Simple translational invariance
#     for force in forces:
#         force -= drift_force / forces.shape[0]
#     set_of_forces.append(forces)
#
#     phonon.produce_force_constants(forces=set_of_forces)
#
#     phonon.set_mesh([21, 21, 21])
#     phonon.run_thermal_properties(t_step=10,
#                           t_max=1000,
#                           t_min=0)
#
#     l += "{0}   {1}\n".format(str(round(a**3,6)), round(energy,6))
#     #phonon.plot_thermal_properties().show()
#     #plt.savefig("bla_{}.png".format(str(a)))
#
#     phonon.write_yaml_thermal_properties(filename='thermal_properties_{}.yaml'.format(str(i)))
#     i += 1
#
# print l
#
# text_file = open("e-v.dat", "w")
# text_file.write(l)
# text_file.close()
#
# time.sleep(1)
#
# os.system("phonopy-qha e-v.dat thermal_properties_{-{3..1},{0..2}}.yaml")
#
# properties = {}
#
# for file in ['gruneisen-temperature.dat', 'volume-temperature.dat',
#                 'dsdv-temperature.dat', 'Cp-temperature.dat',
#                 'bulk_modulus-temperature.dat', 'gibbs-temperature.dat',
#                 'thermal_expansion.dat', 'volume-temperature.dat']:
#     print file
#     if file in ["dsdv-temperature.dat", "Cp-temperature.dat", "gibbs-temperature.dat"]:
#         d = pd.read_csv(file, sep="   ", header=None)
#     else:
#         d = pd.read_csv(file, sep="       ", header=None)
#     A, B = np.array(d[0]).tolist(), np.array(d[1]).tolist()
#     properties[file.split(".")[0]] = [A,B]
