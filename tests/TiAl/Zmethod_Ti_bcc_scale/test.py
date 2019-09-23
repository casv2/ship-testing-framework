import model
import os
import subprocess
import sys
from ase.io import read, write
import zmethod
import matplotlib.pyplot as plt

calculator = model.calculator

at = read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bulk.xyz"))
big_at = at * (6,6,6)

def find_PTmelt(nsteps, R, P, T):
    points = [j*nsteps for j in xrange(R)]

    Tm_l, Pm_l = [], []

    for k in xrange(0, R - 1):
        Pm = np.mean(P[points[k]:points[k+1]])
        Tm = np.mean(T[points[k]:points[k+1]])
        Tm_l.append(Tm)
        Pm_l.append(Pm)

    Tmelt_mn = list(filter(lambda x: x < 0, np.diff(Tm_l)))[-1]
    Tmelt_est_index = np.diff(Tm_l).tolist().index(Tmelt_mn)
    Tmelt_est = Tm_l[Tmelt_est_index+1]
    Pmelt_est = Pm_l[Tmelt_est_index+1]

    return Pmelt_est, Tmelt_est

nsteps = 1000
R = 10
A = 0.2 #0.02, 1000, 100, 3500
T = 3500

D = {}

for i in xrange(3):
    big_at.set_cell(big_at.cell*1.02, scale_atoms=True)
    V = big_at.get_volume()
    Etot, Ekin, Epot, T, P = zmethod.Zmethod(calculator, big_at, nsteps=nsteps, dt=1, A=A, T=T, R=R, save_config=100, name="Ti_bcc")
    P = 160.21766208*np.array(P[1000:])
    T = np.array(T[1000:])
    plt.scatter(P, T, label="{}".format(i))
    plt.savefig("zmethod_{}.png".format(i))
    Pmelt_est, Tmelt_est = find_PTmelt(nsteps, R, P, T)
    D[i] = [Pmelt_est, Tmelt_est, V]

properties = D
