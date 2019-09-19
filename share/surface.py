import ase.io, os
from utilities import relax_config, model_test_root, run_root, rescale_to_relaxed_bulk, evaluate
import numpy as np
import sys

# the current 
import model 

def do_symmetric_surface(test_dir):
    surf = ase.io.read(test_dir+"/surface.xyz", format="extxyz")

    bulk = rescale_to_relaxed_bulk(surf)
    evaluate(bulk)

    print "got relaxed bulk cell ", bulk.get_cell()
    print "got rescaled surf cell ", surf.get_cell()

    # relax surface system
    tol = 1.0e-2
    surf = relax_config(surf, relax_pos=True, relax_cell=False, tol=tol, traj_file=None, config_label="surface", from_base_model=True, save_config=True)

    ase.io.write(os.path.join("..",run_root+"-relaxed.xyz"),  surf, format='extxyz')

    # check stoichiometry and number of bulk cell energies to subtract
    surf_Zs = surf.get_atomic_numbers()
    bulk_Zs = bulk.get_atomic_numbers()
    Z0 = bulk_Zs[0]
    n_bulk_cells = float(sum(surf_Zs == Z0))/float(sum(bulk_Zs == Z0))
    if len(set(bulk_Zs)) == 1:
        n_dmu = None
    else:
        n_dmu = {}
        for Z in set(bulk_Zs):
            n_dmu[Z] = n_bulk_cells*sum(bulk_Zs == Z) - sum(surf_Zs == Z)

    # calculate surface energy
    area = np.linalg.norm(np.cross(surf.get_cell()[0,:],surf.get_cell()[1,:]))

    print "got surface cell potential energy", surf.get_potential_energy()
    print "got bulk potential energy",bulk.get_potential_energy()*n_bulk_cells
    print "got area",area

    return { "bulk_struct_test" : surf.info["bulk_struct_test"],  "Ef" : (surf.get_potential_energy() - bulk.get_potential_energy()*n_bulk_cells)/(2.0*area), "dmu" : n_dmu, 'filename' : run_root+"-relaxed.xyz" }

def surface_decohesion_100(bulk):

    bulk.set_calculator(model.calculator)

    # use one of the routines from utilities module to relax the initial
    # unit cell and atomic positions
    tol = 1e-2
    bulk = relax_config(bulk, relax_pos=True, relax_cell=True, tol=tol, traj_file=None, config_label="surface", from_base_model=True, save_config=True)

    # set up supercell
    bulk *= (5, 1, 1)

    def surface_energy(bulk, opening):
        Nat = bulk.get_number_of_atoms()

        # relax atom positions, holding cell fixed
        # vac = relax_atoms(vac, fmax=fmax)

        # compute surface formation energy as difference of bulk and expanded cell
        ebulk = bulk.get_potential_energy()
        print 'bulk cell energy', ebulk

        bulk.cell[0,:] += [opening,0.0,0.0]
        eexp  = bulk.get_potential_energy()

        print 'expanded cell energy', eexp
        e_form = (eexp - ebulk) / (bulk.cell[1,1]*bulk.cell[2,2])
        print 'unrelaxed 100 surface formation energy', e_form
        return e_form

    # dictionary of computed properties - this is output of this test, to
    #   be compared with other models
    n_steps = 35
    max_opening = 3.5

    openings = []
    es = []
    for i in range(n_steps + 1):
        opening = float(i)/float(n_steps)*max_opening
        openings.append(opening)
        bulk_copy = bulk.copy()
        bulk_copy.set_calculator(model.calculator)
        es.append(surface_energy(bulk_copy, opening))

    print "openings ", openings
    print "es ", es
    from scipy import interpolate
    spline = interpolate.splrep(openings, es, s=0)
    stresses = [x for x in interpolate.splev(openings, spline, der=1)]

    print "stresses ", stresses

    return {'surface_decohesion_unrelaxed_opening': openings, 'surface_decohesion_unrelaxed_energy' : es, 'surface_decohesion_unrelaxed_stress' : stresses}

def surface_decohesion_110(bulk):

    bulk.set_calculator(model.calculator)

    # use one of the routines from utilities module to relax the initial
    # unit cell and atomic positions
    tol = 1e-2
    bulk = relax_config(bulk, relax_pos=True, relax_cell=True, tol=tol, traj_file=None, config_label="surface", from_base_model=True, save_config=True)

    # set up supercell
    bulk *= (1, 1, 5)

    def surface_energy(bulk, z_offset, opening):
        Nat = bulk.get_number_of_atoms()

        # shift so cut is through shuffle plane
        bulk.positions[:,2] += z_offset
        bulk.wrap()

        # relax atom positions, holding cell fixed
        # vac = relax_atoms(vac, fmax=fmax)

        # compute surface formation energy as difference of bulk and expanded cell
        ebulk = bulk.get_potential_energy()
        print 'bulk cell energy', ebulk

        bulk.cell[2,2] *= (np.abs(bulk.cell[2,2])+opening)/np.abs(bulk.cell[2,2])
        eexp  = bulk.get_potential_energy()

        ase.io.write(sys.stdout, bulk, format='extxyz')

        print 'expanded cell energy', eexp
        e_form = 0.5*(eexp - ebulk) / np.linalg.norm(np.cross(bulk.cell[0,:],bulk.cell[1,:]))
        print 'unrelaxed 110 surface formation energy', e_form

        return e_form

    # dictionary of computed properties - this is output of this test, to
    #   be compared with other models
    n_steps = 35
    max_opening = 3.5

    openings = []
    es = []
    for i in range(n_steps + 1):
        opening = float(i)/float(n_steps)*max_opening
        openings.append(opening)
        bulk_copy = bulk.copy()
        bulk_copy.set_calculator(model.calculator)
        es.append(surface_energy(bulk_copy, 2.0, opening))

    print "openings ", openings
    print "es ", es
    from scipy import interpolate
    spline = interpolate.splrep(openings, es, s=0)
    stresses = [x for x in interpolate.splev(openings, spline, der=1)]

    print "stresses ", stresses

    return {'surface_decohesion_unrelaxed_opening': openings, 'surface_decohesion_unrelaxed_energy' : es, 'surface_decohesion_unrelaxed_stress' : stresses}

def surface_decohesion_111(bulk):

    bulk.set_calculator(model.calculator)

    # use one of the routines from utilities module to relax the initial
    # unit cell and atomic positions
    tol = 1e-2
    bulk = relax_config(bulk, relax_pos=True, relax_cell=True, tol=tol, traj_file=None, config_label="surface", from_base_model=True, save_config=True)

    # set up supercell
    bulk *= (1, 1, 5)

    def surface_energy(bulk, z_offset, opening):
        Nat = bulk.get_number_of_atoms()

        # shift so cut is through shuffle plane
        bulk.positions[:,2] += z_offset
        bulk.wrap()

        # relax atom positions, holding cell fixed
        # vac = relax_atoms(vac, fmax=fmax)

        # compute surface formation energy as difference of bulk and expanded cell
        ebulk = bulk.get_potential_energy()
        print 'bulk cell energy', ebulk

        bulk.cell[2,:] += [0.0,0.0,opening]
        eexp  = bulk.get_potential_energy()

        ase.io.write(sys.stdout, bulk, format='extxyz')

        print 'expanded cell energy', eexp
        e_form = 0.5*(eexp - ebulk) / np.linalg.norm(np.cross(bulk.cell[0,:],bulk.cell[1,:]))
        print 'unrelaxed 111 surface formation energy', e_form

        return e_form

    # dictionary of computed properties - this is output of this test, to
    #   be compared with other models
    n_steps = 35
    max_opening = 3.5

    openings = []
    es = []
    for i in range(n_steps + 1):
        opening = float(i)/float(n_steps)*max_opening
        openings.append(opening)
        bulk_copy = bulk.copy()
        bulk_copy.set_calculator(model.calculator)
        es.append(surface_energy(bulk_copy, 2.0, opening))

    print "openings ", openings
    print "es ", es
    from scipy import interpolate
    spline = interpolate.splrep(openings, es, s=0)
    stresses = [x for x in interpolate.splev(openings, spline, der=1)]

    print "stresses ", stresses

    return {'surface_decohesion_unrelaxed_opening': openings, 'surface_decohesion_unrelaxed_energy' : es, 'surface_decohesion_unrelaxed_stress' : stresses}


def surface_decohesion(bulk):

    bulk.set_calculator(model.calculator)

    # use one of the routines from utilities module to relax the initial
    # unit cell and atomic positions
    tol = 1e-2
    bulk = relax_config(bulk, relax_pos=True, relax_cell=True, tol=tol, traj_file=None, config_label="surface", from_base_model=True, save_config=True)

    # set up supercell
    bulk *= (5, 1, 1)

    def surface_energy(bulk, opening):
        Nat = bulk.get_number_of_atoms()

        # relax atom positions, holding cell fixed
        # vac = relax_atoms(vac, fmax=fmax)

        # compute surface formation energy as difference of bulk and expanded cell
        ebulk = bulk.get_potential_energy()
        print 'bulk cell energy', ebulk

        bulk.cell[0,:] += [opening,0.0,0.0]
        eexp  = bulk.get_potential_energy()

        print 'expanded cell energy', eexp
        e_form = (eexp - ebulk) / (bulk.cell[1,1]*bulk.cell[2,2])
        print 'unrelaxed 100 surface formation energy', e_form
        return e_form

    # dictionary of computed properties - this is output of this test, to
    #   be compared with other models
    n_steps = 35
    max_opening = 3.5

    openings = []
    es = []
    for i in range(n_steps + 1):
        opening = float(i)/float(n_steps)*max_opening
        openings.append(opening)
        bulk_copy = bulk.copy()
        bulk_copy.set_calculator(model.calculator)
        es.append(surface_energy(bulk_copy, opening))

    print "openings ", openings
    print "es ", es
    from scipy import interpolate
    spline = interpolate.splrep(openings, es, s=0)
    stresses = [x for x in interpolate.splev(openings, spline, der=1)]

    print "stresses ", stresses

    return {'surface_decohesion_unrelaxed_opening': openings, 'surface_decohesion_unrelaxed_energy' : es, 'surface_decohesion_unrelaxed_stress' : stresses}



def surface_decohesion_old(bulk):
    #bulk = ase.io.read(test_dir+"/bulk.xyz", format="extxyz")

    bulk.set_calculator(model.calculator)

    def surface_energy(bulk, z_offset, opening):
            Nat = bulk.get_number_of_atoms()
            # shift so cut is through shuffle plane
            bulk.positions[:,2] += z_offset
            bulk.wrap()

            ebulk = bulk.get_potential_energy()
            print 'bulk cell energy', ebulk

            bulk.cell[2,2] *= (np.abs(bulk.cell[2,2])+opening)/np.abs(bulk.cell[2,2])
            eexp  = bulk.get_potential_energy()

            ase.io.write(sys.stdout, bulk, format='extxyz')

            print 'expanded cell energy', eexp
            e_form = 0.5*(eexp - ebulk) / np.linalg.norm(np.cross(bulk.cell[0,:],bulk.cell[1,:]))
            print 'unrelaxed 110 surface formation energy', e_form
            return e_form

    n_steps = 7
    max_opening = 3.0

    openings = []
    es = []
    for i in range(n_steps + 1):
        opening = float(i)/float(n_steps)*max_opening
        openings.append(opening)
        bulk_copy = bulk.copy()
        bulk_copy.set_calculator(model.calculator)
        es.append(surface_energy(bulk_copy, 2.0, opening))

    print "openings ", openings
    print "es ", es
    from scipy import interpolate
    spline = interpolate.splrep(openings, es, s=0)
    stresses = [x for x in interpolate.splev(openings, spline, der=1)]

    print "stresses ", stresses
    
    return {'surface_decohesion_unrelaxed_opening': openings, 'surface_decohesion_unrelaxed_energy' : es, 'surface_decohesion_unrelaxed_stress' : stresses}





