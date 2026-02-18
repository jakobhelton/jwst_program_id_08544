###

# Import necessary miscellaneous modules

import os
import sys
import glob
import json
import time

# Imports necessary science modules

import numpy as np
import pandas as pd
import seaborn as sns

import astropy, matplotlib, scipy, sedpy, corner

from astropy.io import fits
from astropy.table import Table
from astropy.cosmology import FlatLambdaCDM
from astropy import units as u

import matplotlib.pyplot as plt

from matplotlib.ticker import AutoMinorLocator, MaxNLocator

matplotlib.rcParams['text.usetex'] = True

colors_8 = sns.color_palette('husl', 8)
colors_4 = sns.color_palette('husl', 4)
colors_3 = sns.color_palette('husl', 3)
colors_2 = sns.color_palette('husl', 2)
colors_1 = sns.color_palette('husl', 1)

# Defines the standard cosmology from Planck18
# Reference: https://www.scixplorer.org/abs/2020A&A...641A...6P/abstract

cosmo = FlatLambdaCDM(H0=67.4, Om0=0.315, Tcmb0=2.726)

# Defines sedpy filters for determining rest-frame magnitudes

bessell_U = sedpy.observate.Filter(kname='bessell_U')
bessell_B = sedpy.observate.Filter(kname='bessell_B')
bessell_V = sedpy.observate.Filter(kname='bessell_V')
bessell_R = sedpy.observate.Filter(kname='bessell_R')
bessell_I = sedpy.observate.Filter(kname='bessell_I')
twomass_J = sedpy.observate.Filter(kname='twomass_J')
twomass_H = sedpy.observate.Filter(kname='twomass_H')
twomass_K = sedpy.observate.Filter(kname='twomass_Ks')

# Defines filename for the dispersion profile of NIRSpec/PRISM

dispersion_profile_filename = 'jwst_nirspec_prism_disp.fits'

# Imports fsps, Prospector v2, and necessary Prospector functions

import fsps

import prospect as prosp

from prospect.fitting import fit_model, lnprobfn

from prospect.sources import CSPSpecBasis, FastStepBasis

from prospect.observation import Photometry, Spectrum, Lines, PolyOptCal

from prospect.models import priors, transforms, SpecModel
from prospect.models.templates import TemplateLibrary

from prospect.likelihood import NoiseModel1D
from prospect.likelihood.kernels import Uncorrelated

from prospect.io import write_results as writer
from prospect.io import read_results as reader

from prospect.plotting.corner import quantile

print(prosp.__path__)

# More information about PolySpectrum is at...
# Section: Instrumental Response & Spectrophotometric Calibration
# Link: https://github.com/bd-j/prospector/blob/ea35902880c8a51f0093fea3bc8885a20ce16ef1/doc/spectra.rst

class PolySpectrum(PolyOptCal, Spectrum):

    pass

###

# Testing fsps and Prospector v2 imports

print(f'Prospector pathname: {prosp.__path__}')
print(f'Prospector version: {prosp.__version__}')
print(f'fsps version: {fsps.__version__}')
print('All imports are successful!')

StellarPopulations = fsps.StellarPopulation()

print(StellarPopulations.libraries)

sps_CSPSpecBasis = CSPSpecBasis(zcontinuous=1)
sps_FastStepBasis = FastStepBasis(zcontinuous=1)

###

# General model building function for most default types of SFH and IMF
# Defines and builds model based on the methodology of Carniani et al. (2025)
# Relevant Reference: https://www.scixplorer.org/abs/2025A&A...696A..87C/abstract

def build_model_Prospector(observations, sfh_type, zred, zerr=None, zbirth=20.0, zmax=20.0, zmin=0.0, nbins=6, scale=1.0, alpha=0.8, 
    imf_type='Chabrier', imf_lower=0.08, imf_upper=120.0, decouple_metallicity=True, two_component_dust=True, 
    gas_logu=True, escape_fraction=True, damping_wing=True, igm_factor=True, lyman_alpha=True):

    # Creates list of the available sfh_types

    available_sfh_types = ['RisingContinuity', 'BurstyContinuity', 'Continuity', 'Constant', 'DelayedTau']

    # Initialize the model_params dictionary

    model_params = {}

    if 'bursty' in sfh_type.lower() or 'continuity' in sfh_type.lower() or 'rising' in sfh_type.lower():

        model_params.update(TemplateLibrary['continuity_sfh'])

    elif 'constant' in sfh_type.lower() or 'delayed' in sfh_type.lower() or 'tau' in sfh_type.lower():

        model_params.update(TemplateLibrary['parametric_sfh'])

    else:

        raise ValueError(f'The specified sfh_type is invalid (available_sfh_types == {available_sfh_types}).')

    # Changes SFH parameters in the model_params dictionary

    if 'bursty' in sfh_type.lower() or 'continuity' in sfh_type.lower() or 'rising' in sfh_type.lower():

        # Adjust the SFH parameters for non-parametric SFHs

        model_params['sfh']['init'] = 3

        model_params['logmass'] = {
            'name': 'log_stellar_mass_formed', 
            'units': u.M_sun, # logarithmic
            'N': 1, 
            'isfree': True, 
            'init': 8.0, 
            'prior': priors.TopHat(mini=6.0, maxi=10.0), 
        }

        model_params['mass'] = {
            'name': 'stellar_mass_formed', 
            'units': u.M_sun, 
            'N': nbins, 
            'isfree': False, 
            'init': 1e+8, 
            'prior': None, 
            'depends_on': transforms.logsfr_ratios_to_masses, 
        }

        # Adjust age bins for non-parameteric SFHs

        if zbirth is None:

            model_params['zbirth'] = {
                'name': 'birth_redshift_of_the_first_stars', 
                'units': None, # Redshift
                'N': 1, 
                'isfree': False, 
                'init': 20.0, 
                'prior': None, 
                'depends_on': transform_tbirth_to_zbirth, 
            }

            model_params['tbirth'] = {
                'name': 'birth_lookback_time_of_the_first_stars', 
                'units': u.Gyr, 
                'N': 1, 
                'isfree': True, 
                'init': transform_zbirth_to_tbirth(zred, 20.0), 
                'prior': priors.TopHat(mini=transform_zbirth_to_tbirth(zred, 15.0), maxi=transform_zbirth_to_tbirth(zred, 100.0)), 
            }

        else:

            model_params['zbirth'] = {
                'name': 'birth_redshift_of_the_first_stars', 
                'units': None, # Redshift
                'N': 1, 
                'isfree': False, 
                'init': zbirth, 
                'depends_on': transform_tbirth_to_zbirth, 
            }

            model_params['tbirth'] = {
                'name': 'birth_lookback_time_of_the_first_stars', 
                'units': u.Gyr, 
                'N': 1, 
                'isfree': False, 
                'init': transform_zbirth_to_tbirth(zred, zbirth), 
            }

        agebin1, agebin2, agebin3 = np.log10(3e+6), np.log10(1e+7), np.log10(3e+7)

        model_params = adjust_agebins(model_params, sfh_type=sfh_type, zred=zred, zbirth=zbirth, 
            zmax=zmax, zmin=zmin, nbins=nbins, scale=scale, alpha=alpha,
            agebin1=agebin1, agebin2=agebin2, agebin3=agebin3)

    elif 'constant' in sfh_type.lower() or 'delayed' in sfh_type.lower() or 'tau' in sfh_type.lower():

        # Adjust the SFH parameters for parametric SFHs

        model_params['sfh']['init'] = 4

        model_params['mass'] = {
            'name': 'stellar_mass_formed', 
            'units': u.M_sun, 
            'N': 1, 
            'isfree': True, 
            'init': 1e+8, 
            'prior': priors.LogUniform(mini=1e+6, maxi=1e+10), 
        }

        model_params['tage'] = {
            'name': '', 
            'units': u.Gyr, 
            'N': 1, 
            'isfree': True, 
            'init': 1e-2, 
            'prior': priors.LogUniform(mini=1e-3, maxi=transform_zbirth_to_tbirth(zred, zbirth)), 
        }

        # Adjust SFH parameters to only include the constant component

        if 'constant' in sfh_type.lower():

            model_params['tau'] = {
                'name': '', 
                'units': 1.0/u.Gyr, 
                'N': 1, 
                'isfree': False, 
                'init': 1.0, 
            }

            model_params['const'] = {
                'name': 'fraction_of_stars_in_constant_component', 
                'units': None, 
                'N': 1, 
                'isfree': False, 
                'init': 1.0, 
                'prior': None, 
            }

        # Adjust SFH parameters to only include the delayed-tau component

        elif 'delayed' in sfh_type.lower() or 'tau' in sfh_type.lower():

            model_params['tau'] = {
                'name': '', 
                'units': 1.0/u.Gyr, 
                'N': 1, 
                'isfree': True, 
                'init': 1.0, 
                'prior': priors.LogUniform(mini=0.1, maxi=30.0), 
            }

            model_params['const'] = {
                'name': 'fraction_of_stars_in_constant_component', 
                'units': None, 
                'N': 1, 
                'isfree': False, 
                'init': 0.0, 
                'prior': None, 
            }

    model_params['logzsol'] = {
        'name': 'stellar_metallicity', 
        'units': 'solar_metallicity', 
        'N': 1, 
        'isfree': True, 
        'init': -1.0, 
        'prior': priors.TopHat(mini=-2.0, maxi=0.0), 
    }

    # Change redshift parameters in the model_params dictionary

    if zerr is not None:

        model_params['zred']['init'] = zred
        model_params['zred']['isfree'] = True
        model_params['zred']['prior'] = priors.ClippedNormal(mean=zred, sigma=zerr, mini=zmin, maxi=zmax)

    else:

        model_params['zred']['init'] = zred
        model_params['zred']['isfree'] = False
        model_params['zred']['prior'] = priors.TopHat(mini=zmin, maxi=zmax)

    # Change IMF parameters in the model_params dictionary

    if imf_type == 'Dave': model_params['imf_type']['init'] = 4
    elif imf_type == 'Kroupa': model_params['imf_type']['init'] = 2
    elif imf_type == 'Salpeter': model_params['imf_type']['init'] = 0
    elif imf_type == 'Chabrier': model_params['imf_type']['init'] = 1
    elif imf_type == 'vanDokkum': model_params['imf_type']['init'] = 3
    else: raise ValueError('IMF type is invalid.')

    if imf_type == 'vanDokkum':

        model_params['vdmc'] = {
            'name': 'van_dokkum_mass_cutoff', 
            'units': u.M_sun, 
            'N': 1, 
            'isfree': False, 
            'init': 0.08*np.power(1.0+zred, 1.5), 
        }

    model_params['imf_lower_limit'] = {
        'name': 'imf_lower_limit', 
        'units': u.M_sun, 
        'N': 1, 
        'isfree': False, 
        'init': imf_lower, 
    }

    model_params['imf_upper_limit'] = {
        'name': 'imf_upper_limit', 
        'units': u.M_sun, 
        'N': 1, 
        'isfree': False, 
        'init': imf_upper, 
    }

    # Change dust parameters in the model_params dictionary

    # dust_type == 4 is assuming the attenuation curve from Kriek & Conroy (2013)
    # Relevant Reference: https://www.scixplorer.org/abs/2013ApJ...775L..16K/abstract

    # dust_type == 2 is assuming the attenuation curve from Calzetti et al. (2000)
    # Relevant Reference: https://www.scixplorer.org/abs/2000ApJ...533..682C/abstract

    model_params['dust_type']['init'] = 4 

    model_params['dust2'] = {
        'name': 'attenuation_old_stars', 
        'units': u.mag, 
        'N': 1, 
        'isfree': True, 
        'init': 0.0, 
        'prior': priors.TopHat(mini=0.0, maxi=2.0), 
    }

    model_params['dust1'] = {
        'name': 'attenuation_young_stars', 
        'units': u.mag, 
        'N': 1, 
        'isfree': False, 
        'init': 0.0, 
        'prior': None, 
        'depends_on': transforms.dustratio_to_dust1, 
    }

    model_params['dust_ratio'] = {
        'name': 'attenuation_ratio', 
        'units': None, 
        'N': 1, 
        'isfree': two_component_dust, 
        'init': 1.0, 
        'prior': priors.ClippedNormal(mean=1.0, sigma=0.2, mini=0.0, maxi=2.0), 
    }

    model_params['dust_index'] = {
        'name': 'dust_law_slope', 
        'units': None, 
        'N': 1, 
        'isfree': two_component_dust, 
        'init': 0.0, 
        'prior': priors.ClippedNormal(mean=0.0, sigma=0.2, mini=-1.0, maxi=0.4), 
    }

    # Change nebular parameters in model_params dictionary

    model_params.update(TemplateLibrary['nebular'])

    if decouple_metallicity:

        model_params['gas_logz'] = {
            'name': 'nebular_metallicity', 
            'units': 'solar_metallicity', 
            'N': 1, 
            'isfree': True, 
            'init': model_params['logzsol']['init'], 
            'prior': model_params['logzsol']['prior'], 
        }

    else:

        model_params['gas_logz'] = {
            'name': 'nebular_metallicity', 
            'units': 'solar_metallicity', 
            'N': 1, 
            'isfree': False, 
            'init': model_params['logzsol']['init'], 
            'depends_on': transforms.stellar_logzsol, 
        }

    model_params['gas_logu'] = {
        'name': 'ionization_parameter', 
        'units': None, 
        'N': 1, 
        'isfree': gas_logu, 
        'init': -2.0, 
        'prior': priors.TopHat(mini=-4.0, maxi=-1.0), 
    }

    model_params['nebemlineinspec'] = { # This has the added benefit of allowing the fsps calls to be faster!
        'name': 'include_emission_lines_fsps', 
        'units': None, 
        'N': 1, 
        'isfree': False, 
        'init': False, 
    }

    # Ignore the Lyman-alpha emission line (in addition to more energetic lines)

    if not lyman_alpha:

        if '2.0' not in prosp.__version__: 

            model_params['elines_to_ignore'] = {
                'name': 'emission_lines_to_ignore', 
                'N': 1, 
                'isfree': False, 
                'init': ['Ly alpha 1216'], # Prospector v1.4
            }

        else: 

            model_params['elines_to_ignore'] = {
                'name': 'emission_lines_to_ignore', 
                'N': 1, 
                'isfree': False, 
                'init': ['Ly-7 926', 'Ly-6 930', 'Ly-5 937', 'Ly-delta 949.749A', 'Ly-gamma 972', 'Ly-beta 1025', 
                    'He II 1084.94A', 'He II 1215.13A', 'Ly-alpha 1215'], # Prospector v2.0
            }

    # Change damping wing and IGM parameters in model_params dictionary

    if damping_wing:

        model_params['dla_logNh'] = {
            'name': 'damping_wing_column_density', 
            'units': 1.0/np.square(u.cm), 
            'N': 1, 
            'isfree': True, 
            'init': 21.0, 
            'prior': priors.TopHat(mini=17.0, maxi=25.0), 
        }

        model_params['dla_redshift'] = {
            'name': 'damping_wing_redshift', 
            'units': None, 
            'N': 1, 
            'isfree': False, 
            'init': zred, 
            'depends_on': zred_to_dla_redshift, 
        }

        model_params['igm_damping'] = {
            'name': 'damping_wing', 
            'units': None, 
            'N': 1, 
            'isfree': False, 
            'init': True, 
        }

    model_params.update(TemplateLibrary['igm'])

    model_params['igm_factor'] = {
        'name': 'factor_multiply_igm_absorption', 
        'units': None, 
        'N': 1, 
        'isfree': igm_factor, 
        'init': 1.0, 
        'prior': priors.ClippedNormal(mean=1.0, sigma=0.2, mini=0.0, maxi=2.0), 
    }

    # Creates new parameters in model_params dictionary

    if escape_fraction: 

        model_params['frac_obrun'] = {
            'name': 'escape_fraction', 
            'units': None, 
            'N': 1, 
            'isfree': True, 
            'init': 0.0, 
            'prior': priors.ClippedNormal(mean=0.0, sigma=0.5, mini=0.0, maxi=1.0), 
        }

    # Change spectral calibration parameters in model_params dictionary

    if type(observations) is not list: observations = [observations]

    observation_names, observation_kinds = [], []

    for observation in observations:

        observation_names.append(observation.name)
        observation_kinds.append(observation.kind)

    if np.any(np.array(observation_kinds) == 'spectrum'):

        model_params['eline_sigma'] = {
            'name': 'emission_line_velocity_dispersion', 
            'units': u.km/u.s, 
            'N': 1, 
            'isfree': True, 
            'init': 1e+3, 
            'prior': priors.ClippedNormal(mean=1e+3, sigma=1e+2, mini=1e+1, maxi=1e+4), 
        }

        model_params['eline_delta_zred'] = {
            'name': 'emission_line_velocity_dispersion', 
            'units': None, # Redshift
            'N': 1, 
            'isfree': True, 
            'init': 0.0, 
            'prior': priors.TopHat(mini=-1e-1, maxi=+1e-1), 
        }

    if np.any('nirspec' in ', '.join(observation_names).lower()):

        model_params['f_outlier_nirspec'] = {
            'name': 'pixel_outlier_fraction_nirspec', 
            'units': None, 
            'N': 1, 
            'isfree': True, 
            'init': 0.0, 
            'prior': priors.TopHat(mini=0.0, maxi=0.1), 
        }

        model_params['nsigma_outlier_nirspec'] = {
            'name': 'nsigma_outlier_deviation_nirspec', 
            'units': None, 
            'N': 1, 
            'isfree': False, 
            'init': 10.0, 
        }

        model_params['spec_jitter_nirspec'] = {
            'name': 'spectroscopic_noise_inflation_term_nirspec', 
            'units': None, 
            'N': 1, 
            'isfree': True, 
            'init': 1.0, 
            'prior': priors.TopHat(mini=1.0, maxi=np.power(10, 1.0)), 
        }

    if np.any('miri' in ', '.join(observation_names).lower() and 'lrs' in ', '.join(observation_names).lower()):

        model_params['f_outlier_miri_lrs'] = {
            'name': 'pixel_outlier_fraction_miri_lrs', 
            'units': None, 
            'N': 1, 
            'isfree': True, 
            'init': 0.0, 
            'prior': priors.TopHat(mini=0.0, maxi=0.1), 
        }

        model_params['nsigma_outlier_miri_lrs'] = {
            'name': 'nsigma_outlier_deviation_miri_lrs', 
            'units': None, 
            'N': 1, 
            'isfree': False, 
            'init': 10.0, 
        }

        model_params['spec_jitter_miri_lrs'] = {
            'name': 'spectroscopic_noise_inflation_term_miri_lrs', 
            'units': None, 
            'N': 1, 
            'isfree': True, 
            'init': 1.0, 
            'prior': priors.TopHat(mini=1.0, maxi=np.power(10, 1.0)), 
        }

    # Initialize the Prospector model

    model = SpecModel(model_params)

    # Returns the Prospector model

    return model

###

# Defines function for adjusting the non-parametric agebins

def adjust_agebins(model_params, sfh_type, zred, zbirth, zmax=20.0, zmin=0.0, nbins=6, scale=1.0, alpha=0.8, 
    agebin1=np.log10(3e+6), agebin2=np.log10(1e+7), agebin3=np.log10(3e+7)):

    # Defines age bins using the given parameters

    if zbirth is not None:

        agebins = transform_zred_to_agebins(zred=zred, tbirth=transform_zbirth_to_tbirth(zred, zbirth), nbins=nbins, 
            agebin1=agebin1, agebin2=agebin2, agebin3=agebin3)

    else:

        agebins = transform_zred_to_agebins(zred=zred, tbirth=transform_zbirth_to_tbirth(zred, 20.0), nbins=nbins, 
            agebin1=agebin1, agebin2=agebin2, agebin3=agebin3)

    # Defines everything else using the given parameters

    if 'rising' in sfh_type.lower():

        lookback_time = 1e+9*cosmo.lookback_time(zred).value # lookback time at zred
        lookback_time_agebins = lookback_time + np.mean(np.power(10, agebins), axis=1) # lookback time of agebins
        zbins = astropy.cosmology.z_at_value(cosmo.lookback_time, lookback_time_agebins*u.yr) # redshift associate with agebins
        sfr_z = np.exp(-alpha*(zbins - zred))*np.power(1.0 + zbins, 2.5) # baseline sfr in each bin
        baseline_sfr_ratios = np.log10(sfr_z[0:-1]/sfr_z[1::]) # baseline logarithmic sfr ratio

        mean = baseline_sfr_ratios
        scale = scale*np.ones_like(mean)
        degrees_of_freedom = 2.0*np.ones_like(mean)

    elif 'bursty' in sfh_type.lower() or 'continuity' in sfh_type.lower():

        mean = np.zeros(nbins - 1)
        scale = scale*np.ones_like(mean)
        degrees_of_freedom = 2.0*np.ones_like(mean)

    model_params['logsfr_ratios'] = {
        'name': 'non_parametric_logsfr_ratios', 
        'units': None, # logarithmic
        'N': nbins - 1, 
        'isfree': True, 
        'init': mean, 
        'prior': priors.StudentT(mean=mean, scale=scale, df=degrees_of_freedom), 
    }

    model_params['agebins'] = {
        'name': 'non_parametric_sfh_agebins', 
        'units': u.yr, # logarithmic
        'N': nbins, 
        'isfree': False, 
        'init': agebins, 
        'depends_on': transform_zred_to_agebins, 
    }

    # Returns the model parameters

    return model_params

###

# Defines function for determining the non-parametric age bins

def transform_zred_to_agebins(zred, tbirth, nbins=6, agebin1=np.log10(3e+6), agebin2=np.log10(1e+7), agebin3=np.log10(3e+7), 
    **dictionary_for_extras):

    # Defines age bins using the given parameters

    if tbirth.shape is not ():

        tuniv = tbirth[0]

    else:

        tuniv = tbirth

    if nbins < 4:

        raise Exception('Number of bins must be greater than four.')

    elif agebin1 == None or np.log10(1e+9*tuniv) <= agebin1:

        agelims = np.linspace(0.0, np.log10(1e+9*tuniv), nbins+1).tolist()

    elif agebin2 == None or np.log10(1e+9*tuniv) <= agebin2:

        agelims = [0] + np.linspace(agebin1, np.log10(1e+9*tuniv), nbins-0).tolist()

    elif agebin3 == None or np.log10(1e+9*tuniv) <= agebin3:

        agelims = [0, agebin1] + np.linspace(agebin2, np.log10(1e+9*tuniv), nbins-1).tolist()

    else:

        agelims = [0, agebin1, agebin2] + np.linspace(agebin3, np.log10(1e+9*tuniv), nbins-2).tolist()

    # Ensures that the minimum spacing between adjacent age bins is larger than 1 Myr

    if np.amin(np.diff(np.power(10, np.array([agelims[:-1], agelims[1:]])))) < 1e+6:

        agelims = np.log10(np.linspace(0.0, 1e+9*tuniv, nbins+1)).tolist()

    agebins = np.array([agelims[:-1], agelims[1:]])

    return agebins.T

###

# Defines function for determining the value of tbirth from zbirth

def transform_zbirth_to_tbirth(zred, zbirth, **dictionary_for_extras):

    # This is relevant for defining the prior on the birth redshift/time of the first stars
    # We want the prior to be dependent on lookback time rather than redshift, due to their non-linear relation

    tred, tbirth = cosmo.age(zred).value, cosmo.age(zbirth).value

    tlookback = tred - tbirth

    return tlookback

###

# Defines function for determining the value of zbirth from tbirth

def transform_tbirth_to_zbirth(zred, tbirth, **dictionary_for_extras):

    # This is relevant for defining the prior on the birth redshift/time of the first stars
    # We want the prior to be dependent on lookback time rather than redshift, due to their non-linear relation

    tlookback = cosmo.age(zred) - np.amax(tbirth)*u.Myr

    return astropy.cosmology.z_at_value(cosmo.age, tlookback).value
###

# Defines helper function for including damped Lyman-alpha absorption

def zred_to_dla_redshift(zred=None, **extras): 

    return zred

###

# Defines and builds stellar population synthesis object for non-parametric SFHs

def get_stellarPopulationSynthesis_NonParametric():

    # Returns the stellar population synthesis object

    return sps_FastStepBasis

###

# Defines and builds stellar population synthesis object for parametric SFHs

def get_stellarPopulationSynthesis_Parametric():

    # Returns the stellar population synthesis object

    return sps_CSPSpecBasis

###

# Defines function for reading in the observations

def build_observations(filename_spec, filename_phot, index_phot, maximumSNR=20.0, polynomial_order=2):

    # Input Data for Spectrum Observations Object (same units on flux for Photometry Observations Object)
    # resolution : Instrumental resolution at each wavelength point in units of km/s
    # wavelength : The wavelength of each flux measurement, in vacuum Angstroms
    # flux : The flux at each wavelength, in units of maggies

    # Reads in the file containing the photometric observations

    df = pd.read_csv(f'catalogs/{filename_phot}')

    error_indices = np.array([i for i, col in enumerate(df.columns) if '_e_nJy' in col])
    flux_indices = np.array([i for i, col in enumerate(df.columns) if '_f_nJy' in col])
    errors = df.iloc[index_phot][np.array(df.columns.tolist())[error_indices]]
    fluxes = df.iloc[index_phot][np.array(df.columns.tolist())[flux_indices]]

    temp_filterSet = np.array([col[:5] for col in df.columns[flux_indices]])

    filters, flux_phot, uncertainty_phot = [], [], []

    for i, filt in enumerate(temp_filterSet):

        if fluxes.iloc[i] == 0 and np.isnan(errors.iloc[i]): continue

        flux_phot.append(1e-9*fluxes.iloc[i]/3631.0)
        uncertainty_phot.append(1e-9*np.nanmax([errors.iloc[i], fluxes.iloc[i]/maximumSNR])/3631.0) # establish noise floor

        if filt == 'F814W': filters.append(sedpy.observate.Filter(kname=f'ACS_WFC_{filt}'.lower()))
        else: filters.append(sedpy.observate.Filter(kname=f'JWST_{filt}'.lower()))

    for i, wave in enumerate((1.35041648,)):

        w0 = (wave - 0.02793965) # wavelengths in mm
        w1 = (wave + 0.01503805) # wavelengths in mm
        wavelength_ALMA = np.linspace(0.95*w0, 1.05*w1, 1001)
        transmission_ALMA = np.where((wavelength_ALMA > w0) & (wavelength_ALMA < w1), 1.0, 0.0)
        wavelength_ALMA *= 1e+7

        output_ALMA = f'{sedpy.__path__[0]}/data/filters/GSz14_ALMA{i+1}.par'

        np.savetxt(output_ALMA, np.array((wavelength_ALMA, transmission_ALMA)).T)

        filters.append(sedpy.observate.Filter(f'GSz14_ALMA{i+1}', data=(wavelength_ALMA, transmission_ALMA)))
        flux_phot.append(1e-9*0.0/3631.0); uncertainty_phot.append(1e-9*7000.0/3631.0)

    filters, flux_phot, uncertainty_phot = np.array(filters), np.array(flux_phot), np.array(uncertainty_phot)
    wavelengths_phot = np.array([f.wave_effective for f in filters])
    mask_phot = np.zeros_like(wavelengths_phot, dtype=bool)
    mask_phot = ~mask_phot

    if False: flux_phot[flux_phot < 0.0] = 0.0 # Negative values are zeroed out

    # Reads in the file containing the spectroscopic observations

    if type(filename_spec) is not list:

        temp_filename_spec = filename_spec

    else:

        temp_filename_spec = filename_spec[0]

    with fits.open(f'data/{temp_filename_spec}') as hdul:

        extract_5pix, extract_3pix = hdul[1], hdul[2]

        data = extract_3pix.data

        wavelengths_nirspec, flux_nirspec, uncertainty_nirspec = data['WAVELENGTH'], data['FLUX'], data['FLUX_ERR']
        uncertainty_nirspec = np.nanmax([uncertainty_nirspec, flux_nirspec/maximumSNR], axis=0)
        # Fluxes and uncertainties are in units of ergs/s/cm^2/Angstrom
        # Wavelengths are in units of microns
        # Establishes noise floor

        flux_nirspec *= u.erg/u.s/np.square(u.cm)/u.AA
        uncertainty_nirspec *= u.erg/u.s/np.square(u.cm)/u.AA
        wavelengths_nirspec *= u.um; wavelengths_nirspec = wavelengths_nirspec.to(u.AA)

        flux_nirspec *= np.square(wavelengths_nirspec)/astropy.constants.c.to('AA/s')
        uncertainty_nirspec *= np.square(wavelengths_nirspec)/astropy.constants.c.to('AA/s')

        flux_nirspec = flux_nirspec.to('Jy').value/3631.0
        uncertainty_nirspec = uncertainty_nirspec.to('Jy').value/3631.0
        wavelengths_nirspec = wavelengths_nirspec.value

        mask_nirspec = np.zeros_like(wavelengths_nirspec, dtype=bool)
        mask_nirspec = mask_nirspec | ~np.isfinite(flux_nirspec*uncertainty_nirspec)
        mask_nirspec = ~mask_nirspec

        if False: flux_nirspec[flux_nirspec < 0.0] = 0.0 # Negative values are zeroed out

    table = Table.read(f'data/{dispersion_profile_filename}', format='fits')
    wavelengths_resolution, resolution = table['WAVELENGTH'].value, table['R'].value
    wavelengths_resolution *= u.um; wavelengths_resolution = wavelengths_resolution.to(u.AA)
    # Wavelengths are in units of microns, but need to convert to Angstroms

    sigma_resolution_kms = astropy.constants.c.to('km/s').value/np.sqrt(4*np.log(4))/resolution
    # Convert to instrumental resolution at each wavelength point in units of km/s

    sigma_resolution_kms = scipy.interpolate.interp1d(wavelengths_resolution, sigma_resolution_kms, 
        bounds_error=False, fill_value='extrapolate')

    resolution_nirspec = 0.7*sigma_resolution_kms(wavelengths_nirspec)
    # Please do not ask me about this conversion factor... I need to ask the JWST/NIRSpec people about this

    if type(filename_spec) is list and len(filename_spec) > 1:

        try:

            path_sn_ETC = f'{filename_spec[1]}/lineplot/lineplot_sn.fits'
            path_target_ETC = f'{filename_spec[1]}/lineplot/lineplot_target.fits'

            sn_ETC, target_ETC = fits.open(path_sn_ETC), fits.open(path_target_ETC)

            wave_ETC = np.array(target_ETC['TARGET'].data.tolist())[:, 0]
            flux_ETC = np.array(target_ETC['TARGET'].data.tolist())[:, 1]
            error_ETC = np.array(sn_ETC['SN'].data.tolist())[:, 1]
            error_ETC *= flux_ETC

            error_ETC = np.nanmax([error_ETC, flux_ETC/maximumSNR], axis=0)

            flux_miri_lrs = (1e-3*(flux_ETC*u.Jy)/3631.0).value
            uncertainty_miri_lrs = (1e-3*(error_ETC*u.Jy)/3631.0).value
            wavelengths_miri_lrs = ((wave_ETC*u.um).to(u.AA)).value

        except:

            with fits.open(filename_spec[1]) as hdul_x1d:

                try:

                    data_x1d = hdul_x1d['EXTRACT1D'].data

                except:

                    data_x1d = hdul_x1d['COMBINE1D'].data

                column_names = data_x1d.columns.names
                flux_error_data = data_x1d[np.array(column_names)[np.char.find(column_names, 'ERROR') != -1][0]]
                wavelength_data = data_x1d.field(np.where(np.array(column_names) == 'WAVELENGTH')[0][0])
                flux_data = data_x1d.field(np.where(np.array(column_names) == 'FLUX')[0][0])

                if False:

                    flux_data = np.flip(flux_data)
                    flux_error_data = np.flip(flux_error_data)
                    wavelength_data = np.flip(wavelength_data)

                # Empirical wavelength calibration comes from https://www.scixplorer.org/abs/2024ApJ...977L..32X/abstract

                if False: wavelength_data = -0.0864 + 1.0223*np.power(wavelength_data, 1) - 0.0014*np.power(wavelength_data, 2)

                condition_miri_lrs = np.logical_and(np.logical_and(4.875 <= wavelength_data, wavelength_data <= 10.375), 
                    np.logical_or(wavelength_data < 8.0, 8.5 < wavelength_data))

                flux_miri_lrs = ((flux_data[condition_miri_lrs]*u.Jy)/3631.0).value
                uncertainty_miri_lrs = ((flux_error_data[condition_miri_lrs]*u.Jy)/3631.0).value
                wavelengths_miri_lrs = ((wavelength_data[condition_miri_lrs]*u.um).to(u.AA)).value

                if False: flux_miri_lrs[flux_miri_lrs < 0.0] = 0.0 # Negative values are zeroed out

        mask_miri_lrs = np.zeros_like(wavelengths_miri_lrs, dtype=bool)
        mask_miri_lrs = mask_miri_lrs | ~np.isfinite(flux_miri_lrs*uncertainty_miri_lrs)
        mask_miri_lrs = ~mask_miri_lrs

        resolution_miri_lrs = -73.1 + 20.0*(wavelengths_miri_lrs*u.AA).to(u.um).value
        # Retrieved resolving power for the MIRI/LRS using the binary BD Gliese 229Bab
        # Relevant Reference: https://www.scixplorer.org/abs/2024ApJ...977L..32X/abstract
        # See Figure C1 in Appendix C: Retrieved Resolving Power and Wavelength Correction

        resolution_miri_lrs = astropy.constants.c.to('km/s').value/np.sqrt(4*np.log(4))/resolution_miri_lrs
        # Convert to instrumental resolution at each wavelength point in units of km/s

    # Includes the emission line and continuum constraints from ALMA

    flux_ALMA = np.atleast_1d((2.75e-19*u.erg/u.s/np.square(u.cm)).value)
    uncertainty_ALMA = np.atleast_1d((0.52e-19*u.erg/u.s/np.square(u.cm)).value)
    wavelengths_ALMA = np.atleast_1d(((1.0 + df.iloc[index_phot]['zSpec'])*88.35771*u.um).to('AA').value)
    line_indices_ALMA = np.atleast_1d(159)

    observed_data_ALMA = Lines(flux=flux_ALMA, unc=uncertainty_ALMA, wavelength=wavelengths_ALMA, resolution=None, 
        mask=np.ones_like(wavelengths_ALMA, dtype=bool), line_ind=line_indices_ALMA, name='ALMA emission line fluxes')

    # Initializes and defines the observed_data dictionary

    jitter_nirspec = Uncorrelated(parnames=['spec_jitter_nirspec'], weight_by='uncertainty')
    noise_nirspec = NoiseModel1D(kernels=[jitter_nirspec], metric_name='uncertainty', 
        frac_out_name='f_outlier_nirspec', nsigma_out_name='nsigma_outlier_nirspec')

    observed_data_phot = Photometry(filters=filters, wavelength=wavelengths_phot, 
        flux=flux_phot, uncertainty=uncertainty_phot, mask=mask_phot, 
        name='JWST/NIRCam + JWST/MIRI photometry (ForcePho)')

    observed_data_nirspec = PolySpectrum(wavelength=wavelengths_nirspec, resolution=resolution_nirspec, 
        flux=flux_nirspec, uncertainty=uncertainty_nirspec, mask=mask_nirspec, noise=noise_nirspec, 
        polynomial_order=polynomial_order, lambda_pad=1e+2, 
        name='JWST/NIRSpec slit spectroscopy (PRISM)')

    observations = [observed_data_nirspec, observed_data_ALMA, observed_data_phot]

    if type(filename_spec) is list and len(filename_spec) > 1:

        jitter_miri_lrs = Uncorrelated(parnames=['spec_jitter_miri_lrs'], weight_by='uncertainty')
        noise_miri_lrs = NoiseModel1D(kernels=[jitter_miri_lrs], metric_name='uncertainty', 
            frac_out_name='f_outlier_miri_lrs', nsigma_out_name='nsigma_outlier_miri_lrs')

        observed_data_miri_lrs = PolySpectrum(wavelength=wavelengths_miri_lrs, resolution=resolution_miri_lrs, 
            flux=flux_miri_lrs, uncertainty=uncertainty_miri_lrs, mask=mask_miri_lrs, noise=noise_miri_lrs, 
            polynomial_order=polynomial_order, lambda_pad=1e+2, 
            name='JWST/MIRI slit spectroscopy (LRS)')

        observations = [observed_data_nirspec, observed_data_miri_lrs, observed_data_ALMA, observed_data_phot]

    for observation in observations: observation.redshift = df.iloc[index_phot]['zSpec']

    # Returns the observed_data dictionary

    return observations

###

# Defines function for making a trace plot from an hfile

def make_trace_plot(hfile, burn_in=1e-2, lw=2, y_value_label=1.03):

    # Reads in posterior properties from the provided Prospector hfile

    result, temp_observations, temp_model = reader.results_from(hfile, dangerous=False)

    # Creates array of labels for the theta vector

    try:

        theta_labels = np.array(result['theta_labels'])

    except:

        temp_theta_labels = np.array(list(result['chain'].dtype.names)); theta_labels = []

        for i, temp_theta_label in enumerate(temp_theta_labels):

            temp_size = result['chain'].dtype[i].shape[0]

            if temp_size == 1:

                theta_labels.append(temp_theta_label)

            else:

                for j in range(temp_size):

                    theta_labels.append(f'{temp_theta_label}_{j+1}')

        theta_labels = np.array(theta_labels)

    chain = np.array([value for sample in result['chain'] for values in list(sample) for value in values.tolist()])
    chain = chain.reshape(len(result['chain']), len(theta_labels))

    if burn_in is not int: burn_in = int(burn_in*chain.shape[0])

    trace = chain

    if trace.ndim == 2:

        trace = trace[None, :]

    trace = trace[slice(None), :]

    lnp = np.atleast_2d(result['lnprobability'])[slice(None), :]
    weights = result.get('weights', None)

    nwalk = trace.shape[0]

    # Defines relevant hyperparameters and creates matplotlib figure

    ndim = len(theta_labels) + 1
    nx = int(np.floor(np.sqrt(ndim)))
    ny = int(np.ceil(ndim/nx))
    sz = np.array([nx, ny])
    factor = 3.00
    lbdim = 0.20*factor
    trdim = 0.20*factor
    whspace = 0.05*factor
    plotdim = factor*sz + factor*(sz - 1)*whspace
    dim = lbdim + plotdim + trdim

    fig, axes = plt.subplots(nx, ny, figsize=(dim[1], dim[0]), sharex=True)

    axes = np.atleast_2d(axes)

    for i in range(ndim - 1):

        ax = axes.flat[i]

        ax.tick_params(axis='both', which='major', direction='out', 
            bottom=True, top=True, left=True, right=True, length=6, width=lw, labelsize=12)
        ax.tick_params(axis='both', which='minor', direction='out', 
            bottom=True, top=True, left=True, right=True, length=4, width=lw, labelsize=12)

        for j in range(nwalk):

            ax.plot(trace[j, burn_in:, i], color='darkgrey', lw=lw, alpha=1.0, zorder=2)

        temp_theta_label = theta_labels[i].replace('_', '\_')

        ax.set_title(fr'$\mathrm{{{temp_theta_label}}}$', y=y_value_label, size=16)

        ax.xaxis.set_major_locator(MaxNLocator(4))
        ax.yaxis.set_major_locator(MaxNLocator(4))

        ax.xaxis.set_minor_locator(AutoMinorLocator(4))
        ax.yaxis.set_minor_locator(AutoMinorLocator(4))

        for axis in ['top','bottom','left','right']: 

            ax.spines[axis].set_linewidth(lw)

    if True:

        ax = axes.flat[ndim-1]

        for j in range(nwalk):

            ax.plot(lnp[j, burn_in:], color='darkgrey', lw=lw, alpha=1.0, zorder=2)

        ax.set_title(r'$\mathrm{logprobability}$', y=y_value_label)

        ax.xaxis.set_major_locator(MaxNLocator(4))
        ax.yaxis.set_major_locator(MaxNLocator(4))

        ax.xaxis.set_minor_locator(AutoMinorLocator(4))
        ax.yaxis.set_minor_locator(AutoMinorLocator(4))

        for axis in ['top','bottom','left','right']: 

            ax.spines[axis].set_linewidth(lw)

        for ax in axes.flat[ndim:]: 

            ax.axis('off')

    [ax.set_xlabel(r'$\mathrm{Number\ of\ Iterations}$', size=16) for ax in axes[-1, :]]

    plt.subplots_adjust(hspace=0.25, wspace=0.25)

    plt.savefig(f'{hfile.replace('.h5', '/TracePlot')}.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'{hfile.replace('.h5', '/TracePlot')}.png', dpi=300, bbox_inches='tight')
    plt.savefig(f'{hfile.replace('.h5', '/TracePlot')}.jpg', dpi=300, bbox_inches='tight')

    plt.show()

###

# Defines function for generating Prospector predictions

def predict_Prospector(model, theta, observations, stellarPopulationSynthesis):

    # Generate the physical model and cache many quantities used for all kinds of predictions

    model.set_parameters(theta)

    model._zred = model.params.get('zred', 0)
    model._wave, model._spec, model._mfrac = stellarPopulationSynthesis.get_galaxy_spectrum(**model.params)
    model._eline_wave, model._eline_lum = stellarPopulationSynthesis.get_galaxy_elines()
    model._library_resolution = getattr(stellarPopulationSynthesis, 
        'spectral_resolution', 0.0) # rest-frame

    model._norm_spec = model._spec*model.flux_norm()

    eline_z = model.params.get('eline_delta_zred', 0.0)
    model._ewave_obs = (1.0 + eline_z + model._zred)*model._eline_wave

    model._ln_eline_penalty = 0
    model._eline_lum_mle = model._eline_lum.copy()
    model._eline_lum_covar = np.diag(np.square(model.params.get('eline_prior_width', 0.0)*model._eline_lum))

    model._smooth_spec = model.losvd_smoothing(model._wave, model._norm_spec)

    model._smooth_spec = model.add_dla(model._wave, model._smooth_spec)
    model._smooth_spec = model.add_damping_wing(model._wave, model._smooth_spec)

    predictions = [model.predict_obs(observation) for observation in observations[::-1]]

    return predictions, model._mfrac

# Defines function for extracting model predictions from the posterior distribution

def extract_model_predictions(model, result, observations, stellarPopulationSynthesis):

    # Loops through the chain to extract photometric and spectroscopic model predictions

    try:

        theta_labels = np.array(result['theta_labels'])

    except:

        temp_theta_labels = np.array(list(result['chain'].dtype.names)); theta_labels = []

        for i, temp_theta_label in enumerate(temp_theta_labels):

            temp_size = result['chain'].dtype[i].shape[0]

            if temp_size == 1:

                theta_labels.append(temp_theta_label)

            else:

                for j in range(temp_size):

                    theta_labels.append(f'{temp_theta_label}_{j+1}')

        theta_labels = np.array(theta_labels)

    array_smoothed_spectrum, array_predictions, array_mfrac = [], [], []
    array_U, array_B, array_V, array_R, array_I, array_J, array_H, array_K = [], [], [], [], [], [], [], []

    for i, theta in enumerate(result['chain']):

        theta = np.array([item for array in result['chain'][i] for item in array])

        if np.logical_not(np.array_equal(theta_labels, model.theta_labels(), equal_nan=False)):

            new_indices = []

            for theta_label in model.theta_labels():

                new_indices.append(np.where(theta_labels == theta_label)[0][0])

            theta = theta[new_indices]

        # predictions, mfrac = model.predict(theta, observations=observations, sps=stellarPopulationSynthesis)
        predictions, mfrac = predict_Prospector(model, theta, observations, stellarPopulationSynthesis)
        predictions = [prediction.tolist() for prediction in predictions]
        smoothed_spectrum = model._smooth_spec

        temp_wavelengths = stellarPopulationSynthesis.wavelengths
        temp_flux = 3631e-23*smoothed_spectrum*(2.998e+18/np.square(temp_wavelengths))

        array_smoothed_spectrum.append(smoothed_spectrum.tolist())
        array_predictions.append(predictions)
        array_mfrac.append(mfrac)

        array_U.append(bessell_U.ab_mag(temp_wavelengths, temp_flux))
        array_B.append(bessell_B.ab_mag(temp_wavelengths, temp_flux))
        array_V.append(bessell_V.ab_mag(temp_wavelengths, temp_flux))
        array_R.append(bessell_R.ab_mag(temp_wavelengths, temp_flux))
        array_I.append(bessell_I.ab_mag(temp_wavelengths, temp_flux))
        array_J.append(twomass_J.ab_mag(temp_wavelengths, temp_flux))
        array_H.append(twomass_H.ab_mag(temp_wavelengths, temp_flux))
        array_K.append(twomass_K.ab_mag(temp_wavelengths, temp_flux))

    U = np.array(array_U)
    B = np.array(array_B)
    V = np.array(array_V)
    R = np.array(array_R)
    I = np.array(array_I)
    J = np.array(array_J)
    H = np.array(array_H)
    K = np.array(array_K)

    mfrac = np.array(array_mfrac, dtype=float)
    predictions = np.array(array_predictions, dtype=object)
    smoothed_spectrum = np.array(array_smoothed_spectrum, dtype=float)

    return U, B, V, R, I, J, H, K, smoothed_spectrum, predictions, mfrac

###

# Defines function for measuring properties of the stellar populations from the Prospector results

def measure_stellar_population_properties(sfh_type, result, chain, theta_labels):

    # Measures properties of the stellar populations for the non-parametric continuity model

    if 'bursty' in sfh_type.lower() or 'continuity' in sfh_type.lower() or 'rising' in sfh_type.lower():

        agebins = np.array(result['model_params']['agebins'])

        sfr_indices = np.array([i for i, label in enumerate(theta_labels) if label[:6] == 'logsfr'])
        logmass = chain[:, np.where(theta_labels == 'logmass')[0][0]]
        logsfr_ratios = chain[:, sfr_indices]

        N = agebins.shape[0]
        ratios = np.power(10, np.clip(logsfr_ratios, -100, +100)).T
        bins = (np.power(10, agebins[:, 1]) - np.power(10, agebins[:, 0]))
        temp_bins = np.array([temp + bins[i - 1] for i, temp in enumerate(bins) if i > 0])
        temp_bins = np.insert(temp_bins, 0, bins[0])
        coeffs = [(1.0/np.prod(ratios[:i, :], axis=0))*(np.prod(bins[1:i+1])/np.prod(bins[:i])) for i in range(N)]
        m1 = np.power(10, logmass)/np.array(coeffs).sum(axis=0)
        masses = m1*np.array(coeffs)
        sfrs = masses.T/bins.T

        age = 0.5*(np.power(10, agebins)[:, 1] + np.power(10, agebins)[:, 0])
        age = np.sum(age*masses.T, axis=1)
        age /= np.power(10, logmass)

        for index, agebin in enumerate(np.unique(agebins.flatten())): 

            if index == 0:

                if agebin >= 7.0:

                    sfr_10Myr = sfrs[:, index]
                    break

                else:

                    temp_agebin = np.power(10, agebin)
                    sfr_10Myr = sfrs[:, index]*(temp_agebin)/1e+7

                if agebin >= 8.0:

                    sfr_100Myr = sfrs[:, index]
                    break

                else:

                    temp_agebin = np.power(10, agebin)
                    sfr_100Myr = sfrs[:, index]*(temp_agebin)/1e+8

            else:

                if agebin >= 7.0:

                    sfr_10Myr += sfrs[:, index]*(np.power(10, agebin) - temp_agebin)/1e+7
                    break

                else:

                    temp_temp_agebin = temp_agebin
                    temp_agebin = np.power(10, agebin)
                    sfr_10Myr += sfrs[:, index]*(temp_agebin - temp_temp_agebin)/1e+7

                if agebin >= 8.0:

                    sfr_100Myr += sfrs[:, index]*(np.power(10, agebin) - temp_agebin)/1e+8
                    break

                else:

                    temp_temp_agebin = temp_agebin
                    temp_agebin = np.power(10, agebin)
                    sfr_100Myr += sfrs[:, index]*(temp_agebin - temp_temp_agebin)/1e+8

        age = np.array(age)
        sfr_10Myr = np.array(sfr_10Myr); ssfr_10Myr = sfr_10Myr/np.power(10, logmass)
        sfr_100Myr = np.array(sfr_100Myr); ssfr_100Myr = sfr_100Myr/np.power(10, logmass)

        return age, np.power(10, logmass), sfr_10Myr, sfr_100Myr, ssfr_10Myr, ssfr_100Myr

    # Measures properties of the stellar populations for the parametric delayed-tau model

    elif 'delayed' in sfh_type.lower() or 'tau' in sfh_type.lower():

        tage = chain[:, np.where(theta_labels == 'tage')[0][0]]
        mass = chain[:, np.where(theta_labels == 'mass')[0][0]]
        tau = chain[:, np.where(theta_labels == 'tau')[0][0]]
        age, sfr_10Myr, sfr_100Myr = [], [], []

        for temp_tage, temp_mass, temp_tau in zip(tage, mass, tau):

            dictionary = {'const': 0.0, 'tage': temp_tage, 'mass': temp_mass, 'tau': temp_tau, 'sfh': 4}

            age.append(prosp.plotting.sfh.parametric_mwa(tau=temp_tau, tage=temp_tage, power=1))

            if temp_tage < 100e-3:

                temp_sfr = prosp.plotting.sfh.parametric_sfr(times=0.0, tavg=temp_tage, **dictionary)[0]
                temp_sfr_100Myr = temp_sfr*(temp_tage/100e-3)
                sfr_100Myr.append(temp_sfr_100Myr)

                if temp_tage < 10e-3:

                    temp_sfr = prosp.plotting.sfh.parametric_sfr(times=0.0, tavg=temp_tage, **dictionary)[0]
                    temp_sfr_10Myr = temp_sfr*(temp_tage/10e-3)
                    sfr_10Myr.append(temp_sfr_10Myr)

                else:

                    temp_sfr_10Myr = prosp.plotting.sfh.parametric_sfr(times=0.0, tavg=10e-3, **dictionary)[0]
                    sfr_10Myr.append(temp_sfr_10Myr)

            else:

                temp_sfr_100Myr = prosp.plotting.sfh.parametric_sfr(times=0.0, tavg=100e-3, **dictionary)[0]
                temp_sfr_10Myr = prosp.plotting.sfh.parametric_sfr(times=0.0, tavg=10e-3, **dictionary)[0]
                sfr_100Myr.append(temp_sfr_100Myr)
                sfr_10Myr.append(temp_sfr_10Myr)

        age = 1e+9*np.array(age)
        sfr_10Myr = np.array(sfr_10Myr); ssfr_10Myr = sfr_10Myr/mass
        sfr_100Myr = np.array(sfr_100Myr); ssfr_100Myr = sfr_100Myr/mass

        return age, mass, sfr_10Myr, sfr_100Myr, ssfr_10Myr, ssfr_100Myr

    # Measures properties of the stellar populations for the parametric constant model

    elif 'constant' in sfh_type.lower():

        tage = chain[:, np.where(theta_labels == 'tage')[0][0]]
        mass = chain[:, np.where(theta_labels == 'mass')[0][0]]
        age, sfr_10Myr, sfr_100Myr = [], [], []

        for temp_tage, temp_mass in zip(tage, mass):

            dictionary = {'const': 1.0, 'tage': temp_tage, 'mass': temp_mass, 'sfh': 4}

            age.append(temp_tage/2.0)

            if temp_tage < 100e-3:

                temp_sfr = prosp.plotting.sfh.parametric_sfr(times=0.0, tavg=temp_tage, **dictionary)[0]
                temp_sfr_100Myr = temp_sfr*(temp_tage/100e-3)
                sfr_100Myr.append(temp_sfr_100Myr)

                if temp_tage < 10e-3:

                    temp_sfr = prosp.plotting.sfh.parametric_sfr(times=0.0, tavg=temp_tage, **dictionary)[0]
                    temp_sfr_10Myr = temp_sfr*(temp_tage/10e-3)
                    sfr_10Myr.append(temp_sfr_10Myr)

                else:

                    temp_sfr_10Myr = prosp.plotting.sfh.parametric_sfr(times=0.0, tavg=10e-3, **dictionary)[0]
                    sfr_10Myr.append(temp_sfr_10Myr)

            else:

                temp_sfr_100Myr = prosp.plotting.sfh.parametric_sfr(times=0.0, tavg=100e-3, **dictionary)[0]
                temp_sfr_10Myr = prosp.plotting.sfh.parametric_sfr(times=0.0, tavg=10e-3, **dictionary)[0]
                sfr_100Myr.append(temp_sfr_100Myr)
                sfr_10Myr.append(temp_sfr_10Myr)

        age = 1e+9*np.array(age)/2.0
        sfr_10Myr = np.array(sfr_10Myr); ssfr_10Myr = sfr_10Myr/mass
        sfr_100Myr = np.array(sfr_100Myr); ssfr_100Myr = sfr_100Myr/mass

        return age, mass, sfr_10Myr, sfr_100Myr, ssfr_10Myr, ssfr_100Myr

    # Throws error for invalid fit_type

    else:

        raise ValueError('The specified fit type is invalid...')

###

# Defines function for deriving emission line equivalent widths from the model spectroscopy

def derive_equivalent_widths(wavelength_Angstroms, flux_nJy, line_type='Hb+O3', xmin=4800.0, xmax=5100.0):

    # Derives emission line equivalent widths from the model spectroscopy (Hbeta + [OIII]4960,5008)

    if line_type == 'Hb+O3':

        wavelength, flux = wavelength_Angstroms, flux_nJy

        wave_step = 20.0 # Angstroms
        wave_Hbeta = 4862.637 # Angstroms
        wave_O3_4959 = 4960.295 # Angstroms
        wave_O3_5007 = 5008.240 # Angstroms

        mask = np.logical_and(xmin < wavelength, wavelength < xmax)
        mask[np.logical_and(wave_Hbeta - wave_step < wavelength, wavelength < wave_Hbeta + wave_step)] = False
        mask[np.logical_and(wave_O3_4959 - wave_step < wavelength, wavelength < wave_O3_4959 + wave_step)] = False
        mask[np.logical_and(wave_O3_5007 - wave_step < wavelength, wavelength < wave_O3_5007 + wave_step)] = False
        continuum = np.median(flux[:, mask])

        mask = np.logical_and(xmin < wavelength, wavelength < xmax)

        return (np.trapz(flux[:, mask], x=wavelength[mask]) - continuum*(xmax - xmin))/continuum

    # Throws error for invalid line_type

    else:

        raise ValueError('The specified fit type is invalid...')

###

# Reads the h5 file and interprets the dynesty fit on JADES-GS-z14-0

def build_results(hfile, sfh_type, model, observations, stellarPopulationSynthesis):

    # Reads the results, observations, and model from the output h5 file

    result, temp_observations, temp_model = reader.results_from(hfile, dangerous=False)

    # Creates the necessary directory, if it does not exist

    temp_path = hfile.replace('.h5', '')

    if not os.path.exists(temp_path): 

        os.mkdir(temp_path)

    make_trace_plot(hfile)

    # Determines parameters to be used throughout

    q = [0.16, 0.50, 0.84]

    try:

        theta_labels = np.array(result['theta_labels'])

    except:

        temp_theta_labels = np.array(list(result['chain'].dtype.names)); theta_labels = []

        for i, temp_theta_label in enumerate(temp_theta_labels):

            temp_size = result['chain'].dtype[i].shape[0]

            if temp_size == 1:

                theta_labels.append(temp_theta_label)

            else:

                for j in range(temp_size):

                    theta_labels.append(f'{temp_theta_label}_{j+1}')

        theta_labels = np.array(theta_labels)

    chain = np.array([value for sample in result['chain'] for values in list(sample) for value in values.tolist()])
    chain = chain.reshape(len(result['chain']), len(theta_labels))

    temp_weights = result.get('weights', None)

    if np.isinf(np.sum(temp_weights)):

        weights = np.ones_like(temp_weights, dtype=float)
        weights[~np.isinf(temp_weights)] = 0.0
        weights /= np.sum(weights)

    else:

        weights = temp_weights

    rest_wavelengths = stellarPopulationSynthesis.wavelengths

    np.save(f'{temp_path}/Wavelengths.npy', rest_wavelengths, allow_pickle=True)

    # Interprets the results...

    U, B, V, R, I, J, H, K, smoothed_spectrum, predictions, mfrac = extract_model_predictions(
        model, result, observations, stellarPopulationSynthesis)

    age, mass, sfr_10Myr, sfr_100Myr, ssfr_10Myr, ssfr_100Myr = measure_stellar_population_properties(
        sfh_type, result, chain, theta_labels)

    EWs = derive_equivalent_widths(rest_wavelengths, smoothed_spectrum, line_type='Hb+O3', xmin=4800.0, xmax=5100.0)

    UV = -2.5*np.log10(smoothed_spectrum[:, np.argmin(np.absolute(rest_wavelengths - 1500.0))])

    # Saves the first set of results...

    for i, observation in enumerate(observations):

        if observation.kind == 'photometry':

            spec, phot = smoothed_spectrum, np.array([prediction for prediction in predictions[:, i]])

    spec_p16, spec_p50, spec_p84 = 3631e+9*quantile(spec.T, q=q, weights=weights).T
    phot_p16, phot_p50, phot_p84 = 3631e+9*quantile(phot.T, q=q, weights=weights).T

    StellarMetal = chain[:, np.where(theta_labels == 'logzsol')[0][0]]
    StellarMass = np.log10(mfrac*mass)
    SFR_10Myr = sfr_10Myr
    StellarAge = 1e-6*age
    DustV = 1.086*chain[:, np.where(theta_labels == 'dust2')[0][0]]

    dictionary = {}
    dictionary['SFH'] = sfh_type
    dictionary['predictions'] = predictions
    dictionary['observations'] = observations
    dictionary['model_photometry'] = [phot_p16, phot_p50, phot_p84]
    dictionary['model_spectroscopy'] = [spec_p16, spec_p50, spec_p84]
    dictionary['model_spectroscopy_wavelengths'] = rest_wavelengths*(1.0 + observations[0].redshift)
    dictionary['model_parameters'] = [
        [r'$\mathrm{log}_{10}\left( M_{\ast}/M_{\odot} \right)$', StellarMass], 
        [r'$\mathrm{log}_{10}\left( Z_{\ast}/Z_{\odot} \right)$', StellarMetal], 
        [r'$\mathrm{SFR}_{10}/\left[ M_{\odot}/\mathrm{yr} \right]$', SFR_10Myr], 
        [r'$t_\mathrm{\ast}/\mathrm{Myr}$', StellarAge], 
        [r'$A_{V}\ \left[ \mathrm{AB\ mag} \right]$', DustV], 
        [r'$A_{V}\ \left[ \mathrm{AB\ mag} \right]$', DustV], 
    ]

    np.save(f'{temp_path}/DictionaryResults.npy', dictionary, allow_pickle=True)

    # Saves the second set of results...

    t = Table()
    t['age_stellar'] = age
    t['logmass_stellar'] = np.log10(mfrac*mass)
    t['ssfr_100Myr'] = ssfr_100Myr
    t['ssfr_10Myr'] = ssfr_10Myr
    t['sfr_100Myr'] = sfr_100Myr
    t['sfr_10Myr'] = sfr_10Myr

    for i, label in enumerate(theta_labels): 

        t[label] = chain[:, i]

    photometry = []

    for temp_spec in spec:

        temp_photometry = []

        for i, observation in enumerate(observations):

            if observation.kind == 'photometry':

                for j, filt in enumerate(observations[i].filters):

                    temp_correction = 3631e-23*(2.998e+18/np.square(rest_wavelengths))
                    temp_magnitude = filt.ab_mag(rest_wavelengths*(1.0 + observations[0].redshift), temp_spec*temp_correction)
                    temp_flux_nJy = 3631e+9*np.power(10, temp_magnitude/(-2.5))

                    temp_photometry.append(temp_flux_nJy)

        photometry.append(temp_photometry)

    t['photometry'] = np.array(photometry)

    t.write(f'{temp_path}/PosteriorResults.fits', overwrite=True)

    # Saves the third set of results...

    t = Table()

    for i, label in enumerate(['spectrum_full']): 

        if label == 'spectrum_full': t[label] = spec

    t.write(f'{temp_path}/PosteriorSpectra.fits', overwrite=True)

    # Saves the fourth set of results...

    dictionary_Results = {}
    dictionary_Results['ID'] = 183348
    percentiles = quantile(chain.T, q=q, weights=weights)

    for label, percentile in zip(theta_labels, percentiles): 

        dictionary_Results[f'{label}_p16'] = percentile[0]
        dictionary_Results[f'{label}_p50'] = percentile[1]
        dictionary_Results[f'{label}_p84'] = percentile[2]

    age_percentiles = quantile(age[np.newaxis], q=q, weights=weights)[0]
    mass_percentiles = quantile(mfrac*mass[np.newaxis], q=q, weights=weights)[0]
    sfr_10Myr_percentiles = quantile(sfr_10Myr[np.newaxis], q=q, weights=weights)[0]
    sfr_100Myr_percentiles = quantile(sfr_100Myr[np.newaxis], q=q, weights=weights)[0]
    ssfr_10Myr_percentiles = quantile(ssfr_10Myr[np.newaxis], q=q, weights=weights)[0]
    ssfr_100Myr_percentiles = quantile(ssfr_100Myr[np.newaxis], q=q, weights=weights)[0]

    UV_percentiles = quantile(UV[np.newaxis], q=q, weights=weights)[0]
    U_percentiles = quantile(U[np.newaxis], q=q, weights=weights)[0]
    B_percentiles = quantile(B[np.newaxis], q=q, weights=weights)[0]
    V_percentiles = quantile(V[np.newaxis], q=q, weights=weights)[0]
    R_percentiles = quantile(R[np.newaxis], q=q, weights=weights)[0]
    I_percentiles = quantile(I[np.newaxis], q=q, weights=weights)[0]
    J_percentiles = quantile(J[np.newaxis], q=q, weights=weights)[0]
    H_percentiles = quantile(H[np.newaxis], q=q, weights=weights)[0]
    K_percentiles = quantile(K[np.newaxis], q=q, weights=weights)[0]
    EW_percentiles = quantile(EWs[np.newaxis], q=q, weights=weights)[0]

    dictionary_Results['logage_stellar_p16'] = np.log10(age_percentiles[0])
    dictionary_Results['logage_stellar_p50'] = np.log10(age_percentiles[1])
    dictionary_Results['logage_stellar_p84'] = np.log10(age_percentiles[2])

    dictionary_Results['logmass_stellar_p16'] = np.log10(mass_percentiles[0])
    dictionary_Results['logmass_stellar_p50'] = np.log10(mass_percentiles[1])
    dictionary_Results['logmass_stellar_p84'] = np.log10(mass_percentiles[2])

    dictionary_Results['logssfr_100Myr_p16'] = np.log10(ssfr_100Myr_percentiles[0])
    dictionary_Results['logssfr_100Myr_p50'] = np.log10(ssfr_100Myr_percentiles[1])
    dictionary_Results['logssfr_100Myr_p84'] = np.log10(ssfr_100Myr_percentiles[2])

    dictionary_Results['logssfr_10Myr_p16'] = np.log10(ssfr_10Myr_percentiles[0])
    dictionary_Results['logssfr_10Myr_p50'] = np.log10(ssfr_10Myr_percentiles[1])
    dictionary_Results['logssfr_10Myr_p84'] = np.log10(ssfr_10Myr_percentiles[2])

    dictionary_Results['sfr_100Myr_p16'] = sfr_100Myr_percentiles[0]
    dictionary_Results['sfr_100Myr_p50'] = sfr_100Myr_percentiles[1]
    dictionary_Results['sfr_100Myr_p84'] = sfr_100Myr_percentiles[2]

    dictionary_Results['sfr_10Myr_p16'] = sfr_10Myr_percentiles[0]
    dictionary_Results['sfr_10Myr_p50'] = sfr_10Myr_percentiles[1]
    dictionary_Results['sfr_10Myr_p84'] = sfr_10Myr_percentiles[2]

    dictionary_Results['rest_UV_p16'] = UV_percentiles[0]
    dictionary_Results['rest_UV_p50'] = UV_percentiles[1]
    dictionary_Results['rest_UV_p84'] = UV_percentiles[2]

    dictionary_Results['rest_U_p16'] = U_percentiles[0]
    dictionary_Results['rest_U_p50'] = U_percentiles[1]
    dictionary_Results['rest_U_p84'] = U_percentiles[2]

    dictionary_Results['rest_B_p16'] = B_percentiles[0]
    dictionary_Results['rest_B_p50'] = B_percentiles[1]
    dictionary_Results['rest_B_p84'] = B_percentiles[2]

    dictionary_Results['rest_V_p16'] = V_percentiles[0]
    dictionary_Results['rest_V_p50'] = V_percentiles[1]
    dictionary_Results['rest_V_p84'] = V_percentiles[2]

    dictionary_Results['rest_R_p16'] = R_percentiles[0]
    dictionary_Results['rest_R_p50'] = R_percentiles[1]
    dictionary_Results['rest_R_p84'] = R_percentiles[2]

    dictionary_Results['rest_I_p16'] = I_percentiles[0]
    dictionary_Results['rest_I_p50'] = I_percentiles[1]
    dictionary_Results['rest_I_p84'] = I_percentiles[2]

    dictionary_Results['rest_J_p16'] = J_percentiles[0]
    dictionary_Results['rest_J_p50'] = J_percentiles[1]
    dictionary_Results['rest_J_p84'] = J_percentiles[2]

    dictionary_Results['rest_H_p16'] = H_percentiles[0]
    dictionary_Results['rest_H_p50'] = H_percentiles[1]
    dictionary_Results['rest_H_p84'] = H_percentiles[2]

    dictionary_Results['rest_K_p16'] = K_percentiles[0]
    dictionary_Results['rest_K_p50'] = K_percentiles[1]
    dictionary_Results['rest_K_p84'] = K_percentiles[2]

    dictionary_Results['rest_EquivalentWidth_Angstroms_p16'] = EW_percentiles[0]
    dictionary_Results['rest_EquivalentWidth_Angstroms_p50'] = EW_percentiles[1]
    dictionary_Results['rest_EquivalentWidth_Angstroms_p84'] = EW_percentiles[2]

    df = pd.DataFrame(dictionary_Results, index=[0])
    df.to_csv(f'{temp_path}/Results.csv', index=False)

    # Finished!