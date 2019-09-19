import matplotlib
matplotlib.use('PDF')
from matplotlib.pyplot import *
from analyze_utils import *

(args, models, tests, default_analysis_settings) = analyze_start('burgers_path')

ref_linestyles=[ "-", "--" ]
other_linestyles=[ ":", "-." ]
struct_colors = [ "black", "red", "blue", "orange", "green", "brown", "grey", "magenta","cyan" ]

ref_model_name = default_analysis_settings["ref_model"]

#models = models + [ref_model_name]

data = read_properties(models, tests, args.test_set)

n = 0
for model in sorted(models):
	E = data[model]['burgers_path']['energy']

	if model != ref_model_name:
		n+=1
		plot(E, linestyle=other_linestyles[1], color=struct_colors[n], label=model)
	else:
		plot(E, linestyle=ref_linestyles[0], color=struct_colors[0], label=model)


title(tests[0])
xlabel("BCC to HCP")
ylabel("Energy (eV)")
legend()
savefig("{}.pdf".format(tests[0]), bbox_inches='tight')
