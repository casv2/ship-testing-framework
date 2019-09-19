import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot as plt

import json
import os
import itertools
import glob
from analyze_utils import *

(args, models, bulk_tests, default_analysis_settings) = analyze_start('interstitial_pes_old')

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

print data


f, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,5))

n = 0
for model_name in sorted(models):
    if bool(data[model_name]["interstitial_pes_old"]) == True:
        E_x = data[model_name]["interstitial_pes_old"]["E_x"]
        E_xy = data[model_name]["interstitial_pes_old"]["E_xy"]

        E_x_shift = [ e - E_x[0] for e in E_x]
        E_xy_shift = [ e - E_xy[0] for e in E_xy]

        disp_list = data[model_name]["interstitial_pes_old"]["disp_list"]

        if model_name != ref_model_name:
            n+=1
            ax1.plot(disp_list, E_x_shift, color=struct_colors[n], label=model_name)
            ax2.plot(disp_list, E_xy_shift, color=struct_colors[n], label=model_name)
        else:
            ax1.plot(disp_list, E_x_shift, color=struct_colors[0], label=model_name)
            ax2.plot(disp_list, E_xy_shift, color=struct_colors[0], label=model_name)

plt.title("interstital_pes_unrelaxed")
ax1.set_xlabel(r"Displacement (x) $(\AA)$")
ax1.set_ylabel("Energy (eV)")
ax2.set_xlabel(r"Displacement (x=y) $(\AA)$")
ax2.set_ylabel("Energy (eV)")
#ax1.set_ylim((-0.025,6.0))
#ax2.set_ylim((-0.025,6.0))
ax1.set_ylim((-2.0,6.0))
ax2.set_ylim((-2.0,6.0))
plt.legend()
plt.savefig("interstitial_pes_old.pdf", bbox_inches='tight')
