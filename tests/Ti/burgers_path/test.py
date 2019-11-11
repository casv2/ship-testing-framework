import ase.io, os
import model

al = ase.io.read(os.path.join(os.path.dirname(__file__),"burgers_path_DFT.xyz"),":")
E = []

for at in al:
    at.set_calculator(model.calculator)
    e = at.get_potential_energy()/len(at)
    E.append(e)

properties = {'energy' : E}
