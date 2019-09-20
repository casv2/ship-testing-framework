from ase import units
from ase.io.trajectory import Trajectory
from ase.md.velocitydistribution import (MaxwellBoltzmannDistribution,
                                         Stationary, ZeroRotation)
from ase.md.verlet import VelocityVerlet
import time
from ase.io import read, write
import numpy as np
import pandas as pd
import os

def Zmethod(calculator, atoms, nsteps, dt, A, T, R, save_config, name):

    atoms.set_calculator(calculator)

    #### WRITE FILE

    with open("{}_run.txt".format(name), "w") as myfile:
        myfile.write("Etot,Epot,Ekin,Temp,Pres\n")

    def _write_log(a=atoms):  # store a reference to atoms in the definition.
        """Function to print the potential, kinetic and total energy."""
        epot = a.get_potential_energy() / len(a)
        ekin = a.get_kinetic_energy() / len(a)
        pres = -np.trace(atoms.get_stress(voigt=False))/3
        print('Energy per atom: Epot = %.3feV  Ekin = %.3feV (T=%3.0fK)  '
              'Etot = %.3feV' % (epot, ekin, ekin / (1.5 * units.kB), epot + ekin))
        with open("{}_run.txt".format(name), "a") as myfile:
            myfile.write("{}, {}, {}, {}, {}\n".format(epot+ekin, epot, ekin, ekin / (1.5 * units.kB), pres))

    MaxwellBoltzmannDistribution(atoms, T * units.kB)
    Stationary(atoms)
    ZeroRotation(atoms)

    #try:
    t1 = time.time()
    for i in xrange(R):
        dyn = VelocityVerlet(atoms, dt * units.fs)
        traj = Trajectory('{}_run.traj'.format(name), 'a', atoms)
        dyn.attach(traj.write, interval=save_config)
        dyn.attach(_write_log, interval=1)
        dyn.run(nsteps)

        m = atoms.get_masses()[0]
        v = atoms.arrays["momenta"] / m
        C = A / np.linalg.norm(v)

        atoms.set_momenta( (v + C*v) * m )

    t2 = time.time()

    print "Elapsed Zmethod TIME [s]: ", t2-t1

    traj = Trajectory('{}_run.traj'.format(name))
    write('{}_run.xyz'.format(name), traj)
    os.system("rm {}_run.traj".format(name))

    D = pd.read_csv("{}_run.txt".format(name))

    T = D["Temp"].tolist()
    P = D["Pres"].tolist()
    Etot = D["Etot"].tolist()
    Ekin = D["Ekin"].tolist()
    Epot = D["Epot"].tolist()

    # except:
    #     print "CRASHH!!!", name
    #
    #     traj = Trajectory('{}_run.traj'.format(name))
    #     #write("./MD_run.xyz", traj)
    #     log = pd.read_csv("./{}_run.txt".format(name))
    #
    #     Etot = np.array(log["Etot"].tolist())
    #     Edif = np.diff(Etot)
    #     index = [i for i, x in enumerate(Edif) if x > 1.0]
    #     mnindex = np.amin(index)
    #
    #     write("{}_crash.xyz".format(name), traj[mnindex])

    return Etot, Ekin, Epot, T, P
