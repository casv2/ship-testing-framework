import os
import glob
import shutil
from analyze_utils import *
import matplotlib.pyplot as plt

cwd = os.getcwd()
element = cwd.split("/")[-2]

print element

(args, models, tests, default_analysis_settings) = analyze_start('Zmethod_TiAl')

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



# plt.plot(data["SHIP_test"]["Zmethod_TiAl"]["E_tot"], label="E_tot")
# #plt.plot(data["SHIP_test"]["Zmethod_TiAl"]["E_kin"], label="E_kin")
# #plt.plot(data["SHIP_test"]["Zmethod_TiAl"]["E_pot"], label="E_pot")
#plt.scatter(data["SHIP_v1"]["Zmethod_TiAl"]["P"][100:], data["SHIP_v1"]["Zmethod_TiAl"]["T"][100:])
plt.plot(data["SHIP_v1"]["Zmethod_TiAl"]["T"][100:])
plt.legend()
plt.savefig("Zmethod_Energy.png")
