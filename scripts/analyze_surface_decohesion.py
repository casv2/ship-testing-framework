import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot as plt

import json
import ase.io
from ase.data import chemical_symbols
from analyze_utils import *
import math
import re
import time
import subprocess
import os


# from matplotlib import rc
# rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
# ## for Palatino and other serif fonts use:
# #rc('font',**{'family':'serif','serif':['Palatino']})
# rc('text', usetex=True)

(args, models, tests, default_analysis_settings) = analyze_start('surface_decohesion_*')

#tests = ['surface_decohesion_W_bcc_100']#, 'surface_decohesion_Si_diamond_111']

ref_linestyles=[ "-", "--" ]
other_linestyles=[ ":", "-." ]
struct_colors = [ "black", "red", "blue", "orange", "green", "brown", "grey", "magenta","cyan" ]

ref_model_name = default_analysis_settings["ref_model"]

data = read_properties(models, tests, args.test_set)

print data.keys()

for test in tests:
	ref_opening = data[ref_model_name][test]['surface_decohesion_unrelaxed_opening']
	ref_energy = data[ref_model_name][test]['surface_decohesion_unrelaxed_energy']
	ref_stress = data[ref_model_name][test]['surface_decohesion_unrelaxed_stress']

	#f, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,5))
	f, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,5))

	ax1.plot(ref_opening, ref_energy, label=ref_model_name, linestyle=ref_linestyles[0], color="black")
	ax1.set_xlabel("Unrelaxed opening ($\AA$)")
	ax1.set_ylabel("Energy (eV)")
	ax2.plot(ref_opening, ref_stress, label=ref_model_name, linestyle=ref_linestyles[0], color="black")
	ax2.set_xlabel("Unrelaxed opening ($\AA$)")
	ax2.set_ylabel(r"Stress (eV/$\AA$)")

	i = 0
	for model in sorted(data.keys()):
		if bool(data[model]) is True and model != ref_model_name:
			i += 1
			ax1.plot(data[model][test]['surface_decohesion_unrelaxed_opening'], data[model][test]['surface_decohesion_unrelaxed_energy'], label=model, color=struct_colors[i])#, linestyle=other_linestyles[0])
			ax2.plot(data[model][test]['surface_decohesion_unrelaxed_opening'], data[model][test]['surface_decohesion_unrelaxed_stress'], label=model, color=struct_colors[i])#, linestyle=other_linestyles[0])

	plt.title(test)
	plt.legend()
	plt.savefig("_{}.png".format(test), bbox_inches='tight') ####
	#for model in models:
	#if model != ref_model_name:

os.system("pdfjoin --paper a4paper --rotateoversize false _surface_decohesion_* -o surface_decohesion_analysis.pdf")

time.sleep(1)
os.system("rm _surface_decohesion_*.pdf")
