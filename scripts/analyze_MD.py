import matplotlib
matplotlib.use('PDF')
from matplotlib.pyplot import *
from analyze_utils import * 

(args, models, tests, default_analysis_settings) = analyze_start('MD')

ref_linestyles=[ "-", "--" ]
other_linestyles=[ ":", "-." ]
struct_colors = [ "black", "red", "blue", "cyan", "orange", "magenta", "green", "grey", "brown" ]

ref_model_name = default_analysis_settings["ref_model"]

data = read_properties(models, tests, args.test_set)

print data

n = 0
for model in models:
	if bool(data[model]) == True:
		E = [float(E) for E in data[model]['MD']['E']]

		if model != ref_model_name:
			n+=1
			plot(E, linestyle=other_linestyles[1], color=struct_colors[n], label=model)
		else:
			plot(E, linestyle=ref_linestyles[0], color=struct_colors[0], label=model)


title(tests[0])
xlabel("MD steps")
ylabel("Kinetic Energy (eV)")
legend()
savefig("{}".format(tests[0]), bbox_inches='tight')