import matplotlib
matplotlib.use('PDF')
from matplotlib.pyplot import *

import json
import os
import itertools
import glob
from analyze_utils import *

(args, models, bulk_tests, default_analysis_settings) = analyze_start('layer_test')

ref_linestyles=[ "-", "--" ]
other_linestyles=[ ":", "-." ]
struct_colors = [ "black", "red", "blue", "orange", "green", "brown", "grey", "magenta","cyan" ]

print args, models, bulk_tests, default_analysis_settings

#models = models[1:]

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

print ref_model_name

n = 0
for model_name in sorted(models):
    if bool(data[model_name]["layer_test"]) == True:
        E = data[model_name]["layer_test"]["energy"]
        R = data[model_name]["layer_test"]["distance"]

        E = [ e - min(E) for e in E ]

        if model_name != ref_model_name:
            n+=1
            plot(R, E, color=struct_colors[n], label=model_name)
        else:
            plot(R, E, color=struct_colors[0], label=model_name)

title(bulk_tests[0])
xlabel(r"Interplanar spacing $(\AA)$")
ylabel("Energy (eV)")
ylim([0,5])
legend()
savefig("layer_test.pdf", bbox_inches='tight')
