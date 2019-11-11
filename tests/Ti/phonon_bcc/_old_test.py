import phonon
#from ase.lattice.cubic import BodyCenteredCubic
from ase.io import read
import os

model_dir = os.path.dirname(os.path.realpath(__file__))
#c_over_a = 1.588
#a0 = 2.8

#at = HexagonalClosedPacked(symbol='Ti', latticeconstant=(a0,a0*c_over_a)) 

at = read(model_dir + "/Ti-model-CASTEP_ASE-test-bulk_Ti_bcc-relaxed.xyz")

#a0 = 3.1

#at = read("Ti-model-CASTEP_ASE-test-bulk_Ti_bcc-relaxed.xyz")

properties = phonon.phonon_bcc(at, 3, 0.01)