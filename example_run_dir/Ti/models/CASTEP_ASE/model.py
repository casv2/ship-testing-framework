import os
from distutils import spawn

#from matscipy.socketcalc import CastepClient, SocketCalculator
from ase.calculators.castep import Castep

model_abs_dir = os.path.abspath(os.path.dirname(__file__))

mpirun = "mpirun"
mpirun_args = "-n 32"
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
			cut_off_energy=600, #700
                        max_scf_cycles=250,
                        calculate_stress=True,
                        finite_basis_corr='automatic',
                        smearing_width='0.1',
                        #elec_method='edft',
                        mixing_scheme='Pulay',
                        kpoints_mp_spacing='0.02', #0.015
                        write_checkpoint='none')

