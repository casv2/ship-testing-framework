using Glob
using IPAnalysis

cur_work = pwd()

element = split(cur_work, "/")[end-1]
model_dir = joinpath("/Users/Cas/gits/ship-testing-framework/example_run_dir/", element, "models")

for model in readdir(model_dir)
    fit_dir = joinpath(model_dir, model)
    cd(fit_dir)
    @show readdir(fit_dir)

    if startswith(model, "SHIP")
        fit_file = glob("*.json")[1]
        @show fit_file
        fit_path = joinpath(fit_dir, fit_file)
        @show fit_path
        IPAnalysis.Plotting.IP_pdf(model, fit_file, fit_path, cur_work)
        cd(cur_work)
    end
end
