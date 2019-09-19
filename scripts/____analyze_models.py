import os
import glob
import subprocess
import time

from julia import Julia

if not os.environ.has_key('JL_RUNTIME_PATH'):
    julia = Julia()
else:
    # "/Users/ortner/gits/julia6bp/usr/bin/julia"
    julia = Julia(jl_runtime_path=os.environ['JL_RUNTIME_PATH'])

models_path = os.path.join(os.getcwd(),'../models')
models = glob.glob(os.path.join(models_path, '*'))

def GAP_reader(model, filename):
	pot_string = ""
	gap_configs = []

	xml_file = open(os.path.join(model, filename))
	for line in xml_file:
		if line.startswith("  <command_line>"):
			pot_string = line
		#if line.startswith("    <![CDATA[config_type"):
		#	gap_configs.append(line.split("=")[1].split(" ")[0])
		#	continue
		if "configtype=" in line:
			#print line.split("configtype")[1].split(" ")[0][1:]
			gap_configs.append(line.split("configtype")[1].split(" ")[0][1:])
			continue
		if "config_type=" in line:
			gap_configs.append(line.split("config_type")[1].split(" ")[0][1:])
			continue

	configs = [config for config in set(gap_configs)]
	num_configs = [gap_configs.count(config) for config in set(gap_configs)]
	config_dict = dict(zip(configs, num_configs))

	print config_dict

	return pot_string, config_dict, filename

def GAP_info_to_tex(pot_string, config_dict, filename):
	table = "\\begin{supertabular}{ l c } \\toprule \n"
	table += " Config type & Number of configs \\\ \midrule \n"

	for key in sorted(config_dict.keys()):
		table += key.replace("_", "\_").replace("%", "\%") + " & " + str(config_dict[key]) + "\\\\ \n"

	model_name = model.split("/")[-1].replace("_", "\_")

	return pot_string, table, model_name

def GAP_tex_to_pdf(pot_string, table, model_name):
	filename = 'out.tex'

	template = r'''
	\documentclass[a4paper,landscape]{article}
	\usepackage{booktabs}
	\usepackage[a4paper,margin=1in,landscape]{geometry}
	\usepackage{supertabular}
	\begin{document}
	\begin{center}
	\textbf{Model}: %(model)s \\
	\textbf{Command Line}: %(pot_string)s \\
	\vspace{5mm}
	%(table)s \bottomrule
	\end{supertabular}
	\end{center}
	\end{document}
	'''

	with open(filename, 'wb') as f:
		f.write(template % {'model' : model_name, 'table' : table, 'pot_string' : pot_string.split("[ ")[1].split("]]")[0].replace("_", "\_").replace("=", "$=$")})

	subprocess.call(['pdflatex', filename])
	os.rename("out.pdf", "{}_IPanalysis.pdf".format(model_name))
	os.system("rm out.*")

#print models

for model in models:
	if model.endswith("CASTEP_ASE"):
		models.remove(model)
	#if model.endswith("PIP_4BBA"):
	#	models.remove(model)
	if model.endswith("PIP_4BBAenv"):
		models.remove(model)

#print models

for model in models:
	for filename in os.listdir(model):
		if filename.endswith(".xml"):
			with open(os.path.join(model, filename)) as f:
				first_line = f.readline()
				if first_line.startswith("<GAP_"):
					pot_string, config_dict, filename = GAP_reader(model, filename)
					if bool(config_dict) == False:
						for filename in os.listdir(model):
							if filename.endswith("xyz"):
								pot_string_wrong, config_dict, filename = GAP_reader(model, filename)
					pot_string, table, model_name = GAP_info_to_tex(pot_string, config_dict, filename)
					GAP_tex_to_pdf(pot_string, table, model_name)

		elif filename.endswith(".json"):
			#print filename.split(".")[0]
			file_path = os.path.join(os.path.join(models_path, model), filename)
			julia.using("IPAnalysis")
			julia.using("NBodyIPs")
			julia.eval("IP, info = load_ip(\""+ file_path + "\")")
			julia.eval("IPAnalysis.Plotting.IP_pdf(IP, info,\"" + filename.split(".")[0] + "\")")

			#except:
			#	pass
			#print filename
			#julia.eval("IP, info = load_ip(\""+ filename + "\")")

#os.system("pdfjoin --paper a4paper --rotateoversize false *_IPanalysis.pdf -o model_analysis.pdf")
#time.sleep(1)
#os.system("rm *_IPanalysis.pdf *_plot.png")
