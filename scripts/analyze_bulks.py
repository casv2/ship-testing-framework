#!/usr/bin/env python

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

(args, models, bulk_tests, default_analysis_settings) = analyze_start('bulk_*')

#models = models + ["CASTEP_ASE"] ############################

bulk_tests = ["bulk_Ti_bcc", "bulk_Ti_hcp"]#, "bulk_TiAl"]#, "bulk_Ti3Al", "bulk_TiAl3"]

ref_linestyles=[ "-", "--" ]
other_linestyles=[ ":", ":" ]
struct_colors = [ "black", "red", "blue", "orange", "green", "brown", "grey", "magenta","cyan" ]

print models

#del models[1]

element_ref_struct_data = get_element_ref_structs(args.test_set, models, default_analysis_settings["element_ref_struct"])

# read and parse all data
data = {}
struct_data = {}
for model_name in models:
    sys.stderr.write("reading data for model {}\n".format(model_name))
    data[model_name] = {}
    cur_model_data = {}
    for bulk_test_name in bulk_tests:
        sys.stderr.write("   reading data for test {}\n".format(bulk_test_name))

        # read bulk test structure
        struct_filename = "{}-model-{}-test-{}-relaxed.xyz".format(args.test_set, model_name, bulk_test_name)
        try:
            struct = ase.io.read(struct_filename, format="extxyz")
        except:
            sys.stderr.write("No struct file '{}'\n".format(struct_filename))
            continue

        # read bulk test properties
        prop_filename ="{}-model-{}-test-{}-properties.json".format(args.test_set, model_name, bulk_test_name)
        try:
            with open(prop_filename, "r") as model_data_file:
                json_data = json.load(model_data_file)
        except:
            sys.stderr.write("No properties file '{}'\n".format(prop_filename))
            continue

        cur_model_data[bulk_test_name] = json_data.copy()

        # parse elements present
        elements_present = {}
        for Z in set(struct.get_atomic_numbers()):
            elements_present[Z] = sum(struct.get_atomic_numbers() == Z)

        # shift energy by minimum energies of reference element structures
        E0 = 0.0
        for Z in elements_present:
            symb = chemical_symbols[Z]
            print "looking for min E ",symb,model_name
            try:
                E = element_ref_struct_data[symb]["min_Es"][model_name]
                E0 += sum(struct.get_atomic_numbers() == Z)*E
            except:
                pass
        E0 /= len(struct)

        # shift E_vs_V
        E_vs_V_orig = cur_model_data[bulk_test_name]["E_vs_V"]

        ### MODIF

        cur_model_data[bulk_test_name]["E_vs_V"] = [ [ EV[0], EV[1]] for EV in E_vs_V_orig ]

        if not bulk_test_name in struct_data:
            struct_data[bulk_test_name] = {}
        struct_data[bulk_test_name]["formula_unit"] = formula_unit(struct.get_atomic_numbers())

    # print "got data for ",model_name, cur_model_data.keys()
    data[model_name] = cur_model_data.copy()

ref_model_name = default_analysis_settings["ref_model"]
n_fig = 1
elastic_const_tables = {}

sorted_consts_dict = {}
sorted_consts_tex_dict = {}

n = 0
for model_name in sorted(models):
    if model_name != ref_model_name:
        n += 1
    figure_nums = {}
    bulk_inds = {}
    for bulk_test_name in bulk_tests:
        try:
            min_EV  = min(data[model_name][bulk_test_name]["E_vs_V"], key = lambda x : x[1])
        except:
            print "no data for",model_name,bulk_test_name
        continue
        print "BULK_E_V_MIN",model_name,bulk_test_name, min_EV[0], min_EV[1]

    for bulk_test_name in bulk_tests:
        if bulk_test_name not in data[model_name]:
            sys.stderr.write("skipping struct {} in plotting model {}\n".format(bulk_test_name, model_name))
            continue

        E0 =  min([x[1] for x in data[model_name][bulk_test_name]["E_vs_V"]])
        #l = [x[1] for x in data[model_name][bulk_test_name]["E_vs_V"]]
        #print l

        if model_name != ref_model_name:
            plt.plot( [x[0] for x in data[model_name][bulk_test_name]["E_vs_V"]], [x[1] - E0 for x in data[model_name][bulk_test_name]["E_vs_V"]], other_linestyles[0], color=struct_colors[n], marker="o", markersize="2.5", label=model_name)
        if model_name == ref_model_name:
            print bulk_test_name
            plt.plot( [x[0] for x in data[ref_model_name][bulk_test_name]["E_vs_V"]], [x[1] - E0 for x in data[ref_model_name][bulk_test_name]["E_vs_V"]], ref_linestyles[0], color="black", label=model_name)

        sorted_consts = sorted([k for k in data[model_name][bulk_test_name].keys() if (re.match("^c[0-9][0-9]$",k) or k == 'B') ])

        sorted_consts_tex = []

        for const in sorted_consts:
            if const.startswith("B"):
                sorted_consts_tex.append(const)
            if const.startswith("c"):
                const = "$" + const[0] + "_{" + const[1:] + "}$"
                sorted_consts_tex.append(const)

        sorted_consts_dict[bulk_test_name] = sorted_consts
        sorted_consts_tex_dict[bulk_test_name] = sorted_consts_tex

#FIND REFERENCE VALUES

#print data

ref_bulk_dict = {}

for bulk_test_name in bulk_tests:
    ref_dict = {}
    try:
        for model in models:
            if model == ref_model_name:
                for key in data[model][bulk_test_name]:
                    if type(data[model][bulk_test_name][key]) == float:
                        ref_dict[key] = data[model][bulk_test_name][key]
        ref_bulk_dict[bulk_test_name] = ref_dict
    except:
        pass

#print ref_bulk_dict

#CALCULATE PCT DIFFERENCE WITH OTHER MODELS
#bulk_tests = bulk_tests[0] ###############################
#print bulk_tests

print bulk_tests

for bulk_test_name in bulk_tests:
    print "   ,", bulk_test_name
    #bulk_test_name = bulk_tests[0]
    for model in models:
        if model != ref_model_name:
            for key in data[model][bulk_test_name]:
                print data[model]["bulk_Ti_bcc"]["c44"]
                if type(data[model][bulk_test_name][key]) == float:
                    print bulk_test_name
                    pct_diff = int(((data[model][bulk_test_name][key] - ref_bulk_dict[bulk_test_name][key])/ref_bulk_dict[bulk_test_name][key])*100)
                    data[model][bulk_test_name][key] = str(pct_diff) + "\%"
#print data

filename = 'out.tex'

template = r'''
\documentclass[preview]{standalone}
\usepackage[paperwidth=8in,paperheight=4in,margin=0.5in,showframe]{geometry}
\usepackage{booktabs}
\begin{document}
\begin{center}
\textnormal{Elastic Constants} \\
\vspace{2mm}
%(x)s
\end{center}
\end{document}
'''

tables = ""

for bulk_test_name in bulk_tests:
    #bulk_test_name = bulk_tests[0]
    print bulk_test_name
    #table = "\\textnormal{Elastic Constants} \\"
    #table += "\\vspace{2mm}"
    table = "\\begin{tabular}{ l l " + " ".join(["c"]*len(sorted_consts_dict[bulk_test_name]))+" } \\toprule \n"
    table += "Model & Struct & " + " & ".join(sorted_consts_tex_dict[bulk_test_name]) + "\\\ \midrule \n"

    table += ref_model_name.replace("_","\\_")+" & " +bulk_test_name.replace("bulk_","").replace("_"," ") + " & " + " & ".join(["{0:.1f}".format(data[ref_model_name][bulk_test_name][k]) for k in sorted_consts_dict[bulk_test_name]]) + "\\\\ \n"

    for model in sorted(models):
        if model != ref_model_name:
            #print model
            table += model.replace("_","\\_")+" & " +bulk_test_name.replace("bulk_","").replace("_"," ") + " & " + " & ".join(["{}".format(data[model][bulk_test_name][k]) for k in sorted_consts_dict[bulk_test_name]]) + "\\\\ \n"

    table += "\\end{tabular} \\bigskip "
    tables += table
    print table
    #pdf_table(table, bulk_test_name)

with open(filename, 'wb') as f:
    f.write(template % {'x' : tables })

subprocess.call(['pdflatex', filename])
os.rename("out.pdf", "elastic_const_table.pdf")

print bulk_tests

plt.title("/".join(bulk_tests))
plt.legend(loc="center left", bbox_to_anchor=[1, 0.5])
#plt.legend()
plt.xlabel("V ($A^3$/atom)")
plt.ylabel("E (eV/atom)")
#plt.ylim(-1593.8, -1593)
plt.savefig("bulk_plot.pdf", bbox_inches='tight')

#os.system("convert -density 350 *_plot.pdf *_table.pdf -quality 100 bulk_analysis.pdf")
os.system("pdfjoin *_plot.pdf elastic_const_table.pdf")
time.sleep(1)
os.system("mv *-joined.pdf bulk_analysis.pdf")
