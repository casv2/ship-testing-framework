import os
import subprocess
import sys

cwd = os.getcwd()
element = cwd.split("/")[-2]

os.system("rm *.pdf")

try:
	model = sys.argv[1]
except:
	sys.exit("No model given.")

ps = []
tests =  ["bulk_Ti_bcc", "bulk_Ti_hcp", "burgers_path", "dimer", "layer_test", "phonon_bcc", "phonon_hcp"] #["phonon_bcc", "phonon_hcp"] 
	#["phonon_bcc". "phonon_hcp"]
			#"surface_decohesion_Si_diamond_100", "surface_decohesion_Si_diamond_110", "surface_decohesion_Si_diamond_111"]

for test in tests:
	r_str = ("python ../../../scripts/run-model-test.py {0} {1} -s {2} -f".format(model, test, element)).split(" ")
	print r_str
	p = subprocess.Popen(r_str)
	ps.append(p)

for p in ps:
	p.wait()
