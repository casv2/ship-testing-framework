using Glob
using IPAnalysis

cur_work = pwd()

element = split(cur_work, "/")[end-1]
model_dir = joinpath("/Users/Cas/gits/ship-testing-framework/example_run_dir/", element, "models")

for model in readdir(model_dir)
    if model == ".DS_Store"
        continue
    end
    fit_dir = joinpath(model_dir, model)
    cd(fit_dir)
    @show readdir(fit_dir)

    if startswith(model, "SHIPs")
        fit_file = glob("*.json")[1]
        @show fit_file
        fit_path = joinpath(fit_dir, fit_file)
        @show fit_path
        cd(cur_work)
        IPAnalysis.Plotting.IP_pdf(fit_path, model)
    end
end
