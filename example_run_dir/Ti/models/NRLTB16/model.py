from quippy import Potential
import os

model_dir = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(model_dir, '16x16x16k_mesh_param_file_tightbind.parms.NRL_TB.Ti_spline.xml')

calculator = Potential('TB NRL-TB', param_filename = filename, Fermi_T = 0.1)

no_checkpoint = True
name = 'DFTB'
