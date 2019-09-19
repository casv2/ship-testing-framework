#import json
import os
import glob

# models_path = os.path.join(os.getcwd(),'../models')
# models = glob.glob(os.path.join(models_path, '*'))
#
# for model in models:
#     for filename in os.listdir(models):
#         if
import json

cwd = os.getcwd()

print os.listdir(cwd)

with open('./scripts/foo.json') as json_file:
    data = json.load(json_file)

data

import pandas as pd

pd.read_json('./scripts/foo.json', orient="columns")
