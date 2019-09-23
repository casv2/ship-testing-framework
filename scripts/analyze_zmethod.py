import os
import glob
import shutil
from analyze_utils import *
import matplotlib.pyplot as plt
import numpy as np

cwd = os.getcwd()
element = cwd.split("/")[-2]

print element

(args, models, tests, default_analysis_settings) = analyze_start('Zmethod_*')

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


models = ["SHIP_v1"]
#
tests = ["Zmethod_Ti_bcc", "Zmethod_TiAl", "Zmethod_Al_fcc"]

fig, axs = plt.subplots(nrows=1, ncols=3, sharex=True, figsize=(18,6))

Tmelt = {}
Tmelt["Zmethod_Ti_bcc"] = 1941
Tmelt["Zmethod_TiAl"] = 1776
Tmelt["Zmethod_Al_fcc"] = 934

for (i,test) in enumerate(tests):
    axs[i].axhline(y=Tmelt[test], label="Tm (at 0 GPa)", color="red")
    P, T = data["SHIP_v1"][test]["P"][1000:], data["SHIP_v1"][test]["T"][1000:]
    P = 160.21766208*np.array(P)


    steps = 2000
    points = [j*steps for j in xrange(len(P)/steps)]

    Tm_l, Pm_l = [], []

    for k in xrange(len(P)/steps - 1):
        Pm = np.mean(P[points[k]:points[k+1]])
        Tm = np.mean(T[points[k]:points[k+1]])
        Tm_l.append(Tm)
        Pm_l.append(Pm)

    Tmelt_mn = list(filter(lambda x: x < 0, np.diff(Tm_l)))[-1]
    Tmelt_est_index = np.diff(Tm_l).tolist().index(Tmelt_mn)
    axs[i].axhline(y=Tm_l[Tmelt_est_index+1], label="Tm est", color="blue")
    axs[i].scatter(P, T, s=0.001, label="SHIP_v1")
    axs[i].scatter(Pm_l, Tm_l, s=10, label="means")
    axs[i].legend()
    axs[i].set_xlabel("Pressure (GPa)")
    if i == 0:
        axs[i].set_ylabel("Temperature (K)")
    axs[i].set_title(test)

fig.savefig("Zmethod.png")
