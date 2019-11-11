import os.path
from ase.io import read, write

import model

at = read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "phonopy_hcp_config.xyz"))

at.set_calculator(model.calculator)
e = at.get_potential_energy()
f = at.get_forces()
s = at.get_stress()

at.info["energy"] = e
at.arrays["force"] = f
at.info["virial"] = s

write("evaluated_phonopy_config.xyz", at)

properties = { 'energy' : e}
