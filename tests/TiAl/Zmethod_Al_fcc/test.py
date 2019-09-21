import model
import os
import subprocess
import sys
from ase.io import read, write
import zmethod

calculator = model.calculator

at = read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bulk.xyz"))
big_at = at * (8,8,8)

Etot, Ekin, Epot, T, P = zmethod.Zmethod(calculator, big_at, nsteps=2000, dt=1, A=0.01, T=1500, R=50, save_config=100, name="Al_fcc")

properties = { 'E_tot' : Etot, 'E_kin' : Ekin, 'E_pot' : Epot, 'T' : T, 'P' : P }
