import os.path
from ase.io import read, write

import model

al = read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "Ti_bcc_layer_test.xyz"), ":")

disp = al[1].positions[1][2] - al[0].positions[1][2]

E, R = [], []

i = 0
for at in al:
	at.set_calculator(model.calculator)
	e = at.get_potential_energy()

	i += 1
	r = disp*i

	E.append(e)
	R.append(r)

properties = { 'energy' : E, 'distance' : R }