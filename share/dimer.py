from ase import Atoms
import numpy as np

import model

def get_e0(element):
	at = Atoms(element, cell=[[20,0,0],[0,20,0],[0,0,20]])
	at.set_calculator(model.calculator)
	return at.get_potential_energy()

def dimer(element1, element2, start, end, step):
	at = Atoms(element1+element2, positions=[[0, 0, 0],
		[0, 0, 1.5]], cell=[[20,0,0],[0,20,0],[0,0,20]])

	at.set_calculator(model.calculator)

	p = at.get_positions()
	e0 = get_e0(element1) + get_e0(element2) 

	E, R = [], []

	for r in np.arange(start, end, step):
		p[1,2] = r
		at.set_positions(p)
		E.append(at.get_potential_energy() - (e0))
		R.append(r)

	return { "dimer_distance" : R, "dimer_energy" : E }
