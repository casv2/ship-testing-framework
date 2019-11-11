import MD
from ase.lattice.cubic import BodyCenteredCubic

at = BodyCenteredCubic("Ti", latticeconstant=3.32)

#dt is in femtoseconds, T in Kelvin

properties = MD.MD_run(at, N=3, Tmin=1000, Tmax=1000, dt=1.0, ramps=1, MDsteps=1000)