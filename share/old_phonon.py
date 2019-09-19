from ase.dft.kpoints import ibz_points, bandpath
from ase.phonons import Phonons

import model

#def phonon_calc(at, N, delta):
#	ph = Phonons(at, model.calculator, supercell=(N, N, N), delta=delta)
#	ph.run()
#	ph.read(acoustic=True)

def phonon_diamond(at, N, delta):
	ph = Phonons(at, model.calculator, supercell=(N, N, N), delta=delta)
	ph.run()
	ph.read(acoustic=True)

	points = ibz_points['cubic']
	G = points['Gamma']
	X = points['X']
	R = points['R']

	point_names = ['$\Gamma$', 'X', '$\Gamma$', 'R']
	path = [G, X, G, R]

	path_kc, q, Q = bandpath(path, at.cell, 100)
	omega_kn = 1000 * ph.band_structure(path_kc)

	return {"omega_kn" : omega_kn.tolist(), "point_names" : point_names, "path" : path, "Q" : list(Q), "q" : list(q) }


def phonon_bcc(at, N, delta):
	ph = Phonons(at, model.calculator, supercell=(N, N, N), delta=delta)
	ph.run()
	ph.read(acoustic=True)

	points = ibz_points['bcc']
	G = points['Gamma']
	H = points['H']
	P = points['P']
	N = points['N']

	point_names = ['$\Gamma$', 'H', 'P', '$\Gamma$', 'N']
	path = [G, H, P, G, N]

	path_kc, q, Q = bandpath(path, at.cell, 100)
	omega_kn = 1000 * ph.band_structure(path_kc)

	return {"omega_kn" : omega_kn.tolist(), "point_names" : point_names, "path" : path, "Q" : list(Q), "q" : list(q) }

def phonon_hcp(at, N, delta):
	ph = Phonons(at, model.calculator, supercell=(N, N, N), delta=delta)
	ph.run()
	ph.read(acoustic=True)

	points = ibz_points['hexagonal']
	G = points['Gamma']
	K = points['K']
	M = points['M']
	A = points['A']

	point_names = ['$\Gamma$', 'K', 'M', '$\Gamma$', 'A']
	path = [G, K, M, G, A]

	path_kc, q, Q = bandpath(path, at.cell, 100)
	omega_kn = 1000 * ph.band_structure(path_kc)

	return {"omega_kn" : omega_kn.tolist(), "point_names" : point_names, "path" : path, "Q" : list(Q), "q" : list(q) }

def phonon_fcc(at, N, delta):
	ph = Phonons(at, model.calculator, supercell=(N, N, N), delta=delta)
	ph.run()
	ph.read(acoustic=True)

	points = ibz_points['fcc']
	G = points['Gamma']
	K = points['K']
	U = points['U']
	X = points['X']
	L = points['L']

	point_names = ['$\Gamma$', 'X', 'U', 'L', '$\Gamma$', 'K']
	path = [G, X, U, L, G, K]

	path_kc, q, Q = bandpath(path, at.cell, 100)
	omega_kn = 1000 * ph.band_structure(path_kc)

	return {"omega_kn" : omega_kn.tolist(), "point_names" : point_names, "path" : path, "Q" : list(Q), "q" : list(q) }

def phonon_fcc(at, N, delta):
	ph = Phonons(at, model.calculator, supercell=(N, N, N), delta=delta)
	ph.run()
	ph.read(acoustic=True)

	points = ibz_points['fcc']
	G = points['Gamma']
	K = points['K']
	U = points['U']
	X = points['X']
	L = points['L']

	point_names = ['$\Gamma$', 'X', 'U', 'L', '$\Gamma$', 'K']
	path = [G, X, U, L, G, K]

	path_kc, q, Q = bandpath(path, at.cell, 100)
	omega_kn = 1000 * ph.band_structure(path_kc)

	return {"omega_kn" : omega_kn.tolist(), "point_names" : point_names, "path" : path, "Q" : list(Q), "q" : list(q) }



#	ph.clean()

#	path = bandpath('GXULGK', atoms.cell, 100)[0]
#	bs = ph.get_band_structure(path)

	#dos = ph.get_dos(kpts=(20, 20, 20)).sample_grid(npts=100, width=1e-3)
