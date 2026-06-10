"""
==========================================
JADES-GS-z14-0 Prospector Helper Functions
==========================================

The following Python script was last updated on 2026/06/10 by Jakob M. Helton.
Helper functions for running Prospector v2 spectral energy distribution fitting
on JADES spectroscopy and photometry. Covers model building (non-parametric and
parametric star-formation histories, dust attenuation, nebular gas emission, and
intergalactic medium absorption), observation construction, stellar population
synthesis setup, posterior analysis, and diagnostic plotting.

-----------
Environment
-----------

Requires the SPS_HOME environment variable pointing to the FSPS data directory.

The following ancillary files must be in the Python path or working directory:
  - jwst_nirspec_{grating}_disp.fits (JWST/NIRSpec dispersion profiles, default)
  - shajib_2025_jwst_nirspec_{grating}_disp.fits (JWST/NIRSpec dispersion profiles, custom)
  - Input spectrum fits file and photometry catalog (passed to the build_observations function)

-------------
Usage Example
-------------

Below is the complete, minimal workflow used for JADES-GS-z14-0 (at redshift 14). Copy this
block into a notebook cell (or a driver script) and adapt the filenames, star formation
history type, and redshift for your own target.

    # Imports all helper functions

    import PID08544_Prospector_helper as helper

    # Defines the spectroscopic files and photometry catalog

    filename_spec = [
        'hlsp_jades_jwst_nirspec_goods-s-deepjwst-00183348_clear-prism_v1.0_x1d.fits',
        'jw08544_obsAll_t001_miri_p750l_x1d.fits',
    ] # Defines the spectroscopic files

    filename_phot = 'catalogs/catalog_183348.csv' # Defines the photometric catalog

    observations = helper.build_observations(filename_spec, filename_phot, index=0, maximumSNR=20.0)

    # Builds the Prospector model for the target galaxy assuming a non-parametric rising star formation history

    sfh_type = 'Rising' # Options: 'BurstyContinuity', 'Continuity', 'Constant', 'DelayedTau', 'Rising'

    model = helper.build_model_Prospector(observations,
        sfh_type, observations[0].redshift, zerr=0.7e-3, zbirth=None, zmax=15.0, zmin=13.0,
        nbins=6, scale=1.0, alpha=0.8, imf_type='Chabrier', imf_lower=0.08, imf_upper=120.0, decouple_metallicity=True,
        two_component_dust=True, gas_logu=True, escape_fraction=True, damping_wing=True, igm_factor=False,
        lyman_alpha=False,
    )

    # Defines the relevant run parameters dictionary

    dlogz = float(1e-2)
    neffective = int(1e+4)
    nlivepoints = int(1e+3)
    method = 'auto'

    run_params = {}

    run_params['verbose'] = True

    run_params['emcee'] = False
    run_params['optimize'] = False
    run_params['nested_sampler'] = 'dynesty'

    run_params['method'], run_params['nested_method'] = method, method

    run_params['dlogz'], run_params['nested_dlogz'] = dlogz, dlogz
    run_params['n_effective'], run_params['nested_n_effective'] = neffective, neffective
    run_params['target_n_effective'], run_params['nested_target_n_effective'] = neffective, neffective
    run_params['nlive'], run_params['nested_nlive'] = nlivepoints, nlivepoints

    run_params['FSPS_version'] = fsps.__version__
    run_params['Prospector_version'] = prosp.__version__
    run_params['StellarPopulation_libraries'] = StellarPopulations.libraries

    # Retrieves the stellar population synthesis object appropriate for the chosen SFH type

    stellarPopulationSynthesis = helper.get_stellarPopulationSynthesis_NonParametric()

    # Runs the dynesty nested sampler and writes the output HDF5 file

    hfile = f'h5/GSz14_{sfh_type}SFH_dynesty_v0.h5'

    fitted_model = fit_model(observations, model, stellarPopulationSynthesis, lnprobfn=lnprobfn, **run_params)

    writer.write_hdf5(hfile, config=run_params, model=model, obs=observations, sps=stellarPopulationSynthesis,
        sampling_result=fitted_model['sampling'], optimize_result_tuple=fitted_model['optimization'],
        write_model_params=True,
    )

    # Builds posterior results, diagnostic plots (trace, corner, SFH) from the HDF5 output file

    helper.build_results(hfile, sfh_type, model, observations, stellarPopulationSynthesis)

    # Investigates the weights from the sampler

    result, temp_observations, temp_model = reader.results_from(hfile, dangerous=False)

    weights_fin = np.sum(~np.isinf(result.get('weights', None)))
    weights_inf = np.sum(np.isinf(result.get('weights', None)))

    print(f'Number of samples with finite weights = {weights_fin}')
    print(f'Number of samples with infinite weights = {weights_inf}')
    print(f'Percentage of samples with infinite weights = {100.0*weights_inf/(weights_inf+weights_fin):.3f}%')

    weights_new = result.get('lnweights', None) - np.amax(result.get('lnweights', None))

    weights_fin = np.sum(~np.isinf(weights_new))
    weights_inf = np.sum(np.isinf(weights_new))

    print()
    print(f'After reweighting...')
    print(f'Number of samples with finite weights = {weights_fin}')
    print(f'Number of samples with infinite weights = {weights_inf}')
    print(f'Percentage of samples with infinite weights = {100.0*weights_inf/(weights_inf+weights_fin):.3f}%')

    weights_new = np.exp(weights_new); weights_new /= np.sum(weights_new); weights_new

    # Modifies and adds relevant quantities in the Posterior_Results fits files

    table = Table.read(f'{hfile.replace(".h5", "")}/Posterior_Results.fits', format='fits')

    table['tbirth'] = 1e+3*table['tbirth'].data
    table['age_stellar'] = np.log10(1e+0*table['age_stellar'].data)
    table['sfr_100Myr'] = 1e+0*table['sfr_100Myr'].data
    table['sfr_10Myr'] = 1e+0*table['sfr_10Myr'].data

    for i in range(model.params['agebins'].shape[0]-1):

        table[f'sfr_ratios_{i+1}'] = np.power(10, table[f'logsfr_ratios_{i+1}'].data)

    zipped_data = zip(table['zred'].data, table['tbirth'].data/1e+3)

    table['zbirth'] = np.array([helper.transform_tbirth_to_zbirth(zred, tbirth) for zred, tbirth in zipped_data])

    # Determines the inferred SFHs from the Prospector fitting results

    theta_labels, chain = helper.determine_theta_labels_and_chain(result)

    N = int(1e+4) + 1
    lin_lookback_times = np.linspace(+0.0, 1e+3*cosmo.age(observations[0].redshift).value, N)
    log_lookback_times = np.logspace(+6.0, np.log10(1e+9*cosmo.age(observations[0].redshift).value), N)

    lookback_times, sfhs = helper.measure_star_formation_history(
        sfh_type, result, chain, theta_labels,
        log_lookback_times,
    )

    sfh_arguments = {
        'include_sfh': True,
        'lookback_times': lookback_times, 'sfhs': sfhs,
        'xlimits': [1e+0, 3e+2], 'ylimits': [3e-3, 3e+1],
        'vlines': [15.0, 20.0, 100.0], 'redshift': observations[0].redshift,
    }

    helper.make_sfh_plot(hfile, weights_new, sfh_arguments=sfh_arguments)

    # Creates corner plot to illustrate the fitting results

    temp_xarray = np.array([
        # X-Axis Range (list), Column Name (string), X-Axis Label (rstring)
            [[+6.0, +10.0], 'logmass_stellar', r'$\mathrm{log}_{10} (\frac{M_{\ast}}{M_{\odot}})$'],
            [[+6.0, +9.0], 'age_stellar', r'$\mathrm{log}_{10} (\frac{t_{\ast}}{\mathrm{yr}})$'],
            [[+0.0, +10.0], 'sfr_ratios_1', r'$\frac{\mathrm{SFR}_{3}}{\mathrm{SFR}_{10}}$'],
            [[+0.0, +50.0], 'sfr_10Myr', r'$\frac{\mathrm{SFR}_{10}}{M_{\odot} / \mathrm{yr}}$'],
            [[+0.0, +50.0], 'sfr_100Myr', r'$\frac{\mathrm{SFR}_{100}}{M_{\odot} / \mathrm{yr}}$'],
            [[+0.0, +300.0], 'tbirth', r'$\frac{t_{\mathrm{birth}}}{\mathrm{Myr}}$'],
            [[observations[0].redshift, +100.0], 'zbirth', r'$z_{\mathrm{birth}}$'],
    ], dtype=object)

    helper.make_corner_plot(hfile, weights_new, table, temp_xarray, smooth=+0.0, 
        filename_suffix='small', sfh_arguments=sfh_arguments,
    )
"""

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

colors_8 = sns.color_palette('husl', 8)
colors_7 = sns.color_palette('husl', 7)
colors_6 = sns.color_palette('husl', 6)
colors_5 = sns.color_palette('husl', 5)
colors_4 = sns.color_palette('husl', 4)
colors_3 = sns.color_palette('husl', 3)
colors_2 = sns.color_palette('husl', 2)
colors_1 = sns.color_palette('husl', 1)

matplotlib.rcParams.update({

    'text.usetex': True,

    'font.size': 16,
    'axes.labelsize': 20,
    'axes.titlesize': 20,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,

    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.top': True, # ticks on top spine
    'ytick.left': True, # ticks on left spine
    'ytick.right': True, # ticks on right spine
    'xtick.bottom': True, # ticks on bottom spine
    'xtick.minor.visible': True, # draw minor ticks by default

    'xtick.major.size': 6,
    'ytick.major.size': 6,
    'xtick.minor.size': 4,
    'ytick.minor.size': 4,
    'xtick.major.width': 3,
    'ytick.major.width': 3,
    'xtick.minor.width': 3,
    'ytick.minor.width': 3,

    'axes.linewidth': 3,
    'lines.linewidth': 3,

    'savefig.dpi': 300,
    'savefig.bbox': 'tight',

})

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

import fsps, dynesty

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

fsps_emlines_file = os.path.join(os.environ.get('SPS_HOME', ''), 'data', 'emlines_info.dat')
fsps_emlines_rest_wavelength_Angstroms = np.loadtxt(fsps_emlines_file, delimiter=',', usecols=0)

maggies_to_Jy = 3631.0

###

# General model building function for most default types of SFH and IMF
# Defines and builds model based on the methodology of Carniani et al. (2025)
# Relevant Reference: https://www.scixplorer.org/abs/2025A&A...696A..87C/abstract

def build_model_Prospector(observations, sfh_type, zred, zerr=None, zbirth=20.0, zmax=20.0, zmin=0.0, nbins=6, scale=1.0, alpha=0.8, 
    imf_type='Chabrier', imf_lower=0.08, imf_upper=120.0, decouple_metallicity=True, two_component_dust=True, 
    gas_logu=True, escape_fraction=True, damping_wing=True, igm_factor=True, lyman_alpha=True):

    # Creates list of the available sfh_types

    available_sfh_types = ['BurstyContinuity', 'Continuity', 'Constant', 'DelayedTau', 'Rising']

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
                'prior': priors.TopHat(
                    mini=transform_zbirth_to_tbirth(zred, 15.0), maxi=transform_zbirth_to_tbirth(zred, 100.0)), 
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
            'depends_on': transforms.delogify_mass, 
        }

        # Includes the model parameters for tBirth and zBirth

        if zbirth is None:

            model_params['tage'] = {
                'name': 'parametric_lookback_time_of_the_first_stars', 
                'units': u.Gyr, 
                'N': 1, 
                'isfree': True, 
                'init': 1e-2, 
                'prior': priors.LogUniform(mini=1e-3, maxi=transform_zbirth_to_tbirth(zred, 100.0)), 
            }

        else:

            model_params['tage'] = {
                'name': 'parametric_lookback_time_of_the_first_stars', 
                'units': u.Gyr, 
                'N': 1, 
                'isfree': True, 
                'init': 1e-2, 
                'prior': priors.LogUniform(mini=1e-3, maxi=transform_zbirth_to_tbirth(zred, zbirth)), 
            }

        # Adjust SFH parameters to only include the constant component

        if 'constant' in sfh_type.lower():

            model_params['tau'] = {
                'name': 'exponential_e_folding_time', 
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

            if zbirth is None:

                model_params['tau'] = {
                    'name': 'exponential_e_folding_time', 
                    'units': 1.0/u.Gyr, 
                    'N': 1, 
                    'isfree': True, 
                    'init': 1.0, 
                    'prior': priors.LogUniform(mini=1e-3, maxi=transform_zbirth_to_tbirth(zred, 100.0)), 
                }

            else:

                model_params['tau'] = {
                    'name': 'exponential_e_folding_time', 
                    'units': 1.0/u.Gyr, 
                    'N': 1, 
                    'isfree': True, 
                    'init': 1.0, 
                    'prior': priors.LogUniform(mini=1e-3, maxi=transform_zbirth_to_tbirth(zred, zbirth)), 
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
        'prior': priors.TopHat(mini=-2.0, maxi=0.0), # priors.ClippedNormal(mean=-1.0, sigma=0.5, mini=-2.0, maxi=0.0), 
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

        contains_nirspec = np.any('nirspec' in ', '.join(observation_names).lower())

        contains_miri_lrs = np.any('miri' in ', '.join(observation_names).lower() 
            and 'lrs' in ', '.join(observation_names).lower())

        model_params['eline_delta_zred'] = {
            'name': 'emission_line_redshift_offset', 
            'units': None, # Redshift
            'N': 1, 
            'isfree': True, 
            'init': 0.0, 
            'prior': priors.TopHat(mini=-1e-1, maxi=+1e-1), 
        }
        
        if contains_nirspec and contains_miri_lrs:

            model_params['eline_sigma'] = {
                'name': 'emission_line_velocity_dispersion', 
                'units': u.km/u.s, 
                'N': len(fsps_emlines_rest_wavelength_Angstroms), 
                'isfree': False, 
                'init': 1e+2*np.ones(len(fsps_emlines_rest_wavelength_Angstroms)), 
                'depends_on': transform_eline_sigma_across_instruments_with_wavelength_dependence,
            }

            model_params['eline_sigma_nirspec'] = {
                'name': 'emission_line_velocity_dispersion_intrinsic', 
                'units': u.km/u.s, 
                'N': 1, 
                'isfree': True, 
                'init': 1e+2, 
                'prior': priors.ClippedNormal(mean=1e+2, sigma=1e+2, mini=1e+1, maxi=1e+4), 
            }

        else:

            model_params['eline_sigma'] = {
                'name': 'emission_line_velocity_dispersion', 
                'units': u.km/u.s, 
                'N': 1, 
                'isfree': True, 
                'init': 1e+2, 
                'prior': priors.ClippedNormal(mean=1e+2, sigma=1e+2, mini=1e+1, maxi=1e+4), 
            }

        if contains_nirspec:

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

        if contains_miri_lrs:

            model_params['disp_corr_poly_0_miri_lrs'] = {
                'name': 'dispersion_correction_polynomial_coefficient_0_miri_lrs', 
                'units': None, 
                'N': 1, 
                'isfree': True, 
                'init': 1.0, 
                'prior': priors.LogUniform(mini=1e+0, maxi=1e+1), 
            }

            model_params['disp_corr_poly_1_miri_lrs'] = {
                'name': 'dispersion_correction_polynomial_coefficient_1_miri_lrs', 
                'units': 1.0/u.um, 
                'N': 1, 
                'isfree': True, 
                'init': 0.0, 
                'prior': priors.ClippedNormal(mean=0.0, sigma=0.2, mini=-1.0, maxi=+1.0), 
            }

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

    model = SpecModel(model_params) # model = ProspectorParams(model_params)

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

        lookback_time = 1.0e+9*cosmo.lookback_time(zred).value # lookback time at zred
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

    if tbirth.shape != ():

        tuniv = tbirth[0]

    else:

        tuniv = tbirth

    if nbins < 4:

        raise Exception('Number of bins must be greater than four.')

    elif agebin1 is None or np.log10(1.0e+9*tuniv) <= agebin1:

        agelims = [0] + np.linspace(6.0, np.log10(1.0e+9*tuniv), nbins-0).tolist()

    elif agebin2 is None or np.log10(1.0e+9*tuniv) <= agebin2:

        agelims = [0] + np.linspace(agebin1, np.log10(1.0e+9*tuniv), nbins-0).tolist()

    elif agebin3 is None or np.log10(1.0e+9*tuniv) <= agebin3:

        agelims = [0, agebin1] + np.linspace(agebin2, np.log10(1.0e+9*tuniv), nbins-1).tolist()

    else:

        agelims = [0, agebin1, agebin2] + np.linspace(agebin3, np.log10(1.0e+9*tuniv), nbins-2).tolist()

    # Ensures that the minimum spacing between adjacent age bins is larger than 1 Myr

    if np.amin(np.diff(np.power(10, np.array([agelims[:-1], agelims[1:]])))) < 1e+6:

        agelims = [0] + np.linspace(6.0, np.log10(1.0e+9*tuniv), nbins-0).tolist()

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

    tlookback = cosmo.age(zred) - np.amax(tbirth)*u.Gyr

    return astropy.cosmology.z_at_value(cosmo.age, tlookback).value

###

# Defines function for splitting emission line velocity dispersions across different instruments

def transform_eline_sigma_across_instruments(zred=0.0, eline_sigma_nirspec=100.0, eline_sigma_miri_lrs=100.0, 
    pivot_wavelength_microns=5.3, **dictionary_for_extras):

    # This is relevant for allowing the emission line velocity dispersion to be different across different instruments
    # We want to accurately model the spectrophotometric calibration of the spectrum across the full wavelength range

    obs_wavelength_microns = fsps_emlines_rest_wavelength_Angstroms*(1.0 + zred)/1e+4
    nirspec_sigma = np.atleast_1d(eline_sigma_nirspec)[0]
    miri_sigma = np.atleast_1d(eline_sigma_miri_lrs)[0]

    return np.where(obs_wavelength_microns < pivot_wavelength_microns, nirspec_sigma, miri_sigma)

def transform_eline_sigma_across_instruments_with_wavelength_dependence(zred=0.0, eline_sigma_nirspec=100.0, 
    disp_corr_poly_0_miri_lrs=1.0, disp_corr_poly_1_miri_lrs=0.0, minimum_wavelength_microns_miri_lrs=5.3, 
    maximum_wavelength_microns_miri_lrs=10.3, **dictionary_for_extras):

    # This is relevant for allowing the emission line velocity dispersion to be different across different instruments
    # We want to accurately model the spectrophotometric calibration of the spectrum across the full wavelength range

    # The dispersion profile of the MIRI/LRS is corrected by multiplying by a wavelength-dependent linear polynomial
    # This corrections addresses potential issues with wavelength dependence of the instrumental resolution

    obs_wavelength_microns = fsps_emlines_rest_wavelength_Angstroms*(1.0 + zred)/1e+4
    nirspec_sigma = np.atleast_1d(eline_sigma_nirspec)[0]

    resolution_miri_lrs = -73.1 + 20.0*obs_wavelength_microns
    # Retrieved resolving power for the MIRI/LRS using the binary BD Gliese 229Bab
    # Relevant Reference: https://www.scixplorer.org/abs/2024ApJ...977L..32X/abstract
    # See Figure C1 in Appendix C: Retrieved Resolving Power and Wavelength Correction
    resolution_miri_lrs = np.clip(resolution_miri_lrs, 1.0, None)

    sigma_instrument_miri = astropy.constants.c.to('km/s').value/(np.sqrt(4.0*np.log(4.0))*resolution_miri_lrs)
    # Convert to instrumental resolution at each wavelength point in units of km/s

    P0 = np.atleast_1d(disp_corr_poly_0_miri_lrs)[0]
    P1 = np.atleast_1d(disp_corr_poly_1_miri_lrs)[0]
    pivot_wavelength_microns = minimum_wavelength_microns_miri_lrs if P1 >= 0.0 else maximum_wavelength_microns_miri_lrs
    polynomial_correction = P0 + P1*(obs_wavelength_microns - pivot_wavelength_microns)

    miri_sigma = np.sqrt(np.maximum(0.0, 
        np.square(nirspec_sigma) + np.square(sigma_instrument_miri)*(np.square(polynomial_correction) - 1.0)))

    condition = np.logical_or(obs_wavelength_microns < minimum_wavelength_microns_miri_lrs, 
        maximum_wavelength_microns_miri_lrs < obs_wavelength_microns)

    return np.where(condition, nirspec_sigma, miri_sigma)

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

    temp_filterSet = np.array([
        col.replace('_f_nJy', '') for col in df.columns[flux_indices]
    ])

    filters, flux_phot, uncertainty_phot = [], [], []

    for i, filt in enumerate(temp_filterSet):

        if fluxes.iloc[i] == 0 and np.isnan(errors.iloc[i]): continue

        flux_phot.append(1e-9*fluxes.iloc[i]/maggies_to_Jy)
        uncertainty_phot.append(1e-9*np.nanmax([errors.iloc[i], fluxes.iloc[i]/maximumSNR])/maggies_to_Jy) # establish noise floor

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
        flux_phot.append(1e-9*(0.0/maggies_to_Jy)); uncertainty_phot.append(1e-9*(7000.0/maggies_to_Jy))

    filters, flux_phot, uncertainty_phot = np.array(filters), np.array(flux_phot), np.array(uncertainty_phot)
    wavelengths_phot = np.array([f.wave_effective for f in filters])
    mask_phot = np.zeros_like(wavelengths_phot, dtype=bool)
    mask_phot = ~mask_phot

    if True: flux_phot[flux_phot < 0.0] = 0.0 # Negative values are zeroed out

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

        flux_nirspec = flux_nirspec.to('Jy').value/maggies_to_Jy
        uncertainty_nirspec = uncertainty_nirspec.to('Jy').value/maggies_to_Jy
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

            flux_miri_lrs = (1e-3*(flux_ETC*u.Jy)/maggies_to_Jy).value
            uncertainty_miri_lrs = (1e-3*(error_ETC*u.Jy)/maggies_to_Jy).value
            wavelengths_miri_lrs = ((wave_ETC*u.um).to(u.AA)).value

        except Exception:

            with fits.open(filename_spec[1]) as hdul_x1d:

                try:

                    data_x1d = hdul_x1d['EXTRACT1D'].data

                except KeyError:

                    data_x1d = hdul_x1d['COMBINE1D'].data

                column_names = data_x1d.columns.names
                flux_error_data = data_x1d[np.array(column_names)[np.char.find(column_names, 'ERROR') != -1][0]]
                wavelength_data = data_x1d.field(np.where(np.array(column_names) == 'WAVELENGTH')[0][0])
                flux_data = data_x1d.field(np.where(np.array(column_names) == 'FLUX')[0][0])

                if True:

                    flux_data = np.flip(flux_data)
                    flux_error_data = np.flip(flux_error_data)
                    wavelength_data = np.flip(wavelength_data)

                # Empirical wavelength calibration comes from https://www.scixplorer.org/abs/2024ApJ...977L..32X/abstract

                if False: wavelength_data = -0.0864 + 1.0223*np.power(wavelength_data, 1) - 0.0014*np.power(wavelength_data, 2)

                condition_miri_lrs = np.logical_and(4.875 <= wavelength_data, wavelength_data <= 10.375)

                flux_miri_lrs = ((flux_data[condition_miri_lrs]*u.Jy)/maggies_to_Jy).value
                uncertainty_miri_lrs = ((flux_error_data[condition_miri_lrs]*u.Jy)/maggies_to_Jy).value
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

    except KeyError:

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

    if not isinstance(burn_in, int): burn_in = int(burn_in*chain.shape[0])

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

        ax.tick_params(axis='both', which='major', direction='out', 
            bottom=True, top=True, left=True, right=True, length=6, width=lw, labelsize=12)
        ax.tick_params(axis='both', which='minor', direction='out', 
            bottom=True, top=True, left=True, right=True, length=4, width=lw, labelsize=12)

        for j in range(nwalk):

            ax.plot(lnp[j, burn_in:], color='darkgrey', lw=lw, alpha=1.0, zorder=2)

        ax.set_title(r'$\mathrm{logprobability}$', y=y_value_label, size=16)

        ax.xaxis.set_major_locator(MaxNLocator(4))
        ax.yaxis.set_major_locator(MaxNLocator(4))

        ax.xaxis.set_minor_locator(AutoMinorLocator(4))
        ax.yaxis.set_minor_locator(AutoMinorLocator(4))

        for axis in ['top','bottom','left','right']: 

            ax.spines[axis].set_linewidth(lw)

        for ax in axes.flat[ndim:]: 

            ax.axis('off')

    [ax.set_xlabel(r'$\mathrm{Number\ of\ Iterations}$', size=16) for ax in axes[-1, :]]

    # Saves the trace plot figure

    plt.subplots_adjust(hspace=0.25, wspace=0.25)

    plt.savefig(f'{hfile.replace(".h5", "/Trace_Plot")}.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'{hfile.replace(".h5", "/Trace_Plot")}.png', dpi=300, bbox_inches='tight')
    plt.savefig(f'{hfile.replace(".h5", "/Trace_Plot")}.jpg', dpi=300, bbox_inches='tight')

    plt.show()

###

# Defines function for making a corner plot from input data

def make_corner_plot(hfile, weights_new, table, xarray, smooth=+0.0, lw=2, nbins=20, max_n_ticks=4, levels=[+0.68, +0.95, +0.99], 
    highlight_panel=None, filename_suffix=None, sfh_arguments=None):

    # Defines the dictionary containing arguments for the SFH, if none are provided

    if sfh_arguments is None:

        sfh_arguments = {
            'include_sfh': False, 
            'lookback_times': [], 'sfhs': [], 
            'xlimits': [1e+0, 3e+2], 'ylimits': [3e-3, 3e+1], 
            'vlines': [15.0, 20.0, 100.0], 
            'redshift': 14.1796, 
        }

    # Defines relevant hyperparameters and creates matplotlib figure

    plt.close()

    fig = corner.corner(
        weights=weights_new, 
        data=table[xarray[:, 1].tolist()].to_pandas().to_numpy(), 
        labels=xarray[:, 2].tolist(), 
        range=xarray[:, 0].tolist(), 
        bins=nbins, 
        levels=levels, 
        fill_contours=True,
        title_kwargs={'fontsize': 12, 'pad':8}, 
        label_kwargs={'fontsize': 40}, 
        plot_datapoints=False, 
        plot_density=False, 
        smooth1d=smooth, 
        smooth=smooth, 
        labelpad=5e-2, 
        lw=1.5*lw, 
        color=colors_5[3], 
        max_n_ticks=max_n_ticks, 
        hist_kwargs={'lw': lw}, 
        contourf_kwargs={'lw': lw}, 
        kwargs={'lw': 1.5*lw}, 
    )

    fig.subplots_adjust(wspace=+0.1, hspace=+0.1)

    temp_N = len(xarray); ax_list = fig.axes

    for i in range(temp_N):

        for j in range(temp_N):

            if i == j:

                temp_ax = ax_list[temp_N*i+j]

                temp_ymin, temp_ymax = temp_ax.get_ylim(); temp_color = colors_5[3]

                p16, p50, p84 = np.quantile(dynesty.utils.resample_equal(
                    table[xarray[:, 1].tolist()].to_pandas().to_numpy()[:, i], weights_new), [0.16, 0.50, 0.84], axis=0)

                temp_ax.vlines([p16, p84], temp_ymin, temp_ymax, color=temp_color, ls=':', lw=1.5*lw, alpha=1.0, zorder=2)
                temp_ax.vlines([p50], temp_ymin, temp_ymax, color=temp_color, ls='--', lw=1.5*lw, alpha=1.0, zorder=2)

                if xarray[i, 1] == 'tbirth':

                    temp_ax.set_title(fr'${int(p50):+d}_{{{int(p16-p50):+d}}}^{{{int(p84-p50):+d}}}$', fontsize=24, pad=12)

                elif xarray[i, 1] == 'frac_obrun':

                    temp_ax.set_title(fr'${p50:+.3f}_{{{p16-p50:+.3f}}}^{{{p84-p50:+.3f}}}$', fontsize=24, pad=12)

                elif xarray[i, 1] == 'zbirth' or xarray[i, 1] == 'dla_logNh':

                    temp_ax.set_title(fr'${p50:+.1f}_{{{p16-p50:+.1f}}}^{{{p84-p50:+.1f}}}$', fontsize=24, pad=12)

                else:

                    temp_ax.set_title(fr'${p50:+.2f}_{{{p16-p50:+.2f}}}^{{{p84-p50:+.2f}}}$', fontsize=24, pad=12)

    # Changes the plotting parameters for each of the axes

    for ax in ax_list:

        ax.tick_params(axis='both', which='major', direction='out', 
            bottom=True, top=False, left=True, right=False, length=3*lw, width=lw, labelsize=16)
        ax.tick_params(axis='both', which='minor', direction='out', 
            bottom=True, top=False, left=True, right=False, length=2*lw, width=lw, labelsize=16)

        for axis in ['top','bottom','left','right']: 

            ax.spines[axis].set_linewidth(lw)

    if highlight_panel is not None:

        for coordinates in highlight_panel:

            for i in range(temp_N):

                for j in range(temp_N):

                    if i == coordinates[0] and j == coordinates[1]:

                        temp_ax = ax_list[temp_N*i+j]

                        temp_ax.tick_params(axis='both', which='major', direction='out', 
                            bottom=True, top=False, left=True, right=False, length=3*lw, width=2*lw, labelsize=16)
                        temp_ax.tick_params(axis='both', which='minor', direction='out', 
                            bottom=True, top=False, left=True, right=False, length=2*lw, width=2*lw, labelsize=16)

                        for axis in ['top','bottom','left','right']: 

                            temp_ax.spines[axis].set_linewidth(2*lw)

    # Includes an additional axis to illustrate the inferred SFH

    if sfh_arguments['include_sfh']:

        assert sfh_arguments['lookback_times'].shape[0] == sfh_arguments['sfhs'].shape[0], 'Length of lookback times and SFHs must match.'

        assert 'xlimits' in sfh_arguments and len(sfh_arguments['xlimits']) == 2, 'xlimits must be specified with a length of two.'
        assert 'ylimits' in sfh_arguments and len(sfh_arguments['ylimits']) == 2, 'ylimits must be specified with a length of two.'

        assert sfh_arguments['redshift'] is not None, 'Redshift must be specified.'

        fig_width, fig_height = fig.get_size_inches(); fact = 0.3*fig_width/6.0

        ax = fig.add_axes([0.65, 0.67, 0.30, 0.30])

        ages_Myr, sfhs = 1e-6*sfh_arguments['lookback_times'], sfh_arguments['sfhs']

        ax.tick_params(
            axis='both', which='major', direction='out', 
            bottom=True, top=True, left=True, right=True, 
            length=6*lw*fact, width=2*lw*fact, labelsize=24*fact)
        ax.tick_params(
            axis='both', which='minor', direction='out', 
            bottom=True, top=True, left=True, right=True, 
            length=4*lw*fact, width=2*lw*fact, labelsize=24*fact)

        ax.set_xlabel(r'$t_{\mathrm{lookback}}\ \left[\mathrm{Myr}\right]$', fontsize=36*fact)
        ax.set_ylabel(r'$\mathrm{SFR}\ \left[M_{\odot}/\mathrm{yr}\right]$', fontsize=36*fact, labelpad=8*fact)

        if sfh_arguments['lookback_times'] is not None:

            ax.vlines(1e+3*(cosmo.age(sfh_arguments['redshift']).value - cosmo.age([15.0, 20.0, 100.0]).value), 
                sfh_arguments['ylimits'][0], sfh_arguments['ylimits'][1], color='lightgrey', 
                ls=':', lw=2*lw*fact, alpha=1.0, zorder=0)

        sfh16, sfh50, sfh84 = np.quantile(dynesty.utils.resample_equal(sfhs.T, weights_new), [0.16, 0.50, 0.84], axis=0)

        ax.stairs(sfh50, np.append(-10.0, ages_Myr), baseline=sfh50, color=colors_5[3], lw=2*lw*fact, zorder=1)
        ax.fill_between(np.append(-10.0, ages_Myr), np.append(sfh16[0], sfh16), np.append(sfh84[0], sfh84), 
            step='pre', color=colors_5[3], lw=0, alpha=0.2, zorder=0)

        ax.set_xscale('log'); ax.set_yscale('log')

        ax.set_xlim(sfh_arguments['xlimits'][0], sfh_arguments['xlimits'][1])
        ax.set_ylim(sfh_arguments['ylimits'][0], sfh_arguments['ylimits'][1])

        for axis in ['top','bottom','left','right']: 

            ax.spines[axis].set_linewidth(2*lw*fact)

    # Saves the corner plot figure

    if filename_suffix is not None:

        plt.savefig(f'{hfile.replace(".h5", f"/Corner_Plot_{filename_suffix}")}.pdf', dpi=300, bbox_inches='tight')
        plt.savefig(f'{hfile.replace(".h5", f"/Corner_Plot_{filename_suffix}")}.png', dpi=300, bbox_inches='tight')
        plt.savefig(f'{hfile.replace(".h5", f"/Corner_Plot_{filename_suffix}")}.jpg', dpi=300, bbox_inches='tight')

    else:

        plt.savefig(f'{hfile.replace(".h5", "/Corner_Plot")}.pdf', dpi=300, bbox_inches='tight')
        plt.savefig(f'{hfile.replace(".h5", "/Corner_Plot")}.png', dpi=300, bbox_inches='tight')
        plt.savefig(f'{hfile.replace(".h5", "/Corner_Plot")}.jpg', dpi=300, bbox_inches='tight')

    plt.show()

###

# Defines function for making a star-formation history plot from input data

def make_sfh_plot(hfile, weights_new, lw=3, sfh_arguments=None):

    # Defines the dictionary containing arguments for the SFH, if none are provided

    if sfh_arguments is None:

        sfh_arguments = {
            'include_sfh': False, 
            'lookback_times': [], 'sfhs': [], 
            'xlimits': [1e+0, 3e+2], 'ylimits': [3e-3, 3e+1], 
            'vlines': [15.0, 20.0, 100.0], 
            'redshift': 14.1796, 
        }

    # Defines relevant hyperparameters and creates matplotlib figure

    if sfh_arguments['include_sfh']:

        assert sfh_arguments['lookback_times'].shape[0] == sfh_arguments['sfhs'].shape[0], 'Length of lookback times and SFHs must match.'

        assert 'xlimits' in sfh_arguments and len(sfh_arguments['xlimits']) == 2, 'xlimits must be specified with a length of two.'
        assert 'ylimits' in sfh_arguments and len(sfh_arguments['ylimits']) == 2, 'ylimits must be specified with a length of two.'

        assert sfh_arguments['redshift'] is not None, 'Redshift must be specified.'

        plt.close()
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111)

        ages_Myr, sfhs = 1e-6*sfh_arguments['lookback_times'], sfh_arguments['sfhs']

        ax.tick_params(axis='both', which='major', direction='out', 
            bottom=True, top=True, left=True, right=True, length=3*lw, width=lw, labelsize=20)
        ax.tick_params(axis='both', which='minor', direction='out', 
            bottom=True, top=True, left=True, right=True, length=2*lw, width=lw, labelsize=20)

        ax.set_xlabel(r'$t_{\mathrm{lookback}}\ \left[\mathrm{Myr}\right]$', fontsize=32)
        ax.set_ylabel(r'$\mathrm{SFR}\ \left[M_{\odot}/\mathrm{yr}\right]$', fontsize=32, labelpad=8)

        if False:

            redshifts_major = np.array([15.0, 20.0, 100.0], dtype=int)
            redshifts_minor = np.array([14.0, 16.0, 17.0, 18.0, 19.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0], dtype=int)

            ages_major = 1e+3*(cosmo.age(observations[0].redshift).value - cosmo.age(redshifts_major).value)
            ages_minor = 1e+3*(cosmo.age(observations[0].redshift).value - cosmo.age(redshifts_minor).value)

            ax_top = ax.twiny()
            ax_top.set_xscale('log')
            ax_top.set_xlim(xmin, xmax)
            ax_top.set_xticks(ages_major)
            ax_top.set_xticklabels([fr'${_z_}$' for _z_ in redshifts_major])
            ax_top.xaxis.set_minor_locator(FixedLocator(ages_minor))
            ax_top.tick_params(axis='both', which='major', direction='out', 
                bottom=False, top=True, left=False, right=False, length=3*lw, width=lw, labelsize=20)
            ax_top.tick_params(axis='both', which='minor', direction='out', 
                bottom=False, top=True, left=False, right=False, length=2*lw, width=lw, labelsize=20)
            ax_top.set_xlabel(r'$z$', fontsize=24)

            for axis in ['top','bottom','left','right']: 

                ax_top.spines[axis].set_linewidth(lw)

        if sfh_arguments['lookback_times'] is not None:

            ax.vlines(1e+3*(cosmo.age(sfh_arguments['redshift']).value - cosmo.age([15.0, 20.0, 100.0]).value), 
                sfh_arguments['ylimits'][0], sfh_arguments['ylimits'][1], color='lightgrey', 
                ls=':', lw=lw, alpha=1.0, zorder=0)

        sfh16, sfh50, sfh84 = np.quantile(dynesty.utils.resample_equal(sfhs.T, weights_new), [0.16, 0.50, 0.84], axis=0)

        ax.stairs(sfh50, np.append(-10.0, ages_Myr), baseline=sfh50, color=colors_5[3], lw=lw, zorder=1)
        ax.fill_between(np.append(-10.0, ages_Myr), np.append(sfh16[0], sfh16), np.append(sfh84[0], sfh84), 
            step='pre', color=colors_5[3], lw=0, alpha=0.2, zorder=0)

        ax.set_xscale('log'); ax.set_yscale('log')

        ax.set_xlim(sfh_arguments['xlimits'][0], sfh_arguments['xlimits'][1])
        ax.set_ylim(sfh_arguments['ylimits'][0], sfh_arguments['ylimits'][1])

        for axis in ['top','bottom','left','right']: 

            ax.spines[axis].set_linewidth(lw)

    # Saves the star-formation history plot figure

    plt.savefig(f'{hfile.replace(".h5", "/SFH_Plot.pdf")}', dpi=300, bbox_inches='tight')
    plt.savefig(f'{hfile.replace(".h5", "/SFH_Plot.png")}', dpi=300, bbox_inches='tight')
    plt.savefig(f'{hfile.replace(".h5", "/SFH_Plot.jpg")}', dpi=300, bbox_inches='tight')

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
        continuum = np.median(flux[:, mask], axis=1)

        mask = np.logical_and(xmin < wavelength, wavelength < xmax)

        return (np.trapezoid(flux[:, mask], x=wavelength[mask], axis=1) - continuum*(xmax - xmin))/continuum

    # Throws error for invalid line_type

    else:

        raise ValueError('The specified fit type is invalid...')

###

# Defines function for analytically deriving emission line fluxes and equivalent widths from the model spectroscopy

def derive_analytic_emission_line_properties(redshift, wavelength_Angstroms, eline_wavelength_Anstroms, 
    continuum_flux_normalized, smooth_flux_normalized, eline_flux_normalized, eline_names=None):

    # Determines emission line fluxes and rest-frame equivalent widths for all lines included in FSPS.
    # This function requires nebemlineinspec == False so that model._smooth_spec is emission-line-free.

    if eline_names is None:

        eline_names = []
        
        for wavelength in eline_wavelength_Anstroms:

            temp_eline_name = f'line_{wavelength:.2f}'

            eline_names.append(temp_eline_name.replace('.', 'p'))

    speed_of_light_Angstroms_s = float(astropy.constants.c.to(u.AA/u.s).value)

    jansky_to_cgs = float(u.Jy.to(u.erg/u.s/np.square(u.cm)/u.Hz))

    continuum_flux = continuum_flux_normalized[:, np.newaxis]

    continuum_near_elines = np.zeros_like(eline_flux_normalized)

    eline_flux_erg_s_cm2 = (maggies_to_Jy*jansky_to_cgs)*(eline_flux_normalized*continuum_flux/(1.0 + redshift))

    for index in range(continuum_near_elines.shape[0]):

        continuum_near_elines[index] = np.interp(eline_wavelength_Anstroms, wavelength_Angstroms, 
            smooth_flux_normalized[index], left=0.0, right=0.0)

    eline_ew_Angstroms = eline_flux_normalized*continuum_flux*np.square(eline_wavelength_Anstroms[np.newaxis, :])
    eline_ew_Angstroms /= np.where(continuum_near_elines > 0.0, continuum_near_elines, np.nan)
    eline_ew_Angstroms /= speed_of_light_Angstroms_s*(1.0 + redshift)

    # Defines and returns dictionary containing the derived analytic emission line properties

    dictionary = {
        name: {
            'eline_wavelengths_Anstroms': float(eline_wavelength_Anstroms[index]), 
            'eline_fluxes_erg_s_cm2': eline_flux_erg_s_cm2[:, index], 
            'eline_EWs_Angstroms': eline_ew_Angstroms[:, index],
        } for index, name in enumerate(eline_names)
    }

    return dictionary

###

# Defines function for measuring spectral indices Dn4000 and DnBalmerBreak from the model spectroscopy

def measure_spectral_indices(wavelength_Angstroms, smooth_flux_normalized):

    # Determines the spectral indices Dn4000 (Balogh et al. 1999) and DnBalmerBreak (de Graaff et al. 2025).
    # This function requires nebemlineinspec == False so that model._smooth_spec is emission-line-free.
    # Reference for DnBalmerBreak: https://www.scixplorer.org/abs/2025A%26A...701A.168D/abstract
    # Reference for Dn4000: https://www.scixplorer.org/abs/1999ApJ...527...54B/abstract

    def mean_fnu_in_window(wave_lo, wave_hi):

            mask = np.logical_and(wave_lo <= wavelength_Angstroms, wavelength_Angstroms <= wave_hi)

            if mask.sum() < 2: return np.full(smooth_flux_normalized.shape[0], np.nan)

            temp_wave = wavelength_Angstroms[mask]
            temp_flux = smooth_flux_normalized[:, mask]

            return np.trapezoid(temp_flux, x=temp_wave, axis=1)/(temp_wave[-1] - temp_wave[0])

    fnu_blue_Dn4000 = mean_fnu_in_window(3850.0, 3950.0)
    fnu_red__Dn4000 = mean_fnu_in_window(4000.0, 4100.0)

    Dn4000 = fnu_red__Dn4000/fnu_blue_Dn4000

    fnu_blue_DnBalmerBreak = mean_fnu_in_window(3620.0, 3720.0)
    fnu_red__DnBalmerBreak = mean_fnu_in_window(4000.0, 4100.0)

    DnBalmerBreak = fnu_red__DnBalmerBreak/fnu_blue_DnBalmerBreak

    # Defines and returns dictionary containing the derived spectral indices

    dictionary = {
        'Dn4000': Dn4000,
        'DnBalmerBreak': DnBalmerBreak,
    }

    return dictionary

###

# Defines function for extracting model predictions from the posterior distribution

def extract_model_predictions(model, result, observations, stellarPopulationSynthesis):

    # Loops through the chain to extract photometric and spectroscopic model predictions

    try:

        theta_labels = np.array(result['theta_labels'])

    except KeyError:

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

        predictions, mfrac = predict_Prospector(model, theta, observations, stellarPopulationSynthesis)
        predictions = [prediction.tolist() for prediction in predictions]
        smoothed_spectrum = model._smooth_spec

        temp_wavelengths = stellarPopulationSynthesis.wavelengths

        temp_flux = 1.0e-23*maggies_to_Jy*smoothed_spectrum*(astropy.constants.c.to(u.AA/u.s)/np.square(temp_wavelengths)).value

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
        coeffs = [(1.0/np.prod(ratios[:i, :], axis=0))*(np.prod(bins[1:i+1])/np.prod(bins[:i])) for i in range(N)]
        m1 = np.power(10, logmass)/np.array(coeffs).sum(axis=0)
        masses = m1*np.array(coeffs)
        sfrs = masses.T/bins.T

        age = 0.5*(np.power(10, agebins)[:, 1] + np.power(10, agebins)[:, 0])
        age = np.sum(age*masses.T, axis=1)
        age /= np.power(10, logmass)

        for index, agebin in enumerate(np.unique(agebins.flatten())[1:]): 

            if index == 0:

                temp_agebin = np.power(10, agebin)

                if temp_agebin >= 1e+7:

                    sfr_10Myr = sfrs[:, index]; break

                else:

                    sfr_10Myr = sfrs[:, index]*(temp_agebin)/1e+7

            else:

                temp_temp_agebin = temp_agebin
                temp_agebin = np.power(10, agebin)

                if temp_agebin >= 1e+7:

                    sfr_10Myr += sfrs[:, index]*(1e+7 - temp_temp_agebin)/1e+7; break

                else:

                    sfr_10Myr += sfrs[:, index]*(temp_agebin - temp_temp_agebin)/1e+7

        for index, agebin in enumerate(np.unique(agebins.flatten())[1:]): 

            if index == 0:

                temp_agebin = np.power(10, agebin)

                if temp_agebin >= 1e+8:

                    sfr_100Myr = sfrs[:, index]; break

                else:

                    sfr_100Myr = sfrs[:, index]*(temp_agebin)/1e+8

            else:

                temp_temp_agebin = temp_agebin
                temp_agebin = np.power(10, agebin)

                if temp_agebin >= 1e+8:

                    sfr_100Myr += sfrs[:, index]*(1e+8 - temp_temp_agebin)/1e+8; break

                else:

                    sfr_100Myr += sfrs[:, index]*(temp_agebin - temp_temp_agebin)/1e+8

        age = np.array(age)
        sfr_10Myr = np.array(sfr_10Myr); ssfr_10Myr = sfr_10Myr/np.power(10, logmass)
        sfr_100Myr = np.array(sfr_100Myr); ssfr_100Myr = sfr_100Myr/np.power(10, logmass)

        return age, np.power(10, logmass), sfr_10Myr, sfr_100Myr, ssfr_10Myr, ssfr_100Myr

    # Measures properties of the stellar populations for the parametric delayed-tau model

    elif 'delayed' in sfh_type.lower() or 'tau' in sfh_type.lower():

        try:

            mass = chain[:, np.where(theta_labels == 'mass')[0][0]]

        except IndexError: 

            mass = np.power(10, chain[:, np.where(theta_labels == 'logmass')[0][0]])

        tage = chain[:, np.where(theta_labels == 'tage')[0][0]]
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

        age = 1.0e+9*np.array(age)
        sfr_10Myr = np.array(sfr_10Myr); ssfr_10Myr = sfr_10Myr/mass
        sfr_100Myr = np.array(sfr_100Myr); ssfr_100Myr = sfr_100Myr/mass

        return age, mass, sfr_10Myr, sfr_100Myr, ssfr_10Myr, ssfr_100Myr

    # Measures properties of the stellar populations for the parametric constant model

    elif 'constant' in sfh_type.lower():

        try:

            mass = chain[:, np.where(theta_labels == 'mass')[0][0]]

        except IndexError: 

            mass = np.power(10, chain[:, np.where(theta_labels == 'logmass')[0][0]])

        tage = chain[:, np.where(theta_labels == 'tage')[0][0]]

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

        age = 1.0e+9*np.array(age)
        sfr_10Myr = np.array(sfr_10Myr); ssfr_10Myr = sfr_10Myr/mass
        sfr_100Myr = np.array(sfr_100Myr); ssfr_100Myr = sfr_100Myr/mass

        return age, mass, sfr_10Myr, sfr_100Myr, ssfr_10Myr, ssfr_100Myr

    # Throws error for invalid fit_type

    else:

        raise ValueError('The specified fit type is invalid...')

###

# Defines function for measuring properties of the stellar populations from the Prospector results

def measure_star_formation_history(sfh_type, result, chain, theta_labels, lookback_times):

    # Measures properties of the stellar populations for the non-parametric continuity model

    if 'bursty' in sfh_type.lower() or 'continuity' in sfh_type.lower() or 'rising' in sfh_type.lower():

        agebins = np.array(result['model_params']['agebins'])

        sfr_indices = np.array([i for i, label in enumerate(theta_labels) if label[:6] == 'logsfr'])
        logmass = chain[:, np.where(theta_labels == 'logmass')[0][0]]
        logsfr_ratios = chain[:, sfr_indices]

        N = agebins.shape[0]
        ratios = np.power(10, np.clip(logsfr_ratios, -100, +100)).T
        bins = (np.power(10, agebins[:, 1]) - np.power(10, agebins[:, 0]))
        coeffs = [(1.0/np.prod(ratios[:i, :], axis=0))*(np.prod(bins[1:i+1])/np.prod(bins[:i])) for i in range(N)]
        m1 = np.power(10, logmass)/np.array(coeffs).sum(axis=0)
        masses = m1*np.array(coeffs)
        sfrs = masses.T/bins.T

        sfhs = []

        for index, lookback_time in enumerate(lookback_times):

            try:

                sfhs.append(sfrs.T[np.where(lookback_time <= np.power(10, agebins))[0][0]])

            except IndexError:

                sfhs.append(np.zeros(sfrs.shape[0]))

        return lookback_times, np.array(sfhs)

    # Measures properties of the stellar populations for the parametric delayed-tau model

    elif 'delayed' in sfh_type.lower() or 'tau' in sfh_type.lower():

        try:

            mass = chain[:, np.where(theta_labels == 'mass')[0][0]]

        except IndexError: 

            mass = np.power(10, chain[:, np.where(theta_labels == 'logmass')[0][0]])

        tage = chain[:, np.where(theta_labels == 'tage')[0][0]]
        tau = chain[:, np.where(theta_labels == 'tau')[0][0]]

        sfhs = []

        for temp_tage, temp_mass, temp_tau in zip(tage, mass, tau):

            dictionary = {'const': 0.0, 'tage': temp_tage, 'mass': temp_mass, 'tau': temp_tau, 'sfh': 4}

            sfhs.append(prosp.plotting.sfh.parametric_sfr(times=lookback_times/1e+9, tavg=0.0, **dictionary))

        return lookback_times, np.array(sfhs).T

    # Measures properties of the stellar populations for the parametric constant model

    elif 'constant' in sfh_type.lower():

        try:

            mass = chain[:, np.where(theta_labels == 'mass')[0][0]]

        except IndexError: 

            mass = np.power(10, chain[:, np.where(theta_labels == 'logmass')[0][0]])

        tage = chain[:, np.where(theta_labels == 'tage')[0][0]]

        sfhs = []

        for temp_tage, temp_mass in zip(tage, mass):

            dictionary = {'const': 1.0, 'tage': temp_tage, 'mass': temp_mass, 'sfh': 4}

            sfhs.append(prosp.plotting.sfh.parametric_sfr(times=lookback_times/1e+9, tavg=0.0, **dictionary))

        return lookback_times, np.array(sfhs).T

    # Throws error for invalid fit_type

    else:

        raise ValueError('The specified fit type is invalid...')
    
###

# Defines function for returning theta labels and the posterior chain from a results object

def determine_theta_labels_and_chain(result):

    # Determines arrays for both theta labels and the posterior chain

    try:

        theta_labels = np.array(result['theta_labels'])

    except KeyError:

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

    return theta_labels, chain

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

    theta_labels, chain = determine_theta_labels_and_chain(result)

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

    spec_p16, spec_p50, spec_p84 = 1.0e+9*maggies_to_Jy*quantile(spec.T, q=q, weights=weights).T
    phot_p16, phot_p50, phot_p84 = 1.0e+9*maggies_to_Jy*quantile(phot.T, q=q, weights=weights).T

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
        [r'$\mathrm{EW}_{\mathrm{H}\beta+\mathrm{[OIII]}}/\mathrm{\AA}$', EWs], 
    ]

    np.save(f'{temp_path}/Dictionary_Results.npy', dictionary, allow_pickle=True)

    # Saves the second set of results...

    t = Table()
    t['age_stellar'] = age
    t['logage_stellar'] = np.log10(age)
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

                    temp_correction = 1.0e-23*maggies_to_Jy*(2.998e+18/np.square(rest_wavelengths))
                    temp_magnitude = filt.ab_mag(rest_wavelengths*(1.0 + observations[0].redshift), temp_spec*temp_correction)
                    temp_flux_nJy = 1.0e+9*maggies_to_Jy*np.power(10, temp_magnitude/(-2.5))

                    temp_photometry.append(temp_flux_nJy)

        photometry.append(temp_photometry)

    t['photometry'] = np.array(photometry)

    t.write(f'{temp_path}/Posterior_Results.fits', overwrite=True)

    # Saves the third set of results...

    t = Table()

    for i, label in enumerate(['spectrum_full']): 

        if label == 'spectrum_full': t[label] = spec

    t.write(f'{temp_path}/Posterior_Spectra.fits', overwrite=True)

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