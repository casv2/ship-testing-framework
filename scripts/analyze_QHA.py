import os
import glob
import shutil
from analyze_utils import *

import matplotlib
matplotlib.use('PDF')
from matplotlib.pyplot import *

#print os.path.abspath(os.path.dirname(__file__))

# cwd = os.getcwd()
# element = cwd.split("/")[-2]
#
# print element

(args, models, tests, default_analysis_settings) = analyze_start('QHA')

ref_linestyles=[ "-", "--", "-." ]
other_linestyles=[ ":", "-." ]
struct_colors = [ "black", "red", "blue", "orange", "green", "brown", "grey", "magenta","cyan" ]

print args, models, tests, default_analysis_settings

#models = models[1:]

data = {}
struct_data = {}
for model_name in models:
    sys.stderr.write("reading data for model {}\n".format(model_name))
    data[model_name] = {}
    cur_model_data = {}
    for bulk_test_name in tests:
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

for (i,model) in enumerate(models):
    if model.startswith("CASTEP"):
        del models[i]

n = 0
for model in sorted(models):
    if model_name != ref_model_name:
        n+=1
        plot(data[model]["QHA"]["temperatures"], data[model]["QHA"]["heat_capacity"], color=struct_colors[n], label=model)
        plot(data[model]["QHA"]["temperatures"], data[model]["QHA"]["entropy"], color=struct_colors[n])
        plot(data[model]["QHA"]["temperatures"], data[model]["QHA"]["free_energy"], color=struct_colors[n])
    else:
        plot(data[model]["QHA"]["temperatures"], data[model]["QHA"]["heat_capacity"], color=struct_colors[0], label=model)
        plot(data[model]["QHA"]["temperatures"], data[model]["QHA"]["entropy"], color=struct_colors[0])
        plot(data[model]["QHA"]["temperatures"], data[model]["QHA"]["free_energy"], color=struct_colors[0])

title("QHA")
xlabel("Temperature (K)")
#ylabel("Energy (eV)")
legend()
savefig("QHA.pdf", bbox_inches='tight')


# for model_name in sorted(models):
#     if bool(data[model_name]["layer_test"]) == True:
#         E = data[model_name]["layer_test"]["energy"]
#         R = data[model_name]["layer_test"]["distance"]
#
#         if model_name != ref_model_name:
#             n+=1
#             plot(R, E, color=struct_colors[n], label=model_name)
#         else:
#             plot(R, E, color=struct_colors[0], label=model_name)
#
# title(bulk_tests[0])
# xlabel(r"Interplanar spacing $(\AA)$")
# ylabel("Energy (eV)")
# legend()
# savefig("layer_test.pdf", bbox_inches='tight')
