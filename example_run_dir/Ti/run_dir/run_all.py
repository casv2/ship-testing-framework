import os
import subprocess
import sys

model = sys.argv[1]

ps = []
tests = ["bulk_Ti_bcc", "bulk_Ti_hcp", "phonon_bcc", "phonon_hcp"]

for test in tests:
	r_str = ("python ../../../scripts/run-model-test.py {0} {1} -s Ti -f".format(model, test)).split(" ")
	print r_str
	p = subprocess.Popen(r_str)
	ps.append(p)

for p in ps:
	p.wait()

# tests = ["phonon_Ti_bcc", "phonon_Ti_hcp", "phonon_Al", "phonon_Ti3Al", "phonon_TiAl", "phonon_TiAl3", "TiAl_trans_2"]

# ps = []

# for test in tests:
# 	r_str = ("python ../../../scripts/run-model-test.py {0} {1} -s TiAl -f".format(model, test)).split(" ")
# 	print r_str
# 	p = subprocess.Popen(r_str)
# 	ps.append(p)

# for p in ps:
# 	p.wait()
