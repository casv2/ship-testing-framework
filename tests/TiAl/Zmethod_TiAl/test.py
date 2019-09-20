import model
import os
import subprocess
import sys
from ase.io import read, write
import zmethod

calculator = model.calculator

at = read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bulk.xyz"))
big_at = at * (6,6,6)

Etot, Ekin, Epot, T, P = zmethod.Zmethod(calculator, big_at, nsteps=1000, dt=1, A=0.01, T=2800, R=20, save_config=50, name="TiAl")

properties = { 'E_tot' : Etot, 'E_kin' : Ekin, 'E_pot' : Epot, 'T' : T, 'P' : P }
