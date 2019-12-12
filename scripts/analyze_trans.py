import matplotlib
matplotlib.use('PDF')
from matplotlib.pyplot import *
from analyze_utils import *
import numpy as np

(args, models, tests, default_analysis_settings) = analyze_start('TiAl_trans_2')

ref_linestyles=[ "-", "--" ]
other_linestyles=[ ":", "-." ]
struct_colors = [ "black", "red", "blue", "orange", "green", "brown", "grey", "magenta","cyan" ]

ref_model_name = default_analysis_settings["ref_model"]

#models = models + [ref_model_name]

data = read_properties(models, tests, args.test_set)

print data

n = 0
for model in sorted(models):
	E = data[model]['TiAl_trans_2']['energy']

	if model != ref_model_name:
		n+=1
		plot(np.array(E)-min(E), linestyle=other_linestyles[1], color=struct_colors[n], label=model)
	else:
		plot(np.array(E)-min(E), linestyle=ref_linestyles[0], color=struct_colors[0], label=model)


title(tests[0])
xlabel("Path")
ylabel("Energy (eV)")
legend()
savefig("{}.pdf".format(tests[0]), bbox_inches='tight')
