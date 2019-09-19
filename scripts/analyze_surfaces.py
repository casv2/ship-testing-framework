#!/usr/bin/env python

import subprocess
from analyze_utils import *
import numpy as np

(args, models, tests, default_analysis_settings) = analyze_start('surface_*')

try:
    (mcc_compositions, mcc_energies) = get_multicomponent_constraints(args.test_set, models, default_analysis_settings["multicomponent_constraints"])
except:
    (mcc_compositions, mcc_energies) = (None, None)

# print "multicomponent_constraints_data ", multicomponent_constraints_data

from multicomponent_mu_range import mu_range

# read and parse all data
data = read_properties(models, tests, args.test_set)

def pdf_table(table):
    filename = 'out.tex'

    template = r'''
    \documentclass[preview]{standalone}
    \usepackage{booktabs}
    \begin{document}
    \begin{center}
    \textnormal{Surface Energy} \\
    \vspace{2mm}
    %(x)s \bottomrule
    \end{tabular}
    \end{center}
    \end{document}
    ''' 

    with open(filename, 'wb') as f:
        f.write(template % {'x' : table })

    subprocess.call(['pdflatex', filename])
    os.rename("out.pdf", "surface_analysis.pdf")
    os.system("rm out.*")

n_fig = 0
surface_table_data = {}
for model_name in models:
    table_entry = []
    for test_name in tests:
        print "DO {} {}".format(model_name, test_name)

        try:
            (cur_min_EV, cur_composition) = read_ref_bulk_model_struct(args.test_set, model_name, data[model_name][test_name]["bulk_struct_test"])
        except:
            print "No data"
            continue
        try:
            (stable_mu_extrema, full_mu_range) = mu_range(cur_min_EV, cur_composition, data[model_name][test_name]["bulk_struct_test"], mcc_compositions, mcc_energies[model_name])
        except:
            (stable_mu_extrema, full_mu_range) = (None,None)
        # print model_name, test_name, "stable_mu_extrema", stable_mu_extrema
        # print "full_mu_range", full_mu_range
        if stable_mu_extrema is not None:
            if len(stable_mu_extrema) > 0:
                print "stable mu range:"
                for pt in stable_mu_extrema:
                    for Z in sorted(pt.keys()):
                        print "mu_{} = {}".format(Z, pt[Z]),
                    print ""
            else:
                print "stable mu range: None"

        # print "data", data[model_name][test_name]
        if data[model_name][test_name]["dmu"] is None: # single component
            print "SURFACE", model_name, test_name, data[model_name][test_name]["Ef"]
            table_entry.append((test_name, "{}".format(data[model_name][test_name]["Ef"])))
        else: # multicomponent
            print "SURFACE", model_name, test_name, data[model_name][test_name]["Ef"],"+ ",
            l = "{} + ".format(data[model_name][test_name]["Ef"])
            mu_contrib_min_total = 0.0
            mu_contrib_max_total = 0.0
            l = ""
            for mu_Z in data[model_name][test_name]["dmu"]:
                n_dmu = data[model_name][test_name]["dmu"][mu_Z]
                if n_dmu != 0:
                    print "( {} * mu_{} =".format(n_dmu,mu_Z),
                    l += " ( {} * mu_{} =".format(n_dmu,mu_Z)
                    mu_min = min([ mu_pt[int(mu_Z)] for mu_pt in stable_mu_extrema] )
                    mu_max = max([ mu_pt[int(mu_Z)] for mu_pt in stable_mu_extrema] )
                    mu_contrib_min = np.finfo(float).max
                    mu_contrib_max = -np.finfo(float).max
                    mu_contrib_min = min(mu_contrib_min, n_dmu*mu_min)
                    mu_contrib_min = min(mu_contrib_min, n_dmu*mu_max)
                    mu_contrib_max = max(mu_contrib_max, n_dmu*mu_min)
                    mu_contrib_max = max(mu_contrib_max, n_dmu*mu_max)
                    print "[",mu_contrib_min,"--",mu_contrib_max,"] )",
                    l += " [ {} -- {} ]".format(mu_contrib_min, mu_contrib_max)
                    mu_contrib_min_total += mu_contrib_min
                    mu_contrib_max_total += mu_contrib_max
            print " = [", data[model_name][test_name]["Ef"] + mu_contrib_min_total,"--",data[model_name][test_name]["Ef"] + mu_contrib_max_total,"]"
            l += " = [ {} -- {} ]".format(data[model_name][test_name]["Ef"] + mu_contrib_min_total,data[model_name][test_name]["Ef"] + mu_contrib_max_total)
            table_entry.append((test_name, l))

        print ""

    for (test_name, Ef) in table_entry:
        if test_name not in surface_table_data:
            surface_table_data[test_name] = {}
        surface_table_data[test_name][model_name] = Ef

#print data

surfaces_sorted = sorted(surface_table_data.keys())
surfaces_sorted_print = [ n.replace("surface_","").replace("_"," ") for n in surfaces_sorted ]

ref_model = default_analysis_settings['ref_model']

surfaces_sorted_dict = {}

for s in surfaces_sorted:
    ref_value = surface_table_data[s][ref_model]
    model_dict = {}
    for model_name in models:
        if model_name != ref_model:
            try:
                pct_diff = int((float(surface_table_data[s][model_name])-float(ref_value))/(float(ref_value))*100)
                model_dict[model_name] = str(pct_diff) + "\%"
            except:
                pass
        if model_name == ref_model:
            model_dict[model_name] = ref_value
    surfaces_sorted_dict[s] = model_dict

table = "\\begin{tabular}{ l " + " ".join(["c"]*len(surfaces_sorted)) + " } \\toprule \n"
table += "Model & "+" & ".join( [ n for n in surfaces_sorted_print ] ) + "\\\ \midrule \n"

def add_to_table(model, table, surf_dict):
    table += model.replace("_","\\_") 
    for s in surf_dict:
        if model in surf_dict[s]:
            table += " & " + "{}".format(surf_dict[s][model][:5]) 
        else:
            table += " & & "
    table += "\\\\ \n"
    return table

table = add_to_table(ref_model, table, surfaces_sorted_dict)

#do over testname


for test_name in tests:
    for model_name in sorted(surfaces_sorted_dict[test_name].keys()):
        if model_name != ref_model:
            table = add_to_table(model_name, table, surfaces_sorted_dict)
    pdf_table(table)

#table = "\\begin{tabular}{ l " + " ".join(["c"]*len(surfaces_sorted)) + " } \\toprule \n"
#table += "Model & "+" & ".join( [ n for n in surfaces_sorted_print ] ) + "\\\ \midrule \n"
#for model_name in models:
#    table += model_name.replace("_","\\_") 
#    for s in surfaces_sorted:
#        if model_name in surface_table_data[s]:
#            table += " & " + "{}".format(surface_table_data[s][model_name][:5]) 
#        else:
#            table += " & & "
#    table += "\\\\ \n"

#pdf_table(table)

######
#print "\\begin{tabular}{ l & " + " & ".join(["c"]*len(surfaces_sorted)) + " }"
#print "model & "+" & ".join( [ n for n in surfaces_sorted_print ] ),
#for model_name in models:
#    print "\\\\\n"+model_name.replace("_","\\_"),
#    for s in surfaces_sorted:
#        if model_name in surface_table_data[s]:
#            print " & " + "{}".format(surface_table_data[s][model_name]),
#        else:
#            print " & & ",
#print "\n\\end{tabular}"
####

