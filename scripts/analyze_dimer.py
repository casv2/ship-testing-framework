import matplotlib
matplotlib.use('PDF')
from matplotlib.pyplot import *

import json
import os
import itertools
import glob
import numpy as np
from analyze_utils import *

(args, models, tests, default_analysis_settings) = analyze_start('dimer_*')

ref_linestyles=[ "-", "--" ]
other_linestyles=[ ":", "-." ]
struct_colors =  [ "black", "red", "blue", "orange", "green", "brown", "grey", "magenta","cyan" ]

cwd = os.getcwd()
element = cwd.split("/")[-2]

print element

r0 = { "Si" : 2.35, "Ti" : 2.89607, "W" : 2.74 }

print args, models, tests, default_analysis_settings

# for (i,model) in enumerate(models):
#     if model.startswith("CASTEP"):
#         del models[i]
##del models[2] #delete CASTEP
del models[0]
del models[0]

data = {}
struct_data = {}
for model_name in models:
    sys.stderr.write("reading data for model {}\n".format(model_name))
    data[model_name] = {}
    cur_model_data = {}
    for test_name in tests:
        sys.stderr.write("   reading data for test {}\n".format(test_name))

        prop_filename ="{}-model-{}-test-{}-properties.json".format(args.test_set, model_name, test_name)

        try:
            with open(prop_filename, "r") as model_data_file:
                json_data = json.load(model_data_file)
        except:
            sys.stderr.write("No properties file '{}'\n".format(prop_filename))
            continue

        cur_model_data[test_name] = json_data.copy()
        # print "got data for ",model_name, cur_model_data.keys()
        data[model_name] = cur_model_data.copy()

ref_model_name = default_analysis_settings["ref_model"]

n = 0
min_E = 0

print data

#models = ["SHIP_TiAl_v1"]

#axvline(x=r0[element], label="r0", color="grey") #Si
# axvline(x=2.89, label="r0 Ti", color="grey") #Si
# axvline(x=2.86, label="r0 Al", color="grey")
for test in tests:
    for model_name in sorted(models):
        E = data[model_name][test]["dimer_energy"]
        if min(E) < min_E:
            min_E = min(E)
        R = data[model_name][test]["dimer_distance"]
        if model_name != ref_model_name:
            n+=1
            plot(R, np.array(E) - E[-1], linestyle=ref_linestyles[0], color=struct_colors[n], label=model_name)
        else:
            plot(R, np.array(E) - E[-1], linestyle=ref_linestyles[0], color=struct_colors[0], label=model_name)

        title("Ti-Ti, Ti-Al, Al-Al dimers")
        xlabel(r"Dimer distance ($\AA$)")
        ylabel("Energy (eV)")
        #ylim([min_E*1.1, -min_E*1.5])
        ylim([-7.0,4.0])
        #xlim([2.0,5.0])
        legend()
        savefig("dimer_test.pdf", bbox_inches='tight')
