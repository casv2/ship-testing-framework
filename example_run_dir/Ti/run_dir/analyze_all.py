import os
import subprocess

cwd = os.getcwd()
element = cwd.split("/")[-2]

ps = []
tests = ["bulks", "layer_test", "dimer", "burgers_path", "phonon", "QHA"] #, "surface_decohesion"]#, "phonon"]

for test in tests:
	r_str = ("python ../../../scripts/analyze_{}.py".format(test)).split(" ")
	print r_str
	p = subprocess.Popen(r_str)
	ps.append(p)

for p in ps:
	p.wait()

##phonon taken out

#PERHAPS JUS TAKE ALL PDF FILES
os.system("julia ../../../scripts/analyze_models.jl")
os.system("pdfjoin --paper a4paper --rotateoversize false *_IPanalysis.pdf -o model_analysis.pdf")
os.system("pdfjoin --paper a4paper --rotateoversize false model_analysis.pdf bulk_analysis.pdf burgers_path.pdf phonon_hcp.pdf phonon_bcc.pdf layer_test.pdf")
os.system("mv layer_test-joined.pdf {}_analysis.pdf".format(element))
os.system("rm *.png")
