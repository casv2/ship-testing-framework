from ase.io import read, write
from ase.calculators.calculator import Calculator
from ase.calculators.singlepoint import SinglePointCalculator
from ase.optimize import FIRE
from ase.optimize.precon import PreconLBFGS
from ase.constraints import ExpCellFilter, FixAtoms, voigt_6_to_full_3x3_stress, full_3x3_to_voigt_6_stress
from quippy.potential import Minim
import numpy as np
import os.path
import sys

import symmetrize

#from quippy.io import AtomsWriter
#from quippy.cinoutput import CInOutput,OUTPUT
#from quippy.atoms import Atoms

def name_of_file(file):
    if '/' in file:
        name = os.path.basename(os.path.dirname(file))
    else:
        name = file
    return name

def model_test_root(u_model_name=None, u_test_name=None, base_model=False):
    if u_model_name is None:
        if base_model:
            u_model_name = base_model_name
        else:
            u_model_name = model_name
    if u_test_name is None:
        u_test_name = test_name
    if system_label != '':
        return '{0}-model-{1}-test-{2}'.format(system_label, u_model_name, u_test_name)
    else:
        return 'model-{0}-test-{1}'.format(model_name, test_name)

def sd2_run(log_prefix, config_minim, tol, converged, max_iter=1000, max_cell_vec_change_ratio=3.0, exception_if_invalid_config = None):
    traj = []
    x = config_minim.get_positions()
    # x_old = 0.0
    # grad_f_old = 0.0
    try:
        initial_cell_mag = np.linalg.norm(config_minim.atoms.get_cell(), axis=1)
    except:
        initial_cell_mag = None

    try:
        underlying_atoms = config_minim.atoms
    except:
        underlying_atoms = config_minim

    return_stat = "unconverged"
    for i_minim in range(max_iter):
        if "n_minim_iter" in underlying_atoms.info:
            underlying_atoms.info["n_minim_iter"] += 1
        if initial_cell_mag is not None:
            cur_cell_mag = np.linalg.norm(config_minim.atoms.get_cell(), axis=1)
            if np.max(cur_cell_mag/initial_cell_mag) > max_cell_vec_change_ratio:
                print "SD2: i {} bad lattice constant".format(i_minim)
                sys.stdout.flush()
                return_stat="failed"
                break

        config_minim.set_positions(x)
        if exception_if_invalid_config is not None:
            exception_if_invalid_config(config_minim)
        grad_f = - config_minim.get_forces()
        E = config_minim.get_potential_energy()
        done = converged(i_minim)

        try: # ExpCellFilter
            traj.append(config_minim.atoms.copy())
        except:
            traj.append(config_minim.copy())

        if done:
            print log_prefix,"SD2: i {} E {} {} {}".format(i_minim, E, config_minim.log_message, done)
            sys.stdout.flush()
            return_stat="converged"
            break

        if i_minim == 0:
            alpha = 1.0e-4
        else:
            alpha_num = np.sum((x-x_old)*(grad_f-grad_f_old))
            if alpha_num < 0.0:
                alpha = 1.0e-2
            else:
                alpha = alpha_num / np.sum((grad_f-grad_f_old)**2)

        print log_prefix,"SD2: i {} E {} {} alpha {} {}".format(i_minim, E, config_minim.log_message, alpha, done)
        sys.stdout.flush()

        x_old = x.copy()
        grad_f_old = grad_f.copy()
        x -= alpha*grad_f

    return (traj, return_stat)

def f_conv_crit_sq(forces):
    return (forces**2).sum(axis=1).max()
def s_conv_crit_sq(stress):
    return (stress**2).max()

def sd2_converged(minim_ind, atoms, fmax, smax=None):
    forces = atoms.get_forces()

    if isinstance(atoms, ExpCellFilter):
        fmax_sq = f_conv_crit_sq(forces[:len(atoms)-3])
        smax_sq = s_conv_crit_sq(forces[len(atoms)-3:])
        if smax is None:
            smax = fmax
        atoms.log_message = "f {} s {} ".format(np.sqrt(fmax_sq), np.sqrt(smax_sq))
        f_conv = (fmax_sq < fmax**2 and smax_sq < smax**2)
    else:
        fmax_sq = f_conv_crit_sq(forces)
        atoms.log_message = "f {} ".format(np.sqrt(fmax_sq))
        f_conv = fmax_sq < fmax**2

    return f_conv


def relax_config(atoms, relax_pos, relax_cell, tol=1e-3, method='lbfgs', max_steps=200, traj_file=None, constant_volume=False,
    refine_symmetry_tol=None, keep_symmetry=False, strain_mask = None, config_label=None, from_base_model=False, save_config=False,
    **kwargs):

    # get from base model if requested
    import model
    if from_base_model:
        if config_label is None:
            raise ValueError('from_base_model is set but no config_label provided')
        try:
            base_run_file = os.path.join('..',base_run_root,base_run_root+'-'+config_label+'-relaxed.xyz')
            atoms_in = read(base_run_file, format='extxyz')
            # set positions from atoms_in rescaling to match current cell
            saved_cell = atoms.get_cell().copy()
            atoms.set_cell(atoms_in.get_cell())
            atoms.set_positions(atoms_in.get_positions())
            atoms.set_cell(saved_cell, scale_atoms=True)
            print "relax_config read config from ",base_run_file
        except:
            try:
                print "relax_config failed to read base run config from ",base_run_root+'-'+config_label+'-relaxed.xyz'
            except:
                print "relax_config failed to determined base_run_root"

    #if refine_symmetry_tol is not None:
    #    symmetrize.refine(atoms, refine_symmetry_tol)
    #if keep_symmetry:
    #    atoms.set_calculator(symmetrize.SymmetrizedCalculator(model.calculator, atoms))
    #else:
    atoms.set_calculator(model.calculator)

    if method == 'lbfgs' or method == 'sd2':
        if 'move_mask' in atoms.arrays:
            atoms.set_constraint(FixAtoms(np.where(atoms.arrays['move_mask'] == 0)[0]))
        if relax_cell:
            atoms_cell = ExpCellFilter(atoms, mask=strain_mask, constant_volume=constant_volume)
        else:
            atoms_cell = atoms
        atoms.info["n_minim_iter"] = 0
        if method == 'sd2':
            (traj, run_stat) = sd2_run("", atoms_cell, tol, lambda i : sd2_converged(i, atoms_cell, tol), max_steps)
            if traj_file is not None:
                write(traj_file, traj)
        else:
            # precon="Exp" specified to resolve an error with the lbfgs not optimising
            opt = PreconLBFGS(atoms_cell, precon="Exp", **kwargs)
            if traj_file is not None:
                traj = open(traj_file, "w")
                def write_trajectory():
                    if "n_minim_iter" in atoms.info:
                        atoms.info["n_minim_iter"] += 1
                    write(traj, atoms, format='extxyz')
                opt.attach(write_trajectory)
    elif method == 'cg_n':
        if strain_mask is not None:
            raise(Exception("strain_mask not supported with method='cg_n'"))
        atoms.info['Minim_Constant_Volume'] = constant_volume
        opt = Minim(atoms, relax_positions=relax_pos, relax_cell=relax_cell, method='cg_n')
    else:
        raise ValueError('unknown method %s!' % method)

    if method != 'sd2':
        opt.run(tol, max_steps)

    if refine_symmetry_tol is not None:
        symmetrize.check(atoms, refine_symmetry_tol)
    symmetrize.check(atoms, 1.0e-6)

    # in case we had a trajectory saved
    try:
        traj.close()
    except:
        pass

    if save_config:
        if config_label is None:
            raise ValueError('save_config is set but no config_label provided')
        write(run_root+'-'+config_label+'-relaxed.xyz', atoms, format='extxyz')

    if keep_symmetry:
        atoms.set_calculator(model.calculator)

    return atoms


def evaluate(atoms, do_energy=True, do_forces=True, do_stress=True):
    import model
    atoms.set_calculator(model.calculator)

    energy = None
    if do_energy:
        energy = atoms.get_potential_energy()

    forces = None
    if do_forces:
        forces = atoms.get_forces()

    stress = None
    if do_stress:
        stress = atoms.get_stress()

    spc = SinglePointCalculator(atoms,
                                energy=energy,
                                forces=forces,
                                stress=stress)
    atoms.set_calculator(spc)
    return atoms

def robust_minim_cell_pos(atoms, final_tol, label="robust_minim", max_sd2_iter=50, sd2_tol=1.0, max_lbfgs_iter=20, max_n_lbfgs=50, keep_symmetry=True):
    import model

    # do each minim at fixed cell-dependent model params (e.g. k-point mesh)
    if hasattr(model, "fix_cell_dependence"):
        model.fix_cell_dependence(atoms)
    relax_config(atoms, relax_pos=True, relax_cell=True, tol=sd2_tol, max_steps=max_sd2_iter,
        traj_file="%s_sd2_traj.extxyz" % label, method='sd2', keep_symmetry=keep_symmetry, config_label=label )

    done=False
    i_iter = 0
    while not done and i_iter < max_n_lbfgs:
        try:
            if hasattr(model, "fix_cell_dependence"):
                model.fix_cell_dependence(atoms)
            relax_config(atoms, relax_pos=True, relax_cell=True, tol=final_tol, max_steps=max_lbfgs_iter,
                traj_file="%s_lbfgs_traj.%02d.extxyz" % (label, i_iter), method='lbfgs', keep_symmetry=keep_symmetry, config_label=label )
            done = (atoms.info["n_minim_iter"] < max_lbfgs_iter)
            print "robust_minim relax_configs LBFGS finished in ",atoms.info["n_minim_iter"],"iters, max", max_lbfgs_iter
        except:
            print "robust_minim relax_configs LBFGS failed, trying again"
        i_iter += 1

    # Undo fixed cell dependence. Hopefully no one is using robust_minim as part of a
    # more complex process that is doing its own fix_cell_depdence()
    if hasattr(model, "fix_cell_dependence"):
        model.fix_cell_dependence()

def rescale_to_relaxed_bulk(supercell):
    # read bulk
    bulk_struct_test=supercell.info['bulk_struct_test']
    bulk_model_test_relaxed = os.path.join('..',model_test_root(u_test_name=bulk_struct_test)+"-relaxed.xyz")

    try:
        bulk = read(bulk_model_test_relaxed, format='extxyz')
    except:
        sys.stderr.write("Failed to read relaxed bulk '{}', perhaps bulk test hasn't been run yet\n".format(bulk_model_test_relaxed))
        sys.exit(1)

    # rescale supercell cell
    supercell_a1_lattice = supercell.info['supercell_a1_in_bulk_lattice_coords']
    bulk_lattice = bulk.get_cell()
    supercell_a1_in_bulk = np.dot(supercell_a1_lattice,bulk_lattice)
    cell_ratio = np.linalg.norm(supercell_a1_in_bulk) / np.linalg.norm(supercell.get_cell()[0,:])
    if 'supercell_a2_in_lattice_coords' in supercell.info:
        raise ValueError('anisotropic rescaling of supercellace cell not implemented')
    if 'supercell_a3_in_lattice_coords' in supercell.info:
        raise ValueError('anisotropic rescaling of supercellace cell not implemented')

    supercell.set_cell(supercell.get_cell()*cell_ratio, scale_atoms=True)

    return bulk
