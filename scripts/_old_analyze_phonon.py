import matplotlib
matplotlib.use('PDF')
#from matplotlib.pyplot import *
import matplotlib.pyplot as plt
import numpy as np

import json
import os
import itertools
import glob
import time
import subprocess
from analyze_utils import *

(args, models, bulk_tests, default_analysis_settings) = analyze_start('phonon_hcp2')

ref_linestyles=[ "-", "--" ]
other_linestyles=[ ":", "-." ]
struct_colors = [ "black", "red", "blue", "cyan", "orange", "magenta", "green", "grey", "brown" ]

print args, models, bulk_tests, default_analysis_settings

bulk_tests = ['phonon_hcp2']

### READ DATA

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
#print data.keys()

phonon_types = data[ref_model_name].keys()
#phonon_types = ["phonon_hcp"]

print ref_model_name

###PLOT PHONON

def phonon_plot(model_name, phonon_type, i, ref_model_name):
    omega_kn = np.array(data[model_name][phonon_type]["omega_kn"])
    point_names = data[model_name][phonon_type]["point_names"]
    path = data[model_name][phonon_type]["path"]
    Q = data[model_name][phonon_type]["Q"]
    q = data[model_name][phonon_type]["q"]
    if model_name != ref_model_name:
        i += 1
    for n in range(len(omega_kn[0])):
        omega_n = omega_kn[:, n]
        if model_name != ref_model_name:
            plt.plot(q, omega_n, color=struct_colors[i], label=model_name, linestyle=other_linestyles[0]) #if n == 0 else ""
        if model_name == ref_model_name:
            plt.plot(q, omega_n, color=struct_colors[0], label=model_name, linestyle=ref_linestyles[0])
    plt.xticks(Q, point_names)
    plt.xlim(q[0], q[-1])
    plt.grid('on')
    plt.title(phonon_type)
    #plt.legend()
    return i

#os.system("rm phonon_*.pdf")

#time.sleep(1)

print "blaaaaa"

#print data[ref_model_name]
#print data
#print ref_model_name

print phonon_types

for phonon_type in phonon_types:
    i = 0
    print i
    plt.figure()
    for model in sorted(models):
        print model, phonon_type
        #try:
        i = phonon_plot(model, phonon_type, i, ref_model_name)
        #except:
        #    pass
        plt.savefig("{}.pdf".format(phonon_type))

#os.system("convert -density 350 phonon_*.pdf -quality 100 phonon_analysis.pdf")
#time.sleep(1)

#r_str = ["rm"]
#for phonon_type in phonon_types:
#    r_str.append(phonon_type + ".pdf")
#    subprocess.call(r_str)
