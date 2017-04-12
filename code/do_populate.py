"""Code for generating a population of FRBs"""

import math
import random

import distributions as dis
import galacticops as go
from population import Population
from source import Source


def generate(n_gen,
             cosmology=True,
             cosmo_pars=[69.6, 0.286, 0.714],
             electron_model='ne2001',
             emission_pars=[10e6, 10e9],
             lum_dist_pars=[1e40, 1e50, 1],
             name=None,
             pulse=[0.1,5],
             si_pars=[1, 1],
             z_max=2.5):

    """Generate a population of FRB sources

    Args:
        n_gen (int): Number of FRB sources to generate
        cosmology (bool, optional): Whether to use cosmology in all
            calculations. Defaults to True.
        cosmo_pars (list, optional): Three values, the first being the Hubble
            constant, the second the density parameter Omega_m and the third
            being the cosmological constant Omega_Lambda (referred to as W_m
            in the rest of the code). These parameters default to those
            determined with Planck [69.6, 0.286, 0.714]
        electron_model (str, optional): Model for the free electron density in
            the Milky Way. Defaults to 'ne2001'
        emission_pars (list, optional): The minimum and maximum frequency [Hz]
            between which FRB sources should emit the given bolometric
            luminosity. Defaults to [10e6,10e9]
        lum_dist_pars (list, optional): Bolometric luminosity distribution
            parameters being: the minimum luminosity [erg/s], the maximum
            luminosity [erg/s] and the powerlaw index of the distribution.
            Defaults to [1e50, 1e90, 1]
        name (str, optional): Name to be given to the population. Defaults to
            'initial'
        pulse (str, optional): Values between which the intrinsic pulse width
            should be [ms]. Defaults to [0.5, 5]
        si_pars (list, optional): Spectral index parameters, being the mean
            index and the standard deviation thereof. Defaults to [1, 1]
        z_max (float, optional): The maximum redshift out to which to
            distribute FRBs

    Returns:
        pop (Population): A population of generated sources
    """

    # Check input
    if type(n_gen) != int:
        m = 'Please ensure the number of generated sources is an integer'
        raise ValueError(m)

    if n_gen < 1:
        m = 'Please ensure the number of generated sources is > 0'
        raise ValueError(m)

    if type(cosmology) != bool:
        raise ValueError('Please ensure cosmology is a boolean')

    if not all(isinstance(par, (float, int)) for par in cosmo_pars):
        m = 'Please ensure all cosmology parameters are floats or integeters'
        raise ValueError(m)

    if len(cosmo_pars) != 3:
        m = 'Please ensure there are three cosmology parameters'
        raise ValueError(m)

    if electron_model not in ['ne2001']:
        m = 'Unsupported electron model: {}'.format(electron_model)
        raise ValueError(m)

    if not all(isinstance(par, (float, int)) for par in emission_pars):
        m = 'Please ensure all emission parameters are floats or integeters'
        raise ValueError(m)

    if len(emission_pars) != 2:
        m = 'Please ensure there are two emission parameters'
        raise ValueError(m)

    if not all(isinstance(par, (float, int)) for par in lum_dist_pars):
        m = 'Please ensure all luminosity distribution parameters are '
        m += 'floats or integeters'
        raise ValueError(m)

    if len(lum_dist_pars) != 3:
        m = 'Please ensure there are three luminosity distribution parameters'
        raise ValueError(m)

    if not all(isinstance(par, (float, int)) for par in pulse):
        m = 'Please ensure all pulse parameters are '
        m += 'floats or integeters'
        raise ValueError(m)

    if len(pulse) != 2:
        m = 'Please ensure there are two pulse parameters'
        raise ValueError(m)

    if not name:
        name = 'Initial'

    if type(name) != str:
        m = 'Please provide a string as input for the name of the population'
        raise ValueError(m)

    if not all(isinstance(par, (float, int)) for par in si_pars):
        m = 'Please ensure all spectral index parameters are '
        m += 'floats or integers'
        raise ValueError(m)

    if len(si_pars) != 2:
        m = 'Please ensure there are two spectral index parameters'
        raise ValueError(m)

    if not isinstance(z_max, (float, int)):
        m = 'Please ensure the maximum redshift is given as a float or integer'
        raise ValueError(m)

    # Set up population
    pop = Population()
    pop.name = name
    pop.n_gen = n_gen
    pop.electron_model = electron_model
    pop.cosmology = cosmology
    pop.H_0 = cosmo_pars[0]
    pop.W_m = cosmo_pars[1]
    pop.W_v = cosmo_pars[2]
    pop.z_max = z_max
    pop.v_max = go.z_to_v(z_max)
    pop.lum_min = lum_dist_pars[0]
    pop.lum_max = lum_dist_pars[1]
    pop.lum_pow = lum_dist_pars[2]
    pop.w_min = pulse[0]
    pop.w_max = pulse[1]
    pop.f_min = emission_pars[0]
    pop.f_max = emission_pars[1]
    pop.si_mean = si_pars[0]
    pop.si_sigma = si_pars[1]

    # Create a comoving distance to redshift lookup table
    ds, zs = go.dist_lookup(cosmology=pop.cosmology,
                            H_0=pop.H_0,
                            W_m=pop.W_m,
                            W_v=pop.W_v,
                            z_max=pop.z_max
                            )

    while pop.n_srcs < pop.n_gen:

        # Initialise
        src = Source()

        # Add random directional coordinates
        src.gb = math.degrees(math.asin(random.random()))
        if random.random() < 0.5:
            src.gb *= -1
        src.gl = random.random() * 360.0

        # Calculate comoving distance [Gpc]
        src.dist = (pop.v_max * random.random() * (3/(4*math.pi)))**(1/3)
        # Calculate redshift
        src.z = go.interpolate_z(src.dist, ds, zs, H_0=pop.H_0)
        # Convert into galactic coordinates
        src.gx, src.gy, src.gz = go.lb_to_xyz(src.gl, src.gb, src.dist)

        # Dispersion measure of the Milky Way
        src.dm_mw = go.ne2001_dist_to_dm(src.dist, src.gl, src.gb)
        # Dispersion measure of the intergalactic medium
        src.dm_igm = go.ioka_dm_igm(src.z)
        # Dispersion measure of the host
        src.dm_host = 100.  # Thornton et al. (2013)
        # Total dispersion measure
        src.dm = src.dm_mw + src.dm_igm + src.dm_host

        # Give an random intrinsic pulse width [ms]
        src.w_int = go.redshift_pulse(z=src.z,
                                      w_min=pop.w_min,
                                      w_max=pop.w_max)

        # Add bolometric luminosity [erg/s]
        src.lum_bol = dis.powerlaw(pop.lum_min, pop.lum_max, pop.lum_pow)

        # Add spectral index
        src.si = -1.4
        # src.si = random.gauss(pop.si_mean, pop.si_sigma)

        # Add to population
        pop.sources.append(src)
        pop.n_srcs += 1

    return pop