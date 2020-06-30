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
	calculator = Castep()

	calculator._directory="./_CASTEP"

	calculator.param.cut_off_energy=700
	calculator.param.elec_energy_tol=1E-7
	calculator.param.elec_force_tol=1E-3
	calculator.param.spin_polarised=False
	calculator.param.mixing_scheme='Pulay'
	calculator.param.write_checkpoint='none'
	calculator.param.fine_grid_scale=2
	calculator.param.smearing_width=0.1
	calculator.param.finite_basis_corr='automatic'
	calculator.param.calculate_stress=True

	calculator.cell.kpoints_mp_spacing=0.02

	return calculator
