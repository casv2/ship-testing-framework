import os
from distutils import spawn

#from matscipy.socketcalc import CastepClient, SocketCalculator
from ase.calculators.castep import Castep

model_abs_dir = os.path.abspath(os.path.dirname(__file__))

mpirun = "mpirun"
mpirun_args = "-n 16"
castep = "castep.mpi"

os.environ['CASTEP_COMMAND'] = '{0} {1} {2}'.format(mpirun, mpirun_args, castep)

print os.environ['CASTEP_COMMAND']

name = 'CASTEP'
Castep.name = name
Castep.todict = lambda self: {}

no_checkpoint = True

def start(test_name):
        global calculator
	calculator = Castep(directory="./_CASTEP",
						cut_off_energy=500, #700
                        max_scf_cycles=250,
                        calculate_stress=True,
                        finite_basis_corr='automatic',
                        smearing_width='0.1', #0.1
                        #elec_energy_tol='0.0000001',
                        #elec_energy_tol='0.0000001',
                        #elec_method='edft',
                        #nextra_bands='13',
                        mixing_scheme='Pulay',
                        kpoints_mp_spacing='0.04', #0.015
                        #perc_extra_bands=150,
                        write_checkpoint='none')

#                        cut_off_energy=600, #700
#                        max_scf_cycles=250,
#                        calculate_stress=True,
#                        finite_basis_corr='automatic',
#                        smearing_width='0.1', #0.1
#                        #elec_energy_tol='0.0000001',
#                        #elec_method='edft',
#                        #nextra_bands='13',
#                        mixing_scheme='Pulay',
#                        kpoints_mp_spacing='0.04', #0.015
#                        #perc_extra_bands=150,
#                        write_checkpoint='none')
