from ase.io import read, write
from copy import deepcopy
import numpy as np

import model

at_b = read("/Users/Cas/gits/temp/testing-framework/tests/Ti/pes/Ti-model-CASTEP_ASE-test-bulk_Ti_bcc-relaxed.xyz")
at_h = read("/Users/Cas/gits/temp/testing-framework/tests/Ti/pes/Ti-model-CASTEP_ASE-test-bulk_Ti_hcp-relaxed.xyz")

#at_b.set_calculator(model.calculator)
#e0 = at_b.get_potential_energy()

points = 20
E_data = np.zeros((points,points))

for (i, scale) in enumerate(np.linspace(0.8, 1.2, points)):
    for (j, disp) in enumerate(np.linspace(-0.8, 0.8, points)):
        at = deepcopy(at_b)
        at.positions[0] = at.positions[0] + [disp, disp, disp]
        at.set_cell(at.cell*scale)
        print at.positions
        at.set_calculator(model.calculator)
        E = at.get_potential_energy()
        E_data[j,i] = E #- e0

E_data_shift = E_data - np.min(E_data)
scales = [i for i in np.linspace(0.8, 1.2, points)]
disps = [i for i in np.linspace(-0.8, 0.8, points)]

properties = { "E_data_shift" : E_data_shift.tolist(), "scales" : scales, "disps" : disps }

#np.min(np.array([[2,2],[2,2]]))

# def f(x, y):
#     return np.sin(np.sqrt(x ** 2 + y ** 2))
#
# x = np.linspace(-6, 6, 30)
# y = np.linspace(-6, 6, 30)
#
# X, Y = np.meshgrid(x, y)
# Z = f(X, Y)
#
# R = np.random.rand(10,10).tolist()
#
# from mpl_toolkits.mplot3d import Axes3D
# import matplotlib.pyplot as plt
#
# fig = plt.figure()
# ax = plt.axes(projection='3d')
#vi
# scales = np.array([i for i in np.linspace(0.8, 1.2, points)])
# disps = np.array([i for i in np.linspace(-0.5, 0.5, points)])
#
# SC, DS = np.meshgrid(scales, disps)
#
# ax = plt.axes(projection='3d')
# ax.scatter3D(SC, DS, R)
#
# #ax.contour3D(SC, DS, R,50, color="red")
# plt.savefig("plot.png")
