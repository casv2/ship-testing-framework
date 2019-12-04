using IPAnalysis

cd("./example_run_dir/Ti/models/SHIP_Ti_5B")

read_IP("./Ti_5B_o_reg.json")

using JuLIP

D = load_json("./Ti_5B_o_reg.json")

IP = decode_dict(D["IP"])
