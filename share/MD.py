from ase.lattice.cubic import BodyCenteredCubic
from ase.md.langevin import Langevin
from ase import units
from ase.md.velocitydistribution import (MaxwellBoltzmannDistribution,
                                         Stationary, ZeroRotation)
import model
import numpy as np
from ase.io.trajectory import Trajectory
import sys
import time

class ListStream:
    def __init__(self):
        self.data = []
    def write(self, s):
        self.data.append(s)

sys.stdout = x = ListStream()

def MD_run(at, N, Tmin, Tmax, dt, ramps, MDsteps):
    start = time.time()

    at *= (N,N,N)
    at.set_calculator(model.calculator)
    MaxwellBoltzmannDistribution(at, Tmin * units.kB) ###is this allowed?
    Stationary(at)  # zero linear momentum
    ZeroRotation(at)

    def printenergy(a=at):
        #epot = a.get_potential_energy() / len(a)
        ekin = a.get_kinetic_energy() / len(a)
        print(ekin)

    traj = Trajectory('MDtraj.traj', 'w', at, properties=["energy", "forces"])

    for temp in np.linspace(Tmin,Tmax,ramps):
        dyn = Langevin(at, dt*units.fs, units.kB * temp, 0.002)
        dyn.attach(traj.write, interval=10)
        dyn.attach(printenergy, interval=1)
        dyn.run(MDsteps)

    sys.stdout = sys.__stdout__

    E = x.data

    end = time.time()

    return {"E" : E[::2], "t" : end-start} 