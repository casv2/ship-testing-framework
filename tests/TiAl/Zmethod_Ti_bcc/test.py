import model
import os
import subprocess
import sys
from ase.io import read, write
import zmethod

calculator = model.calculator

at = read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bulk.xyz"))
big_at = at * (5,5,5)

zmethod.Zmethod(calculator, big_at, nsteps=2000, dt=1, A=0.01, T=3500, R=50, save_config=1, name="Ti_bcc")
