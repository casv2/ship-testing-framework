from ase import Atoms
import numpy as np
import os
import sys
from ase.io import read, write
import model

calc = model.calculator

al = read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "TiAl_trans_hex.xyz"), ":")

E = []

for at in al:
    at.set_calculator(calc)
    E.append(at.get_potential_energy())

properties = { "energy" : E }
