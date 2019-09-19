import matplotlib
matplotlib.use('PDF')
from matplotlib.pyplot import *

import json
import os
import itertools
import glob
from analyze_utils import *

(args, models, bulk_tests, default_analysis_settings) = analyze_start('dimer')

ref_linestyles=[ "-", "--" ]
other_linestyles=[ ":", "-." ]
struct_colors =  [ "black", "red", "blue", "orange", "green", "brown", "grey", "magenta","cyan" ]

cwd = os.getcwd()
element = cwd.split("/")[-2]

print element

r0 = { "Si" : 2.35, "Ti" : 2.89607, "W" : 2.74 }

print args, models, bulk_tests, default_analysis_settings

# for (i,model) in enumerate(models):
#     if model.startswith("CASTEP"):
#         del models[i]
##del models[2] #delete CASTEP

data = {}
struct_data = {}
for model_name in models:
    sys.stderr.write("reading data for model {}\n".format(model_name))
    data[model_name] = {}
    cur_model_data = {}
    for bulk_test_name in bulk_tests:
        sys.stderr.write("   reading data for test {}\n".format(bulk_test_name))

        prop_filename ="{}-model-{}-test-{}-properties.json".format(args.test_set, model_name, bulk_test_name)

        try:
            with open(prop_filename, "r") as model_data_file:
                json_data = json.load(model_data_file)
        except:
            sys.stderr.write("No properties file '{}'\n".format(prop_filename))
            continue

        cur_model_data[bulk_test_name] = json_data.copy()
        # print "got data for ",model_name, cur_model_data.keys()
        data[model_name] = cur_model_data.copy()

ref_model_name = default_analysis_settings["ref_model"]

n = 0
min_E = 0
axvline(x=r0[element], label="r0", color="grey") #Si
#axvline(x=2.74, label="r0", color="grey") #Si
for model_name in sorted(models):
    E = data[model_name]["dimer"]["dimer_energy"]
    if min(E) < min_E:
        min_E = min(E)
    R = data[model_name]["dimer"]["dimer_distance"]
    if model_name != ref_model_name:
        n+=1
        plot(R, E, linestyle=ref_linestyles[0], color=struct_colors[n], label=model_name)
    else:
        plot(R, E, linestyle=ref_linestyles[0], color=struct_colors[0], label=model_name)

    title(bulk_tests[0])
    xlabel(r"Dimer distance ($\AA$)")
    ylabel("Energy (eV)")
    #ylim([min_E*1.1, -min_E*1.5])
    ylim([-7.0,4.0])
    #xlim([2.0,5.0])
    legend()
    savefig("dimer_test.pdf", bbox_inches='tight')
