import matplotlib
matplotlib.use('PDF')
from matplotlib.pyplot import *

import json
import os
import itertools
import glob
from analyze_utils import *

(args, models, bulk_tests, default_analysis_settings) = analyze_start('gibbs_*')

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

#gibbs_diff = np.array(data["PIP_MCMC_ho100K_novir"]["gibbs_omega"]["gibbs_omega"]) - np.array(data["PIP_MCMC_ho100K_novir"]["gibbs_hcp"]["gibbs_hcp"])


plot(data["PIP_MCMC_ho100K_novir"]["gibbs_omega"]["temperatures"][1:], np.array(data["PIP_MCMC_ho100K_novir"]["gibbs_omega"]["gibbs_omega"]), label="omega")
plot(data["PIP_MCMC_ho100K_novir"]["gibbs_omega"]["temperatures"][1:], np.array(data["PIP_MCMC_ho100K_novir"]["gibbs_hcp"]["gibbs_hcp"]), label="hcp")
legend()
savefig("gibbs_diff.pdf", bbox_inches='tight')
