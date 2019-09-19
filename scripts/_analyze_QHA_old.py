import matplotlib
matplotlib.use('PDF')
from matplotlib.pyplot import *
rc('text', usetex=True)
rc('font', family='serif')

import json
import os
import itertools
import glob
from analyze_utils import *

(args, models, bulk_tests, default_analysis_settings) = analyze_start('QHA')

ref_linestyles=[ "-", "--" ]
other_linestyles=[ ":", "-." ]
struct_colors = [ "black", "red", "blue", "cyan", "orange", "magenta", "green", "grey", "brown" ]

print args, models, bulk_tests, default_analysis_settings

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

#subplots(3,3)

figure(figsize=(18,18))
f=15

j  = 0



for (i,test) in enumerate(data[data.keys()[0]]['QHA']):
    print test
    subplot(3, 3, i+1)
    for pot in data.keys():
        d = data[pot]["QHA"][test]
        if pot == ref_model_name:
            plot(d[0], d[1], ref_linestyles[0], color="black", label=pot.replace("_", "\_"),)
        else:
            plot(d[0], d[1], other_linestyles[0], marker="o", markersize="2.5", label=pot.replace("_", "\_"))
    if test == "volume-temperature":
        ylabel(r"Volume ($\AA^{3}$)", fontsize=f)
        xlabel("Temperature (K)", fontsize=f)
    if test == "thermal_expansion":
        xlabel("Temperature (K)", fontsize=f)
        ylabel(r"Thermal Expansion ($K^{-1}$)", fontsize=f)
    if test == "Cp-temperature":
        ylabel("Cp (J/mol * K)", fontsize=f)
        xlabel("Temperature (K)", fontsize=f)
    if test == "gibbs-temperature":
        xlabel("Temperature (K)", fontsize=f)
        ylabel("Gibbs free energy (eV)", fontsize=f)
    if test == "gruneisen-temperature":
        xlabel("Temperature (K)", fontsize=f)
        ylabel("Gruneisen parameter", fontsize=f)
    if test == "bulk_modulus-temperature":
        xlabel("Temperature (K)", fontsize=f)
        ylabel("Bulk modulus (GPa)", fontsize=f)
    if test == "dsdv-temperature":
        xlabel("Temperature", fontsize=f)
        ylabel(r"$\frac{\delta S}{\delta V}$", fontsize=f)
    title(test.replace("-", " ").replace("_", " "), fontsize=f)
    legend()

#savefig("all.pdf".format(test))
savefig("QHA.pdf")
