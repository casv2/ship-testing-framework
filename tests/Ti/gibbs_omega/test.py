from ase import Atoms
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
import numpy as np
import matplotlib.pyplot as plt
from quippy import Potential
import quippy
import os
import sys
from ase.io import read, write
import pickle
from ase.io import Trajectory
from quippy import GPA
from copy import deepcopy

import phonopy
from phonopy.phonon.band_structure import get_band_qpoints_and_path_connections

from ase.constraints import UnitCellFilter
from ase.optimize.precon import PreconLBFGS

import yaml
from yaml import CLoader as Loader
import numpy as np
from phonopy import PhonopyQHA

import model

def free_energy_calc(at, i, save_yaml):

    cell = PhonopyAtoms(symbols=at.get_chemical_symbols(),
                        cell=at.get_cell(),
                        positions=at.get_positions())

    smat = [[2,0,0], [0,2,0], [0,0,2]]

    phonon = Phonopy(cell,smat)

    phonon.generate_displacements(distance=0.01)

    supercells = phonon.get_supercells_with_displacements()

    set_of_forces = []
    for scell in supercells:
        at = Atoms(symbols=scell.get_chemical_symbols(),
                     scaled_positions=scell.get_scaled_positions(),
                     cell=scell.get_cell(),
                     pbc=True)
        at.set_calculator(model.calculator)
        energy = at.get_potential_energy()
        forces = at.get_forces()
        drift_force = forces.sum(axis=0)
        #print(("[Phonopy] Drift force:" + "%11.5f" * 3) % tuple(drift_force))
        # Simple translational invariance
        for force in forces:
            force -= drift_force / forces.shape[0]
        set_of_forces.append(forces)

    phonon.produce_force_constants(forces=set_of_forces)

    phonon.run_mesh([41, 41, 41])
    phonon.run_thermal_properties(t_step=10,
                                  t_max=700,
                                  t_min=0)
    tp_dict = phonon.get_thermal_properties_dict()
    temperatures = tp_dict['temperatures']
    free_energy = tp_dict['free_energy']
    entropy = tp_dict['entropy']
    heat_capacity = tp_dict['heat_capacity']

    if save_yaml==True:
        phonon.write_yaml_thermal_properties(filename='thermal_properties_{}.yaml'.format(str(i)))
    else:
        return free_energy, entropy, heat_capacity, temperatures


def gibbs_temp(at):
   E = []
   V = []

   for (i,scale) in enumerate(np.linspace(0.98, 1.02, 8)):
      at_scale = at.copy()
      at_scale.set_cell(at_scale.cell * scale, scale_atoms=True)
      at_scale = relax_config_pres(at_scale, 0.0, True)
      at_scale.set_calculator(model.calculator)
      e = at_scale.get_potential_energy()
      v = at_scale.get_volume()

      free_energy_calc(at_scale,i, save_yaml=True)

      E.append(e)
      V.append(v)

   print V


   entropy = []
   cv = []
   fe = []
   for index in range(0,8):
       filename = "thermal_properties_{}.yaml".format(str(index))
       #print("Reading %s" % filename)
       thermal_properties = yaml.load(open(filename),
                                     Loader=Loader)['thermal_properties']
       temperatures = [v['temperature'] for v in thermal_properties]
       cv.append([v['heat_capacity'] for v in thermal_properties])
       entropy.append([v['entropy'] for v in thermal_properties])
       fe.append([v['free_energy'] for v in thermal_properties])

   qha = PhonopyQHA(V,
                    E,
                    temperatures=temperatures,
                    free_energy=np.transpose(fe),
                    cv=np.transpose(cv),

                    entropy=np.transpose(entropy),
                    t_max=700)
   qha.plot_qha().show()
   plt.savefig("QHA.png")

   return temperatures, qha.get_gibbs_temperature()

def relax_config_pres(at, pres, constant_volume):
    at.set_calculator(model.calculator)
    ucf = UnitCellFilter(at, scalar_pressure=pres / GPA, constant_volume=constant_volume)
    qn = PreconLBFGS(ucf)
    qn.run(fmax=0.01)

    print "energy per at ", at.get_potential_energy()/len(at), " volume ", at.get_volume()/len(at)

    return at

#at = read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "Ti-model-CASTEP_ASE-test-bulk_Ti_omega-relaxed.xyz"))
#at_p = relax_config_pres(at, 0.0, False) #false means no constant volume

def create_omega_custom(c_vs_a, V_per_at, z):
   import quippy

   V = 3.0 * V_per_at
   a = (2 * V / (3.0**(0.5) * c_vs_a))**(1.0/3.0)
   c = c_vs_a * a

   lattice = []
   lattice.append([3.0**(0.5) /2.0 * a,-a/2.0,0])
   lattice.append([3.0**(0.5) /2.0 * a, a/2.0,0])
   lattice.append([0,0,c])
   lattice = np.transpose(lattice)
   unitcell = quippy.Atoms(n=0, lattice=lattice)

   pos = []
   pos.append([3.0**(0.5) /6.0 * a,0,0.0])
   pos.append([3.0**(0.5) /2.0 * a,0,c/2.0])
   pos.append([3.0**(0.5) * 5.0/6.0 * a,0,c/2.0])

   for i in range(0,len(pos)):
      unitcell.add_atoms(pos[i],z)

   return unitcell

at_omega = create_omega_custom(0.6, 17, 22)
at_omega_p = relax_config_pres(at_omega, 0.0, False)

temperatures, gibbs_omega = gibbs_temp(at_omega_p)

properties = { 'temperatures' : temperatures, 'gibbs_omega' : (gibbs_omega/len(at)).tolist() }
