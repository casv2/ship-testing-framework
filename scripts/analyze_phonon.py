import os
import glob
import shutil
from analyze_utils import *

#print os.path.abspath(os.path.dirname(__file__))
cwd = os.getcwd()
element = cwd.split("/")[-2]

print element

(args, models, phonon_tests, default_analysis_settings) = analyze_start('phonon_*')

# for (i,model) in enumerate(models):
#     if model.startswith("PIP"):
#         del models[i]

#del models[0]
#print phonon_tests
phonon_tests = ["phonon_TiAl", "phonon_Ti3Al", "phonon_TiAl3"]

def create_phonon_pdf(phonon_test):
    names = []
    print phonon_test
    for model in models:
        for file in glob.glob(os.path.join(os.getcwd(), 'run_{}-model-{}-test-{}'.format(element,model, phonon_test), "*.yaml")):
            print file
            name = file.split("/")[-1]
            print name
            names.append(name)
            shutil.copyfile(file, os.path.join(cwd, name))

    name_str = " ".join(names)

    print name_str
    os.system("phonopy-bandplot --legend " + name_str + " -t {0} -o \"{1}.pdf\"".format(phonon_test, phonon_test))
    os.system("rm *.yaml")

for phonon_test in phonon_tests:
    create_phonon_pdf(phonon_test)
