import numpy as np
from ase.calculators.calculator import Calculator

import os
from julia import Julia

if not os.environ.has_key('JL_RUNTIME_PATH'):
    julia = Julia()
else:
    # "/Users/ortner/gits/julia6bp/usr/bin/julia"
    julia = Julia(jl_runtime_path=os.environ['JL_RUNTIME_PATH'])

julia.using("NBodyIPs")
julia.using("ASE")
julia.using("NBIPsMulti")
julia.using("JuLIP")
#julia.using("JSON")

def import_IP(potname):
    #julia.eval("IP = load_ip(\"" + potname + "\")")
    julia.eval("IP, info = load_ip(\""+ potname + "\")")
    julia.eval("oneB_a = MOneBody(Dict(\"E0\" => Dict(\"Al\" => -105.5952, \"Ti\" => -1585.9998)))")
    julia.eval("IP.components[1] = oneB_a")
    julia.eval("IPf = fast(IP)")
    #julia.eval("IPf = NBodyIPs.Experimental.faster_envpot(IP)")
    #julia.eval("IPASE = ASECalculator(IPf)") ###ISNT THIS SLOW??
    #julia.eval("info_string = JSON.json(info)")
    #julia.eval("open(\"info.json\", \"w\") do f JSON.print(f, info_string) end")
    IP = julia.eval("IPf")
    return IP
