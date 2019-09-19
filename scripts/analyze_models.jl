using SHIPs
using Printf, Glob, PyCall, IPFitting, ASE, JSON, Statistics, IPAnalysis, JuLIP #NBodyIPs

quippy = pyimport("quippy")

cur_work = pwd()

element = split(cur_work, "/")[end-1]
model_dir = joinpath("/Users/Cas/gits/ship-testing-framework/example_run_dir/", element, "models")

function GAP_errors(xml_file_path, xyz_file_path)

    open(xml_file_path) do file
        for ln in eachline(file)
            if startswith(ln, "<")
                global init_args = ln[2:end-1]
                break
            end
        end
    end

    pot = quippy.Potential(println(init_args), param_filename=xml_file_path)
    ASE_pot = ASECalculator(pot)

    al = IPFitting.Data.read_xyz(xyz_file_path)#

    add_fits_serial!(ASE_pot, al, fitkey="gap")

    config_types = unique([at.configtype for at in al])

    data = Dict()

    for config in config_types
        ref_el = []
        gap_el = []
        ref_fl = []
        gap_fl = []
        ref_vl = []
        gap_vl = []
        for (i,at) in enumerate(al)
            if at.configtype == config
                @show i
                push!(gap_el, at.info["gap"]["E"][1]/length(Atoms(at).X))
                push!(ref_el, at.D["E"][1]/length(Atoms(at).X))
                push!(gap_fl, at.info["gap"]["F"])
                push!(ref_fl, at.D["F"])
                try
                    push!(ref_vl, at.D["V"]/length(Atoms(at).X))
                    push!(gap_vl, at.info["gap"]["V"]/length(Atoms(at).X))
                catch
                    println("No Virial")
                end
            end
        end
        data[config] = Dict()
        @show ref_vl
        @show gap_vl
        @show length(ref_vl), length(gap_vl)
        RMSE_E = (mean((ref_el - gap_el).^2.0)).^(0.5)
        RMSE_F = (mean((vcat(ref_fl...) - vcat(gap_fl...)).^2.0)).^(0.5)
        try
            RMSE_V = (mean((vcat(ref_vl...) - vcat(gap_vl...)).^2)).^(0.5)
            data[config]["RMSE_V"] = RMSE_V
        catch
            data[config]["RMSE_V"] = "  NaN  "
            RMSE_V = "  NaN   "
        end

        data[config]["RMSE_E"] = RMSE_E
        data[config]["RMSE_F"] = RMSE_F
        #data[config]["RMSE_V"] = RMSE_V

        @show RMSE_E, RMSE_F#, RMSE_V
    end

    json_string = JSON.json(data)

    open("errors.json","w") do f
      JSON.print(f, json_string)
    end

end

    #pot = quippy.Potential(println("init_args=GAP_2017_6_17_60_4_3_56_165"), param_filename="example_run_dir/Si/models/GAP_6/gp_iter6_sparse9k.xml"); #import GAP pot. init_args is equal to first line of .xml file
    #al = IPFitting.Data.read_xyz("/Users/Cas/Dropbox/PIBmat/Si/silicon_database_gp_iter6_sparse9k.xml.xyz")[1:10:end]
    #pot = ASECalculator(pot)
    #add_fits_serial!(pot, al, fitkey="gap")


function GAP_to_latex(xml_file_path, json_file_path)

    open(xml_file_path) do file
        for ln in eachline(file)
            if startswith(ln,"  <command_line>")
                command_line = ln[27:end-18]
                command_line = replace(command_line, "_" => "\\_")
                global command_line = replace(command_line, "=" => "\$=\$")
            end
        end
    end

    error_table = "\\begin{supertabular}{ l c c c } \\toprule \n"
    error_table *= "Config type & E (meV) & F (eV/A) & V (meV) \\\\ \\midrule \n"

    data = JSON.parse(JSON.parsefile(json_file_path))

    for type in ["isolated_atom", "slice_sample"]
        try
            delete!(data, type)
        catch
        end
    end

    types = sort(collect(keys(data)))

    for key in types
        if key != "slice_sample" || key != "isolated_atom"
            E = try string(round(data[key]["RMSE_E"]*1000, digits=3)) catch; "NaN" end #E = try string(data[key]["RMSE_E"])[1:7] catch; "NaN" end
            F = try string(round(data[key]["RMSE_F"], digits=3)) catch; "NaN" end
            V = try string(round(data[key]["RMSE_V"]*1000, digits=3)) catch; "NaN" end
            s = @sprintf "%s & %s & %s & %s \\\\ \n" replace(key, "_" => "\\_") E F V
            error_table *= s
        end
    end

    error_table *= "\\end{supertabular}"

    pot_name = split(xml_file_path, "/")[end-1]
    latex_pot_name = replace(pot_name, "_" => "\\_")

    template = "\\documentclass[a4paper,landscape]{article}
    \\usepackage{booktabs}
    \\usepackage[a4paper,margin=1in,landscape,twocolumn]{geometry}
    \\usepackage{amsmath}
    \\usepackage{graphicx}
    \\usepackage{subfig}
    \\usepackage{diagbox}
    \\usepackage{supertabular}
    \\begin{document}
    \\begin{center}
    \\vspace{2mm}
    \\textbf{name}: $latex_pot_name
    \\vspace{2mm}
    \\textbf{command line}: $command_line \\\\
    \\vspace{3mm}
    $error_table \\\\
    \\end{center}
    \\end{document}"

    write("out.tex", template)

    potname_file = pot_name * "_IPanalysis.pdf"

    run(`pdflatex out.tex`)
    run(`mv out.pdf $potname_file`)
    #sleep(1)
    run(`rm out.tex out.log out.aux`)
    #println(error_table)

    return nothing
end

for model in readdir(model_dir)
    if model == ".DS_Store"
        continue
    end
    fit_dir = joinpath(model_dir, model)
    cd(fit_dir)
    @show readdir(fit_dir)
    # if startswith(model, "GAP")
    #     if length(glob("*.json")) == 0
    #         xyz_file = glob("*.xyz")[1]
    #         xml_file = glob("*.xml")[1]
    #         xml_file_path = joinpath(fit_dir, xml_file)
    #         xyz_file_path = joinpath(fit_dir, xyz_file)
    #         GAP_errors(xml_file_path, xyz_file_path)
    #     end
    #     xml_file = glob("*.xml")[1]
    #     json_file = glob("*.json")[1]
    #     xml_file_path = joinpath(fit_dir, xml_file)
    #     json_file_path = joinpath(fit_dir, json_file)
    #     cd(cur_work)
    #     GAP_to_latex(xml_file_path, json_file_path)
    if startswith(model, "SHIP")
        fit_file = glob("*.json")[1]
        @show fit_file
        ## PIPs
        #IP, info = load_ip(fit_file)
        ## aPIPs
        D = load_json(fit_file)
        IP = decode_dict(D["IP"])
        info = D["fitinfo"]
        cd(cur_work)
        IPAnalysis.Plotting.IP_pdf(IP, rnn(Symbol(element)), info, save_plot=true, filename=model)
    end
    # elseif startswith(model, "PIP")
    #     fit_file = glob("*.json")[1]
    #     #@show fit_file
    #     ## PIPs
    #     IP, info = load_ip(fit_file)
    #     ## aPIPs
    #     #D = load_json(fit_file)
    #     #IP = decode_dict(D["IP"])
    #     #info = D["fitinfo"]
    #     cd(cur_work)
    #     IPAnalysis.Plotting.IP_pdf(IP, rnn(Symbol(element)), info, save_plot=true, filename=model)
    # end
end

#cd(cur_work)
#run(`pdfjoin --paper a4paper --rotateoversize false *_IPanalysis.pdf -o model_analysis.pdf`)
