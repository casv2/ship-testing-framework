import old_phonon
from ase.lattice.cubic import BodyCenteredCubic
import os
from ase.io import read, write

at = read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "Ti-model-CASTEP_ASE-test-bulk_Ti_bcc-relaxed.xyz"))

properties = phonon.phonon_bcc(at, 2, 0.01)
