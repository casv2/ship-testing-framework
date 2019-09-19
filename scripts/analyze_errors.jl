using JSON, Printf, NBodyIPs, NBodyIPs

# file = JSON.parsefile("./scripts/foo.json")
# data_PIP = JSON.parse(file)
#
# file_GAP = JSON.parsefile("./GAP_6.json")
# data_GAP = JSON.parse(file_GAP)
#
# data_GAP["sh"]

IP1, info1 = load_ip("./example_run_dir/Si/models/PIP_4B_dia_weight1/BA4_fit.json")
IP3, info3 = load_ip("./example_run_dir/Si/models/PIP_4B_dia_weight3/BA4_fit_dw3.json")
IP5, info5 = load_ip("./example_run_dir/Si/models/PIP_4B_dia_weight5/BA4_fit_dw5.json")
IP10, info10 = load_ip("./example_run_dir/Si/models/PIP_4B_dia_weight10/BA4_fit_dw10.json")

info10["errors"]["rmse"]

println("=======================================================")
println("|    Energy    |  PIP1  |  PIP3   |  PIP5   |  PIP10  |")
for config in keys(info10["errors"]["rmse"])
    if config != "set"
        s = @sprintf("| %12s | %.6s | %.6s  | %.6s  | %.6s  |", config, info1["errors"]["rmse"][config]["E"],
        info3["errors"]["rmse"][config]["E"], info5["errors"]["rmse"][config]["E"], info10["errors"]["rmse"][config]["E"])
        println(s)
    end
end

println("=======================================================")
println("|    Energy    |  PIP1  |  PIP3   |  PIP5   |  PIP10  |")
for config in keys(info10["errors"]["rmse"])
    if config != "set"
        s = @sprintf("| %12s | %.6s | %.6s  | %.6s  | %.6s  |", config, info1["errors"]["rmse"][config]["F"],
        info3["errors"]["rmse"][config]["F"], info5["errors"]["rmse"][config]["F"], info10["errors"]["rmse"][config]["F"])
        println(s)
    end
end
println("===================================")

println("|    Stress    |   GAP  |   PIP   |")
for config in keys(data_PIP["rmse"])
    if config != "set"
        try
            data_PIP["rmse"][config]["V"]
        catch
            data_PIP["rmse"][config]["V"] = "   NaN  "
        end
        s = @sprintf("| %12s | %.6s | %.6s  |", config, data_GAP[config]["RMSE_V"], data_PIP["rmse"][config]["V"])
        println(s)
    end
end
println("===================================")

keys(data_PIP["rmse"])
