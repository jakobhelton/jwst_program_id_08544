"""
===================================
PID08544 Reduction Pipeline Helper
===================================

The following Python script was last updated on 2026/06/10 by Jakob M. Helton.
Helper functions for reducing MIRI/LRS spectroscopy for PID08544 (JADES-GS-z14-0).
Covers Detector1 (Stage 1), Spec2 (Stage 2), and Spec3 (Stage 3) pipeline steps,
plus nod subtraction, bad-pixel cleaning, trace finding, optimal extraction,
emission-line fitting, and various emission line diagnostics.

-----------
Environment
-----------

Requires the REDUCTIONS_MIRI environment variable for the reduction root directory.

This directory must contain the following:
  - jwst_miri_psf_0002.fits (MIRI/LRS PSF model; included in data/)
  - resolving_power.csv (tabulated resolution versus wavelength; included in data/)

-------------
Usage Example
-------------

Below is the complete per-observation configuration used for the four visits from
PID08544. Copy this block into a notebook cell (or a driver script) and adapt
the coordinate shifts, masks, and directory paths for your own program.

    # Defines the directories and relevants filenames for the three sets of observations

    pathname_reductions = os.environ['REDUCTIONS_MIRI'] # Sets the environment variable

    import PID08544_Reduction_Pipeline_helper as helper # Imports all helper functions

    asn_files_suffix = 'asn_clean.json' # Defines association file suffix

    # Obs1

    asn_files_Obs1 = sorted(glob.glob(os.path.join(f'{pathname_reductions}/PID8544_Obs1/MAST/', f'*_{asn_files_suffix}')))
    asn_files_Obs1_Spec2 = [os.path.normpath(asn_file) for asn_file in asn_files_Obs1 if 'spec2' in asn_file][::-1]
    asn_files_Obs1_Spec3 = [os.path.normpath(asn_file) for asn_file in asn_files_Obs1 if 'spec3' in asn_file]

    directories_Obs1 = {
        'Base': os.path.normpath(f'{pathname_reductions}'), 
        'Obs': os.path.normpath(f'{pathname_reductions}/PID8544_Obs1/'), 
        'MAST': os.path.normpath(f'{pathname_reductions}/PID8544_Obs1/MAST/'), 
        'Uncal': os.path.normpath(f'{pathname_reductions}/PID8544_Obs1/Uncal/'), 
        'Det1': os.path.normpath(f'{pathname_reductions}/PID8544_Obs1/Stage1/'), 
        'Spec2': os.path.normpath(f'{pathname_reductions}/PID8544_Obs1/Stage2/'), 
        'Spec3': os.path.normpath(f'{pathname_reductions}/PID8544_Obs1/Stage3/'), 
        'Analysis': os.path.normpath(f'{pathname_reductions}/PID8544_Obs1/Analysis/'), 
        'Thumbnails': os.path.normpath(f'{pathname_reductions}/JADES_GSz14/thumbnails/'), 
        'AssociationFiles': None, # [asn_files_Obs1_Spec2, asn_files_Obs1_Spec3], None (default)
        'CoordinateShift': [+0.57851171, +1.61563086], # [+0.57851171, +1.61563086], None (default)
        'ColumnsToMask': None, 'RowsToMask': None, # None, None (default)
    }

    os.makedirs(directories_Obs1['Spec2'], exist_ok=True)
    os.makedirs(directories_Obs1['Spec3'], exist_ok=True)

    for asn_file in asn_files_Obs1_Spec2: shutil.copy(asn_file, directories_Obs1['Spec2'])
    for asn_file in asn_files_Obs1_Spec3: shutil.copy(asn_file, directories_Obs1['Spec3'])

    os.makedirs(directories_Obs1['Spec2'].replace('Stage2', 'Default_Pipeline_Stage2'), exist_ok=True)
    os.makedirs(directories_Obs1['Spec3'].replace('Stage3', 'Default_Pipeline_Stage3'), exist_ok=True)

    for asn_file in asn_files_Obs1_Spec2: shutil.copy(asn_file, directories_Obs1['Spec2'].replace('Stage2', 'Default_Pipeline_Stage2'))
    for asn_file in asn_files_Obs1_Spec3: shutil.copy(asn_file, directories_Obs1['Spec3'].replace('Stage3', 'Default_Pipeline_Stage3'))

    # Obs2

    asn_files_Obs2 = sorted(glob.glob(os.path.join(f'{pathname_reductions}/PID8544_Obs2/MAST/', f'*_{asn_files_suffix}')))
    asn_files_Obs2_Spec2 = [os.path.normpath(asn_file) for asn_file in asn_files_Obs2 if 'spec2' in asn_file][::-1]
    asn_files_Obs2_Spec3 = [os.path.normpath(asn_file) for asn_file in asn_files_Obs2 if 'spec3' in asn_file]

    directories_Obs2 = {
        'Base': os.path.normpath(f'{pathname_reductions}'), 
        'Obs': os.path.normpath(f'{pathname_reductions}/PID8544_Obs2/'), 
        'MAST': os.path.normpath(f'{pathname_reductions}/PID8544_Obs2/MAST/'), 
        'Uncal': os.path.normpath(f'{pathname_reductions}/PID8544_Obs2/Uncal/'), 
        'Det1': os.path.normpath(f'{pathname_reductions}/PID8544_Obs2/Stage1/'), 
        'Spec2': os.path.normpath(f'{pathname_reductions}/PID8544_Obs2/Stage2/'), 
        'Spec3': os.path.normpath(f'{pathname_reductions}/PID8544_Obs2/Stage3/'), 
        'Analysis': os.path.normpath(f'{pathname_reductions}/PID8544_Obs2/Analysis/'), 
        'Thumbnails': os.path.normpath(f'{pathname_reductions}/JADES_GSz14/thumbnails/'), 
        'AssociationFiles': None, # [asn_files_Obs2_Spec2, asn_files_Obs2_Spec3], None (default)
        'CoordinateShift': [+0.76080378, +1.66932663], # [+0.76080378, +1.66932663], None (default)
        'ColumnsToMask': None, 'RowsToMask': None, # None, None (default)
    }

    os.makedirs(directories_Obs2['Spec2'], exist_ok=True)
    os.makedirs(directories_Obs2['Spec3'], exist_ok=True)

    for asn_file in asn_files_Obs2_Spec2: shutil.copy(asn_file, directories_Obs2['Spec2'])
    for asn_file in asn_files_Obs2_Spec3: shutil.copy(asn_file, directories_Obs2['Spec3'])

    os.makedirs(directories_Obs2['Spec2'].replace('Stage2', 'Default_Pipeline_Stage2'), exist_ok=True)
    os.makedirs(directories_Obs2['Spec3'].replace('Stage3', 'Default_Pipeline_Stage3'), exist_ok=True)

    for asn_file in asn_files_Obs2_Spec2: shutil.copy(asn_file, directories_Obs2['Spec2'].replace('Stage2', 'Default_Pipeline_Stage2'))
    for asn_file in asn_files_Obs2_Spec3: shutil.copy(asn_file, directories_Obs2['Spec3'].replace('Stage3', 'Default_Pipeline_Stage3'))

    # Obs3

    asn_files_Obs3 = sorted(glob.glob(os.path.join(f'{pathname_reductions}/PID8544_Obs3/MAST/', f'*_{asn_files_suffix}')))
    asn_files_Obs3_Spec2 = [os.path.normpath(asn_file) for asn_file in asn_files_Obs3 if 'spec2' in asn_file][::-1]
    asn_files_Obs3_Spec3 = [os.path.normpath(asn_file) for asn_file in asn_files_Obs3 if 'spec3' in asn_file]

    directories_Obs3 = {
        'Base': os.path.normpath(f'{pathname_reductions}'), 
        'Obs': os.path.normpath(f'{pathname_reductions}/PID8544_Obs3/'), 
        'MAST': os.path.normpath(f'{pathname_reductions}/PID8544_Obs3/MAST/'), 
        'Uncal': os.path.normpath(f'{pathname_reductions}/PID8544_Obs3/Uncal/'), 
        'Det1': os.path.normpath(f'{pathname_reductions}/PID8544_Obs3/Stage1/'), 
        'Spec2': os.path.normpath(f'{pathname_reductions}/PID8544_Obs3/Stage2/'), 
        'Spec3': os.path.normpath(f'{pathname_reductions}/PID8544_Obs3/Stage3/'), 
        'Analysis': os.path.normpath(f'{pathname_reductions}/PID8544_Obs3/Analysis/'), 
        'Thumbnails': os.path.normpath(f'{pathname_reductions}/JADES_GSz14/thumbnails/'), 
        'AssociationFiles': None, # [asn_files_Obs3_Spec2, asn_files_Obs3_Spec3], None (default)
        'CoordinateShift': [+0.33483082, +1.88349722], # [+0.33483082, +1.88349722], None (default)
        'ColumnsToMask': None, 'RowsToMask': [243, 244, 245, 281, 282, 283], # None, None (default)
    }

    os.makedirs(directories_Obs3['Spec2'], exist_ok=True)
    os.makedirs(directories_Obs3['Spec3'], exist_ok=True)

    for asn_file in asn_files_Obs3_Spec2: shutil.copy(asn_file, directories_Obs3['Spec2'])
    for asn_file in asn_files_Obs3_Spec3: shutil.copy(asn_file, directories_Obs3['Spec3'])

    os.makedirs(directories_Obs3['Spec2'].replace('Stage2', 'Default_Pipeline_Stage2'), exist_ok=True)
    os.makedirs(directories_Obs3['Spec3'].replace('Stage3', 'Default_Pipeline_Stage3'), exist_ok=True)

    for asn_file in asn_files_Obs3_Spec2: shutil.copy(asn_file, directories_Obs3['Spec2'].replace('Stage2', 'Default_Pipeline_Stage2'))
    for asn_file in asn_files_Obs3_Spec3: shutil.copy(asn_file, directories_Obs3['Spec3'].replace('Stage3', 'Default_Pipeline_Stage3'))

    # Obs4

    asn_files_Obs4 = sorted(glob.glob(os.path.join(f'{pathname_reductions}/PID8544_Obs4/MAST/', f'*_{asn_files_suffix}')))
    asn_files_Obs4_Spec2 = [os.path.normpath(asn_file) for asn_file in asn_files_Obs4 if 'spec2' in asn_file][::-1]
    asn_files_Obs4_Spec3 = [os.path.normpath(asn_file) for asn_file in asn_files_Obs4 if 'spec3' in asn_file]

    directories_Obs4 = {
        'Base': os.path.normpath(f'{pathname_reductions}'), 
        'Obs': os.path.normpath(f'{pathname_reductions}/PID8544_Obs4/'), 
        'MAST': os.path.normpath(f'{pathname_reductions}/PID8544_Obs4/MAST/'), 
        'Uncal': os.path.normpath(f'{pathname_reductions}/PID8544_Obs4/Uncal/'), 
        'Det1': os.path.normpath(f'{pathname_reductions}/PID8544_Obs4/Stage1/'), 
        'Spec2': os.path.normpath(f'{pathname_reductions}/PID8544_Obs4/Stage2/'), 
        'Spec3': os.path.normpath(f'{pathname_reductions}/PID8544_Obs4/Stage3/'), 
        'Analysis': os.path.normpath(f'{pathname_reductions}/PID8544_Obs4/Analysis/'), 
        'Thumbnails': os.path.normpath(f'{pathname_reductions}/JADES_GSz14/thumbnails/'), 
        'AssociationFiles': None, # [asn_files_Obs4_Spec2, asn_files_Obs4_Spec3], None (default)
        'CoordinateShift': [+0.21278994, +1.49675700], # [+0.21278994, +1.49675700], None (default)
        'ColumnsToMask': [9, 10, 11], 'RowsToMask': [281, 282, 283], # None, None (default)
    }

    os.makedirs(directories_Obs4['Spec2'], exist_ok=True)
    os.makedirs(directories_Obs4['Spec3'], exist_ok=True)

    for asn_file in asn_files_Obs4_Spec2: shutil.copy(asn_file, directories_Obs4['Spec2'])
    for asn_file in asn_files_Obs4_Spec3: shutil.copy(asn_file, directories_Obs4['Spec3'])

    os.makedirs(directories_Obs4['Spec2'].replace('Stage2', 'Default_Pipeline_Stage2'), exist_ok=True)
    os.makedirs(directories_Obs4['Spec3'].replace('Stage3', 'Default_Pipeline_Stage3'), exist_ok=True)

    for asn_file in asn_files_Obs4_Spec2: shutil.copy(asn_file, directories_Obs4['Spec2'].replace('Stage2', 'Default_Pipeline_Stage2'))
    for asn_file in asn_files_Obs4_Spec3: shutil.copy(asn_file, directories_Obs4['Spec3'].replace('Stage3', 'Default_Pipeline_Stage3'))

    # Runs the full (or partial) pipeline for each set of observations

    run_Stage1, run_Tweak, run_Stage2, run_Stage3 = True, True, True, True

    sigma = 3.0; bkg_subtract_list = [True, False]; mask_trace_width = 5; extraction_type = 'optimal'

    if run_Stage1:

        helper.run_pipeline_full(directories_Obs1, stage1=True, stage2=False, stage3=False, tweak=run_Tweak, sigma=sigma,
            bkg_subtract_list=bkg_subtract_list, mask_trace_width=mask_trace_width, offset=-1.0, zred=14.1796, 
        )

        helper.run_pipeline_full(directories_Obs2, stage1=True, stage2=False, stage3=False, tweak=run_Tweak, sigma=sigma,
            bkg_subtract_list=bkg_subtract_list, mask_trace_width=mask_trace_width, offset=+1.0, zred=14.1796, 
        )

        helper.run_pipeline_full(directories_Obs3, stage1=True, stage2=False, stage3=False, tweak=run_Tweak, sigma=sigma,
            bkg_subtract_list=bkg_subtract_list, mask_trace_width=mask_trace_width, offset=+3.0, zred=14.1796, 
        )

        helper.run_pipeline_full(directories_Obs4, stage1=True, stage2=False, stage3=False, tweak=run_Tweak, sigma=sigma,
            bkg_subtract_list=bkg_subtract_list, mask_trace_width=mask_trace_width, offset=-1.0, zred=14.1796, 
        )
        
    for bkg_subtract in bkg_subtract_list:

        if run_Stage2:

            helper.run_pipeline_full(directories_Obs1, stage1=False, stage2=True, stage3=False, tweak=run_Tweak, sigma=sigma,
                bkg_subtract_list=[bkg_subtract], mask_trace_width=mask_trace_width, offset=-1.0, zred=14.1796, 
            )

            helper.run_pipeline_full(directories_Obs2, stage1=False, stage2=True, stage3=False, tweak=run_Tweak, sigma=sigma,
                bkg_subtract_list=[bkg_subtract], mask_trace_width=mask_trace_width, offset=+1.0, zred=14.1796, 
            )

            helper.run_pipeline_full(directories_Obs3, stage1=False, stage2=True, stage3=False, tweak=run_Tweak, sigma=sigma,
                bkg_subtract_list=[bkg_subtract], mask_trace_width=mask_trace_width, offset=+3.0, zred=14.1796, 
            )

            helper.run_pipeline_full(directories_Obs4, stage1=False, stage2=True, stage3=False, tweak=run_Tweak, sigma=sigma,
                bkg_subtract_list=[bkg_subtract], mask_trace_width=mask_trace_width, offset=-1.0, zred=14.1796, 
            )

        if run_Stage3:

            helper.run_pipeline_full(directories_Obs1, stage1=False, stage2=False, stage3=True, tweak=run_Tweak, sigma=sigma,
                bkg_subtract_list=[bkg_subtract], extra_directories_for_spec3=[], 
                mask_trace_width=mask_trace_width, 
                offset=-1.0, zred=14.1796, 
            )

            helper.run_pipeline_full(directories_Obs2, stage1=False, stage2=False, stage3=True, tweak=run_Tweak, sigma=sigma,
                extraction_type=extraction_type, bkg_subtract_list=[bkg_subtract], extra_directories_for_spec3=[
                directories_Obs3, directories_Obs4], mask_trace_width=mask_trace_width, 
                offset=+1.0, zred=14.1796, 
            )

            helper.run_pipeline_full(directories_Obs3, stage1=False, stage2=False, stage3=True, tweak=run_Tweak, sigma=sigma,
                extraction_type=extraction_type, bkg_subtract_list=[bkg_subtract], extra_directories_for_spec3=[
                directories_Obs4, directories_Obs2], mask_trace_width=mask_trace_width, 
                offset=+3.0, zred=14.1796, 
            )

            helper.run_pipeline_full(directories_Obs4, stage1=False, stage2=False, stage3=True, tweak=run_Tweak, sigma=sigma,
                extraction_type=extraction_type, bkg_subtract_list=[bkg_subtract], extra_directories_for_spec3=[
                directories_Obs2, directories_Obs3], mask_trace_width=mask_trace_width, 
                offset=-1.0, zred=14.1796, 
            )
"""

###

# Use conda env config vars set CRDS_CONTEXT=jwst_XXXX.pmap to manually update the context map for a given environment

# Files were downloaded using scripts provided by the MAST JWST Search at https://mast.stsci.edu/search/ui/#/jwst
# One script was produced for each of the three sets of observations.
# We changed privileges for the final and ran it in terminal.

# chmod +x Download_PID08544_Obs1.sh
# ./Download_PID08544_Obs1.sh

# chmod +x Download_PID08544_Obs2.sh
# ./Download_PID08544_Obs2.sh

# chmod +x Download_PID08544_Obs3.sh
# ./Download_PID08544_Obs3.sh

# chmod +x Download_PID08544_Obs4.sh
# ./Download_PID08544_Obs4.sh

###

# Import necessary miscellaneous modules

import os
import sys
import glob
import json
import time
import shutil
import logging
import warnings

from datetime import datetime

# Imports necessary science modules

import lmfit
import scipy
import numpy as np
import pyneb as pn
import pandas as pd
import seaborn as sns
import dynesty
import corner

import specutils
from specutils.manipulation import box_smooth, gaussian_smooth
from specutils.manipulation import FluxConservingResampler, LinearInterpolatedResampler

import photutils
from photutils.background import Background2D, MeanBackground, MedianBackground, SExtractorBackground

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import AutoLocator, AutoMinorLocator, FixedLocator, MaxNLocator, MultipleLocator
matplotlib.rcParams['text.usetex'] = True

import astropy
from astropy import units as u
from astropy.cosmology import FlatLambdaCDM
from astropy.coordinates import FK5, ICRS, SkyCoord
from astropy.convolution import Box1DKernel, convolve
from astropy.visualization import ImageNormalize, MinMaxInterval, ZScaleInterval
from astropy.visualization import LogStretch, SinhStretch, LinearStretch, AsymmetricPercentileInterval
from astropy.modeling import models, fitting
from astropy.nddata import StdDevUncertainty
from astropy.stats import sigma_clip, SigmaClip
from astropy.table import Table
from astropy.wcs import WCS
from astropy.io import fits

from dust_attenuation.averages import C00

os.environ['CRDS_PATH'] = '{}/crds_cache'.format(os.environ.get('HOME'))
os.environ['CRDS_SERVER_URL'] = 'https://jwst-crds.stsci.edu'

import crds

import jwst
from jwst import datamodels
from jwst.extract_1d import Extract1dStep
from jwst.associations import asn_from_list as afl
from jwst.associations.lib.rules_level2_base import DMSLevel2bBase
from jwst.associations.lib.rules_level3_base import DMS_Level3_Base
from jwst.pipeline import Detector1Pipeline, Spec2Pipeline, Spec3Pipeline

import jwst.extract_1d.source_location as source_location

import stdatamodels
from stcal.alignment import util
from stdatamodels.jwst import datamodels
from stdatamodels.jwst.datamodels import dqflags

# Defines the standard cosmology from Planck18
# Reference: https://www.scixplorer.org/abs/2020A&A...641A...6P/abstract

cosmo = FlatLambdaCDM(H0=67.4, Om0=0.315, Tcmb0=2.726)

# Testing pipeline imports

print(
    f'\n',
    f'JWST Pipeline Path: {jwst.__path__}\n\n',
    f'JWST Pipeline Version: {jwst.__version__}\n',
    f'Calibration References Data System (CRDS) Version: {crds.__version__}\n',
    f'Calibration References Data System (CRDS) Context Map: {crds.get_context_name('jwst')}',
)

# Defines the intrinsic ratio for Halpha divided by Hbeta and [OIII]5007 divided by [OIII]4959 using PyNeb

H1 = pn.RecAtom('H', 1)

C3 = pn.Atom('C', 3)
N3 = pn.Atom('N', 3)
O3 = pn.Atom('O', 3)

Te, ne = 1.0e+4, 1.0e+2

emissivity_Hbeta = H1.getEmissivity(tem=Te, den=ne, wave=4861)
emissivity_O3_4959 = O3.getEmissivity(tem=Te, den=ne, wave=4959)
emissivity_O3_5007 = O3.getEmissivity(tem=Te, den=ne, wave=5007)
emissivity_Halpha = H1.getEmissivity(tem=Te, den=ne, wave=6563)

Balmer_decrement = emissivity_Halpha/emissivity_Hbeta

O3_ratio = emissivity_O3_5007/emissivity_O3_4959

# Defines some relevant variables, constants, and hyperparameters

c_kms = astropy.constants.c.to('km/s').value # speed of light, in units of km/s

rest_wave_O2__3727 = 3727.092e+0 # Angstroms, rest-frame
rest_wave_O2__3729 = 3729.875e+0 # Angstroms, rest-frame
rest_wave_Ne3_3869 = 3869.860e+0 # Angstroms, rest-frame
rest_wave_Ne3_3968 = 3968.140e+0 # Angstroms, rest-frame
rest_wave_He1_3971 = 3971.198e+0 # Angstroms, rest-frame
rest_wave_He1_4027 = 4027.329e+0 # Angstroms, rest-frame
rest_wave_Hd__4103 = 4102.860e+0 # Angstroms, rest-frame
rest_wave_Hg__4342 = 4341.647e+0 # Angstroms, rest-frame
rest_wave_O3__4363 = 4364.436e+0 # Angstroms, rest-frame
rest_wave_He1_4471 = 4472.735e+0 # Angstroms, rest-frame
rest_wave_He2_4686 = 4686.688e+0 # Angstroms, rest-frame
rest_wave_Hb__4863 = 4862.683e+0 # Angstroms, rest-frame
rest_wave_O3__4959 = 4960.295e+0 # Angstroms, rest-frame
rest_wave_O3__5007 = 5008.239e+0 # Angstroms, rest-frame
rest_wave_He1_5876 = 5877.243e+0 # Angstroms, rest-frame
rest_wave_O1__6300 = 6300.304e+0 # Angstroms, rest-frame
rest_wave_O1__6364 = 6363.776e+0 # Angstroms, rest-frame
rest_wave_N2__6548 = 6549.860e+0 # Angstroms, rest-frame
rest_wave_Ha__6565 = 6564.614e+0 # Angstroms, rest-frame
rest_wave_N2__6583 = 6585.270e+0 # Angstroms, rest-frame
rest_wave_S2__6716 = 6718.290e+0 # Angstroms, rest-frame
rest_wave_S2__6731 = 6732.680e+0 # Angstroms, rest-frame

dictionary_elines_rest_wave = { # Angstroms, rest-frame
    'rest_wave_O2__3727': rest_wave_O2__3727,
    'rest_wave_O2__3729': rest_wave_O2__3729,
    'rest_wave_Ne3_3869': rest_wave_Ne3_3869,
    'rest_wave_Ne3_3968': rest_wave_Ne3_3968,
    'rest_wave_He1_3971': rest_wave_He1_3971,
    'rest_wave_He1_4027': rest_wave_He1_4027,
    'rest_wave_Hd__4103': rest_wave_Hd__4103,
    'rest_wave_Hg__4342': rest_wave_Hg__4342,
    'rest_wave_O3__4363': rest_wave_O3__4363,
    'rest_wave_He1_4471': rest_wave_He1_4471,
    'rest_wave_He2_4686': rest_wave_He2_4686,
    'rest_wave_Hb__4863': rest_wave_Hb__4863,
    'rest_wave_O3__4959': rest_wave_O3__4959,
    'rest_wave_O3__5007': rest_wave_O3__5007,
    'rest_wave_He1_5876': rest_wave_He1_5876,
    'rest_wave_O1__6300': rest_wave_O1__6300,
    'rest_wave_N2__6548': rest_wave_N2__6548,
    'rest_wave_Ha__6565': rest_wave_Ha__6565,
    'rest_wave_N2__6583': rest_wave_N2__6583,
    'rest_wave_S2__6716': rest_wave_S2__6716,
    'rest_wave_S2__6731': rest_wave_S2__6731,
}

cmap = sns.color_palette('flare_r', as_cmap=True)

colors_8 = sns.color_palette('husl', 8)
colors_7 = sns.color_palette('husl', 7)
colors_6 = sns.color_palette('husl', 6)
colors_5 = sns.color_palette('husl', 5)
colors_4 = sns.color_palette('husl', 4)
colors_3 = sns.color_palette('husl', 3)
colors_2 = sns.color_palette('husl', 2)
colors_1 = sns.color_palette('husl', 1)

# Defines both the PSF and resolving power

if os.environ.get('REDUCTIONS_MIRI') is not None:

    pathname_reductions = os.environ['REDUCTIONS_MIRI']

    # Defines relevant MIRI/LRS PSF information from the pipeline's reference file

    model_psf = datamodels.SpecPsfModel(f'{pathname_reductions}/jwst_miri_psf_0002.fits')

    wave_psf, psf, center_col, subpix = model_psf.wave, model_psf.data, model_psf.meta.psf.center_col, model_psf.meta.psf.subpix

    N = psf.shape[0]; x = np.array(range(psf.shape[1]))

    fwhms_pixels, fwhms_arcseconds = [], []

    for i in range(N):
        
        y = psf[i, :]
        
        peak_value = np.nanmax(y)

        half_maximum = peak_value/2.0
        
        peak_indices = np.where(y == peak_value)[0]
        
        if len(peak_indices) > 0: peak_index = peak_indices[0]
        else: peak_index = 0

        left_indices = np.where(y[:peak_index] <= half_maximum)[0]
        
        if len(left_indices) > 0: left_index = left_indices[-1]
        else: left_index = 0 # If no point found, use the first point

        right_indices = np.where(y[peak_index:] <= half_maximum)[0]
        
        if len(right_indices) > 0: right_index = peak_index + right_indices[0]
        else: right_index = len(y) - 1

        fwhm_pixels = (x[right_index] - x[left_index])/subpix; fwhm_arcseconds = +0.11*fwhm_pixels

        fwhms_pixels.append(fwhm_pixels); fwhms_arcseconds.append(fwhm_arcseconds)

    wavelength_psf = np.array(wave_psf)
    temp_fwhms_pixels = np.array(fwhms_pixels)
    temp_fwhms_arcseconds = np.array(fwhms_arcseconds)

    temp_condition_psf = ~np.isnan(wavelength_psf)

    temp_data_psf = np.c_[wavelength_psf, temp_fwhms_pixels, temp_fwhms_arcseconds][temp_condition_psf][::-1]

    np.savetxt(f'{pathname_reductions}/jwst_miri_psf_0002.txt', temp_data_psf)

    # Defines spectral resolving power of the MIRI/LRS
    # Fits a line to the resolving power as a function of wavelength
    # Reference: https://www.scixplorer.org/abs/2015PASP..127..623K/abstract

    df = pd.read_csv(f'{pathname_reductions}/resolving_power.csv')

    Rs = np.c_[
        df['x'].values.tolist(), # wavelength, microns
        df[' y'].values.tolist(), # resolving power
    ]

    line = models.Linear1D()
    fit = fitting.LinearLSQFitter()
    fitted_line = fit(line, Rs[:, 0], Rs[:, 1])

else:

    warnings.warn(
        'REDUCTIONS_MIRI environment variable is not set. '
        'Thus, the PSF and resolving power versus wavelength are both unavailable; '
        'get_resolving_power() and emission_line_fitting() will both fail at call time.',
        ImportWarning, stacklevel=2,
    )

###

# https://jwst-pipeline.readthedocs.io/en/latest/jwst/pipeline/calwebb_detector1.html

def run_detector1_pipeline(directories, custom_steps=None):

    """
    Run the Detector1 pipeline on uncal files.

    Parameters:
    -----------
    directories : dict
        Dictionary of directories
    custom_steps : dict, optional
        Dictionary with custom step parameters

    Returns:
    --------
    list : List of output rate files
    """

    uncal_files = sorted(glob.glob(os.path.join(directories['Uncal'], '*_uncal.fits')))

    # Removes files that were used for target acquisition (02101) and verification (3102)

    uncal_files = [file for file in uncal_files if '_02101_' not in os.path.basename(file)]
    uncal_files = [file for file in uncal_files if '_03102_' not in os.path.basename(file)]

    if not uncal_files:

        print('No UNCAL files found!')

        return []

    # Default configuration with optimal settings for ultra-deep observations

    det1_config = {
        'refpix': { # https://jwst-pipeline.readthedocs.io/en/latest/jwst/refpix/index.html
            'skip': True,
        },
        'jump': { # https://jwst-pipeline.readthedocs.io/en/latest/jwst/jump/index.html
            'skip': False,
            'find_showers': True, # Detect cosmic ray showers
            'maximum_cores': 'half', # Use multiple cores; default value is '1'
            'rejection_threshold': '3.0', # Decreased threshold to more aggressively flag bad pixels; default value is '4.0'
            'three_group_rejection_threshold': '5.0', # Decreased threshold; default value is '6.0'
            'four_group_rejection_threshold': '5.0', # Decreased threshold; default value is '5.0'
            'min_jump_to_flag_neighbors': '5.0', # Decreased threshold; default value is '10.0'
            'only_use_ints': False, # Suggestion by Mike Regan
            'expand_large_events': True, # Suggestion by Javier Alvarez-Marquez and Pierluigi Rinaldi
        },
        'ramp_fit': { # https://jwst-pipeline.readthedocs.io/en/latest/jwst/ramp_fitting/index.html
            'skip': False,
            'maximum_cores': 'half',
        },
    }

    # Update with custom steps if provided

    if custom_steps:

        for step, params in custom_steps.items():

            if step in det1_config:

                det1_config[step].update(params)

    # Run pipeline on each file

    rate_files = []

    for i, file in enumerate(uncal_files):

        filename = os.path.basename(file)

        if i == 0: 

            t0 = time.time()

            print(f'Processing {i+1}/{len(uncal_files)}: {filename} at time {t0}')

        else:

            t1 = time.time()

            print(f'Processing {i+1}/{len(uncal_files)}: {filename} at time {t1}', 
                f' ({t1-t0} seconds elapsed since previous checkpoint)')

            t0 = t1

        try:

            log = logging.getLogger()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler = logging.FileHandler(f'{directories['Det1']}/___Detector1Pipeline___.log')
            handler.setFormatter(formatter)
            log.addHandler(handler)

            Detector1Pipeline.call(
                file,
                steps=det1_config,
                save_results=True,
                output_dir=directories['Det1'],
            )

            # Locate the output rate file

            base_name = os.path.splitext(filename)[0].replace('_uncal', '')
            rate_file = os.path.join(directories['Det1'], f'{base_name}_rate.fits')

            if os.path.exists(rate_file):

                rate_files.append(rate_file)

                print(f'  Created: {os.path.basename(rate_file)}')

            else:

                print(f'  WARNING: Expected output file not found: {os.path.basename(rate_file)}')

        except Exception as e:

            print(f'  ERROR processing {filename}: {str(e)}')

    print(f'Detector1 processing complete. Created {len(rate_files)} rate files.')

    return rate_files

###

def inspect_files(pathname, filenames):

    """
    Inspect and visualize rate or cal files.

    Parameters:
    -----------
    pathname : str
        Path name for base directory of rate or cal files
    filenames : list
        List of file names for rate or cal files
    """

    if not filenames:

        print('No rate or cal files to inspect!')
        return

    # Loop through the list of file names for rate or cal files

    for temp_index, filename in enumerate(filenames):

        try:

            if pathname is None: _temp_filename_ = filename
            else: _temp_filename_ = f'{pathname}/{filename}'

            with fits.open(f'{_temp_filename_}') as hdul:

                sci_data = hdul['SCI'].data
                err_data = hdul['ERR'].data
                dq_data = hdul['DQ'].data if 'DQ' in hdul else None

                # Plot the science data

                plt.close()
                fig = plt.figure(figsize=(12, 8))
                grid = fig.add_gridspec(1, 2, hspace=0.06, wspace=0.06)

                suptitle = _temp_filename_.split('/')[-1]

                fig.suptitle(fr'$\texttt{{{suptitle}}}$', x=0.515, y=0.915, fontsize=20)

                for index, axis in enumerate(grid):

                    if index == 0: data = sci_data; title = r'$\mathrm{SCI\ Extension}$'
                    else: data = err_data; title = r'$\mathrm{ERR\ Extension}$'

                        #

                    ax = plt.subplot(axis)
                    ax.set_title(title, fontsize=20, pad=12)
                    ax.set_xticks([]); ax.set_yticks([]); ax.set_xticklabels([]); ax.set_yticklabels([])

                    #

                    norm = ImageNormalize(
                        vmin=+0.0, vmax=np.nanmax(data), 
                        stretch=LogStretch(), interval=ZScaleInterval())
                    temp_image = ax.imshow(data, norm=norm, cmap=cmap, origin='lower', interpolation='nearest')

                    cbar = fig.colorbar(temp_image, ax=ax, location='bottom', shrink=1.0, pad=0.035)

                    cbar.ax.tick_params(axis='both', which='major', direction='out', left=True, right=True, 
                        length=8, width=3, labelsize=16)
                    cbar.ax.tick_params(axis='both', which='minor', direction='out', left=True, right=True, 
                        length=6, width=3, labelsize=16)

                    if 'rate' in filename:

                        cbar.set_label(r'$\mathrm{Surface\ Brightness\ \left[ DN/s \right]}$', fontsize=20, labelpad=6)

                    elif 'cal' in filename:

                        cbar.set_label(r'$\mathrm{Surface\ Brightness\ \left[ MJy/sr \right]}$', fontsize=20, labelpad=6)

                    else:

                        cbar.set_label(r'$\mathrm{Surface\ Brightness\ \left[ Unknown \right]}$', fontsize=20, labelpad=6)

                    cbar.ax.xaxis.set_major_locator(plt.MaxNLocator(2))

                    cbar.ax.xaxis.set_tick_params(pad=12)

                    cbar_ticklabels = cbar.ax.get_xticklabels()

                    for temp_xticklabel in cbar_ticklabels: temp_xticklabel.set_va('center_baseline')

                    #

                    x_array, y_array = [300, 350, 350, 300, 300], [5, 5, 395, 395, 5]
                    ax.plot(x_array, y_array, c=colors_5[3], ls='-', lw=3, alpha=1.0, 
                        label=r'$\mathrm{Approximate\ Location\ of\ LRS/Slit}$')

                    handles, labels = ax.get_legend_handles_labels(); ordering = [0]
                    handles, labels = [handles[i] for i in ordering], [labels[i] for i in ordering]
                    legend = plt.legend(handles, labels, loc='upper center', ncol=1, fontsize=16, framealpha=1)
                    legend.get_frame().set_edgecolor('k')
                    legend.get_frame().set_linewidth(3)

                    #

                    for axis in ['top','bottom','left','right']: 

                        cbar.outline.set_linewidth(3); ax.spines[axis].set_linewidth(3)

                if pathname is None:

                    plt.savefig(f'{filename.replace('fits', 'pdf')}', dpi=300, bbox_inches='tight')
                    plt.savefig(f'{filename.replace('fits', 'png')}', dpi=300, bbox_inches='tight')
                    plt.savefig(f'{filename.replace('fits', 'jpg')}', dpi=300, bbox_inches='tight')

                else:

                    plt.savefig(f'{pathname}/{filename.replace('fits', 'pdf')}', dpi=300, bbox_inches='tight')
                    plt.savefig(f'{pathname}/{filename.replace('fits', 'png')}', dpi=300, bbox_inches='tight')
                    plt.savefig(f'{pathname}/{filename.replace('fits', 'jpg')}', dpi=300, bbox_inches='tight')

        except Exception as e:

            print(f'Error inspecting {filename.split('/')[-1]}: {str(e)}')

###

def tweak_reference_coordinates(filenames, coordinate_shift, offset_additional=(+0.0, +0.0), write_suffix='_tweak_rate.fits'):

    """
    This function updates the header's V2_REF/V3_REF in the rate files and writes new files.

    Parameters
    ----------
    filenames : list of str
        Paths to rate FITS files to modify (the function writes new files, does not overwrite originals).
    coordinate_shift : tuple (dx, dy)
        Shift in pixels to apply to V2 and V3 (will be converted to arcsec using 0.11 arcsec/pixel).
    offset_additional : tuple (ox, oy), optional
        Additional offset (pixels) to add to the shift before converting to arcsec.
    write_suffix : str, optional
        Suffix used for the written filename (default: '_tweak_rate.fits').
    """

    PIX2ARC = +0.11 # arcseconds/pixel for JWST/MIRI

    for filename in filenames:

        try:

            print(f'Processing: {filename.split('/')[-1]}')

            # Read the filename via datamodels to get meta.wcsinfo if present

            datamodel = datamodels.open(filename)

            # Sets up conversion functions

            v23_to_ideal = stdatamodels.jwst.transforms.V2V3ToIdeal(
                datamodel.meta.wcsinfo.v3yangle,
                datamodel.meta.wcsinfo.v2_ref,
                datamodel.meta.wcsinfo.v3_ref,
                datamodel.meta.wcsinfo.vparity,
            )

            ideal_to_v23 = stdatamodels.jwst.transforms.IdealToV2V3(
                datamodel.meta.wcsinfo.v3yangle,
                datamodel.meta.wcsinfo.v2_ref,
                datamodel.meta.wcsinfo.v3_ref,
                datamodel.meta.wcsinfo.vparity,
            )

            # Change v2 and v3 to ideal (x, y) coordinates in order to apply the shift

            reference_x, reference_y = v23_to_ideal(datamodel.meta.wcsinfo.v2_ref, datamodel.meta.wcsinfo.v3_ref)

            reference_x -= ((coordinate_shift[0] + offset_additional[0])*PIX2ARC) # shift plus additional offset, converted to arcseconds
            reference_y -= ((coordinate_shift[1] + offset_additional[1])*PIX2ARC) # shift plus additional offset, converted to arcseconds

            # Convert back to v2 and v3 from ideal (x, y) coordinates in order to write out the updated rate file

            new_v2, new_v3 = ideal_to_v23(reference_x, reference_y)

            with fits.open(filename) as hdul:

                hdul['SCI'].header['V2_REF'] = new_v2
                hdul['SCI'].header['V3_REF'] = new_v3

                filename_output = filename.replace('_rate.fits', write_suffix)

                if filename == filename_output: filename_output = filename.replace('.fits', write_suffix)

                hdul.writeto(filename_output, overwrite=True)

            print(f'Wrote tweaked file: {filename_output.split('/')[-1]}'); print()

        except Exception as e:

            print(f'Failed to tweak {filename.split('/')[-1]}: {e}'); print()

###

def get_nod_positions_from_wcs(filenames_nod1, filenames_nod2, verbose=True):

    """
    Derives the nod positions in cross-dispersion pixel space from the WCS in the 
    cal or assign_wcs files WCS and using the target RA/DEC stored in the metadata.

    Parameters
    ----------
    filenames_nod1 : list of str
        Paths to cal or assign_wcs files for the first nod position
    filenames_nod2 : list of str
        Paths to cal or assign_wcs files for the second nod position
    verbose : bool
        Whether or not to print the derived nod positions for each file

    Returns
    -------
    position_nod1 : float
        Median cross-dispersion pixel position for the first nod position
    position_nod2 : float
        Median cross-dispersion pixel position for the second nod position
    """

    def find_source_pixel(filename):

        model = datamodels.open(filename)

        target_ra = model.meta.target.ra # degrees
        target_dec = model.meta.target.dec # degrees

        bbox = model.meta.wcs.bounding_box

        x0, x1 = bbox[0] # cross-dispersion (column) direction
        y0, y1 = bbox[1] # dispersion (row) direction

        # Sample cross-dispersion axis at the midpoint of the dispersion axis

        y_mid = (y0 + y1)/2.0
        x_samples = np.linspace(x0, x1, int(1e+3))

        separations = np.full(x_samples.shape, np.inf)

        for i, x in enumerate(x_samples):

            try:

                result = model.meta.wcs(x, y_mid)

                ra_out, dec_out  = result[0], result[1]

                if ra_out is not None and np.isfinite(ra_out):

                    separations[i] = np.sqrt(
                        np.square((ra_out-target_ra)*np.cos(np.radians(target_dec)))+
                        np.square(dec_out-target_dec)
                    )

            except Exception:

                pass

        best_x = x_samples[np.argmin(separations)]

        model.close()

        return best_x - x0

    #

    if filenames_nod1 is None:

        raise ValueError(f'Invalid input: {filenames_nod1} (Must not be None).')

    elif filenames_nod2 is None:

        positions_nod1 = [find_source_pixel(f) for f in filenames_nod1]

        position_nod1 = np.median(positions_nod1)

        return position_nod1

    elif filenames_nod2 is not None:

        positions_nod1 = [find_source_pixel(f) for f in filenames_nod1]
        positions_nod2 = [find_source_pixel(f) for f in filenames_nod2]

        position_nod1 = np.median(positions_nod1)
        position_nod2 = np.median(positions_nod2)

        if verbose:

            print(f'Derived nod positions from WCS:')
            print(f'  Nod 1 (all files): {[f'{p:.2f}' for p in positions_nod1]}')
            print(f'  Nod 2 (all files): {[f'{p:.2f}' for p in positions_nod2]}')
            print(f'  Nod 1 (median value) = {position_nod1:.2f}')
            print(f'  Nod 2 (median value) = {position_nod2:.2f}')

        return position_nod1, position_nod2

###

def clean_rate_files(pathname, filenames, sigma_lower_threshold=3.0, sigma_upper_threshold=3.0, max_iterations=int(1e+1), 
    columns_to_mask=None, rows_to_mask=None, mask_trace_width=5):

    """
    This function cleans the rate files by combining all of the available exposures and sigma clipping.

    Parameters
    ----------
    pathname : str
        Path name for base directory of rate files
    filenames : list of str
        Paths to rate FITS files to modify (the function writes new files, does not overwrite originals).
    sigma_lower_threshold : float
        The lower threshold to be used for sigma clipping the available exposures.
    sigma_upper_threshold : float
        The upper threshold to be used for sigma clipping the available exposures.
    max_iterations : int
        The maximum number of iterations to be used for sigma clipping.
    columns_to_mask : list of int
        Detector columns to flag as DO_NOT_USE due to contamination.
    rows_to_mask : list of int
        Detector rows to flag as DO_NOT_USE due to contamination.
    mask_trace_width : int
        Half-width of the mask around the trace in units of JWST/MIRI pixels (0.11 arcsec/pixel)

    Returns:
    --------
    list : List of output cleaned rate files
    """

    # Defines the approximate location of the cutout box to be used

    DO_NOT_USE = dqflags.pixel['DO_NOT_USE']

    print(f'Cleaning rate files...')

    try:

        with datamodels.open(filenames[0]) as temp_datamodel: bbox = temp_datamodel.meta.wcs.bounding_box

        x0, x1 = bbox[0] # cross-dispersion (column) direction
        y0, y1 = bbox[1] # dispersion (row) direction

        xsize, ysize = int(np.round(x1 - x0)), int(np.round(y1 - y0))

    except Exception:

        x0, x1 = +303, +347 # cross-dispersion (column) direction
        y0, y1 =   +7, +394 # dispersion (row) direction

        xsize, ysize = int(np.round(x1 - x0)), int(np.round(y1 - y0))

    # Defines the number of exposures per nod and integrations per exposure to be used

    try:

        temp_filename = filenames[0]

        exposures_per_nod = len(filenames) // 2

        if 'tweak' in temp_filename: filename_rateints = temp_filename.replace('_tweak_rate.fits', '_rateints.fits')
        else: filename_rateints = temp_filename.replace('_rate.fits', '_rateints.fits')

        with datamodels.open(filename_rateints) as temp_datamodel: 

            integrations_per_exposure = temp_datamodel.shape[0]

    except Exception:

        exposures_per_nod, integrations_per_exposure = 4, 23

        # Four exposures per nod position per visit; 23 integrations per exposure for PID08544

    for temp_filenames in [filenames[0::2], filenames[1::2]]:

        cutout_dq = np.zeros((ysize, xsize, exposures_per_nod, integrations_per_exposure), dtype=int)
        cutout_data = np.zeros((ysize, xsize, exposures_per_nod, integrations_per_exposure))
        cutout_error = np.zeros((ysize, xsize, exposures_per_nod, integrations_per_exposure))
        cutout_var_rnoise = np.zeros((ysize, xsize, exposures_per_nod, integrations_per_exposure))
        cutout_var_poisson = np.zeros((ysize, xsize, exposures_per_nod, integrations_per_exposure))

        for i, filename in enumerate(temp_filenames):

            output = jwst.assign_wcs.AssignWcsStep.call(filename, save_results=True, output_dir=pathname)

            if 'tweak' in filename:

                filename_assign_wcs = filename.replace('_tweak_rate.fits', '_tweak_assignwcsstep.fits')
                filename_rateints = filename.replace('_tweak_rate.fits', '_rateints.fits')

            else:

                filename_assign_wcs = filename.replace('_rate.fits', '_assignwcsstep.fits')
                filename_rateints = filename.replace('_rate.fits', '_rateints.fits')

            position_nod = get_nod_positions_from_wcs([filename_assign_wcs], None, verbose=True)

            position_nod_low = int(np.round(position_nod - mask_trace_width))
            position_nod_upp = int(np.round(position_nod + mask_trace_width))

            datamodel = datamodels.open(filename_rateints)

            number_of_ints = datamodel.shape[0]

            temp_dq = datamodel.dq.copy()
            temp_data = datamodel.data.copy()
            temp_error = datamodel.err.copy()
            temp_var_rnoise = datamodel.var_rnoise.copy()
            temp_var_poisson = datamodel.var_poisson.copy()

            datamodel.close()

            for j in range(number_of_ints):

                temp_data_int = temp_dq[j, :, :]
                temp_cutout = temp_data_int[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))]
                cutout_dq[:, :, i, j] = temp_cutout

                temp_data_int = temp_data[j, :, :]
                temp_cutout = temp_data_int[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))]
                cutout_data[:, :, i, j] = temp_cutout

                temp_data_int = temp_error[j, :, :]
                temp_cutout = temp_data_int[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))]
                cutout_error[:, :, i, j] = temp_cutout

                temp_data_int = temp_var_rnoise[j, :, :]
                temp_cutout = temp_data_int[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))]
                cutout_var_rnoise[:, :, i, j] = temp_cutout

                temp_data_int = temp_var_poisson[j, :, :]
                temp_cutout = temp_data_int[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))]
                cutout_var_poisson[:, :, i, j] = temp_cutout

        if columns_to_mask is not None:

            for column in columns_to_mask:

                if column >= x0: 

                    column -= int(np.round(x0))

                if 0 <= column < xsize:

                    cutout_data[:, column, :, :] = np.nan
                    cutout_var_rnoise[:, column, :, :] = np.nan
                    cutout_var_poisson[:, column, :, :] = np.nan

                else:

                    print(f'WARNING: column {column} is out of bounds for the cutout box and will not be masked.')

        if rows_to_mask is not None:

            for row in rows_to_mask:

                if row >= y0: 

                    row -= int(np.round(y0))

                if 0 <= row < ysize:

                    cutout_data[row, position_nod_low:position_nod_upp+1, :, :] = np.nan
                    cutout_var_rnoise[row, position_nod_low:position_nod_upp+1, :, :] = np.nan
                    cutout_var_poisson[row, position_nod_low:position_nod_upp+1, :, :] = np.nan

                else:

                    print(f'WARNING: row {row} is out of bounds for the cutout box and will not be masked.')

        sigma_clipping = SigmaClip(
            sigma_lower=sigma_lower_threshold,
            sigma_upper=sigma_upper_threshold,
            maxiters=max_iterations,
            cenfunc='median',
            stdfunc='mad_std',
        )

        stack = cutout_data.reshape(ysize, xsize, -1)
        stack_sigma_clipped = sigma_clipping(stack, axis=2)

        stack_sigma_clipped_mask = stack_sigma_clipped.mask

        stack_sigma_clipped_indices = np.where(stack_sigma_clipped_mask)

        row_indices = stack_sigma_clipped_indices[0]
        col_indices = stack_sigma_clipped_indices[1]
        stack_indices = stack_sigma_clipped_indices[2]

        file_indices = stack_indices // integrations_per_exposure
        integration_indices = stack_indices % integrations_per_exposure

        stack_sigma_clipped_indices_4d = (
            row_indices, # Y-axis index (from original 3D index [0])
            col_indices, # X-axis index (from original 3D index [1])
            file_indices, # File index (newly calculated)
            integration_indices, # Integration index (newly calculated)
        )

        cutout_dq[stack_sigma_clipped_indices_4d] = DO_NOT_USE
        cutout_data[stack_sigma_clipped_indices_4d] = np.nan
        cutout_error[stack_sigma_clipped_indices_4d] = np.nan
        cutout_var_rnoise[stack_sigma_clipped_indices_4d] = np.nan
        cutout_var_poisson[stack_sigma_clipped_indices_4d] = np.nan

        for i, filename in enumerate(temp_filenames):

            datamodel = datamodels.open(filename)

            final_slope = np.zeros((ysize, xsize))
            final_error  = np.zeros((ysize, xsize))
            final_var_rnoise = np.zeros((ysize, xsize))
            final_var_poisson = np.zeros((ysize, xsize))

            cutout_data_3d = cutout_data[:, :, i, :] # (Y, X, Int, Exp)
            cutout_var_rnoise_3d = cutout_var_rnoise[:, :, i, :] # (Y, X, Int, Exp)
            cutout_var_poisson_3d = cutout_var_poisson[:, :, i, :] # (Y, X, Int, Exp)

            cutout_var_total_3d = cutout_var_rnoise_3d + cutout_var_poisson_3d

            cutout_weights_3d = 1.0/cutout_var_total_3d
            numerator_terms_3d = cutout_data_3d*cutout_weights_3d 

            sum_of_weights = np.nansum(cutout_weights_3d, axis=2) # Shape (Y, X)
            sum_of_numerator = np.nansum(numerator_terms_3d, axis=2) # Shape (Y, X)

            with np.errstate(divide='ignore', invalid='ignore'):

                final_slope = sum_of_numerator/sum_of_weights

                var_combined = 1.0/sum_of_weights
                final_error = np.sqrt(var_combined)
                final_var_rnoise = 1.0/np.nansum(1.0/cutout_var_rnoise_3d, axis=2)
                final_var_poisson = 1.0/np.nansum(1.0/cutout_var_poisson_3d, axis=2)

            bad_pixel_mask = np.isnan(final_slope)
            bad_pixel_indices = np.where(bad_pixel_mask)
            temp_dq = datamodel.dq[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))].copy()
            temp_dq[bad_pixel_indices] |= DO_NOT_USE

            datamodel.dq[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = temp_dq
            datamodel.data[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = final_slope
            datamodel.err[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = final_error
            datamodel.var_rnoise[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = final_var_rnoise
            datamodel.var_poisson[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = final_var_poisson

            datamodel.save(filename.replace('_rate.fits', '_clean_rate.fits'))

            datamodel.close()

    filenames_clean = [filename.replace('_rate.fits', '_clean_rate.fits') for filename in filenames]

    cutouts_data = np.zeros((ysize, xsize, len(filenames_clean)))

    for i, filename_clean in enumerate(filenames_clean):

        datamodel = datamodels.open(filename_clean)

        temp_dq, temp_data = datamodel.dq.copy(), datamodel.data.copy()

        temp_cutout = temp_data[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))].copy()
        temp_cutout_dq = temp_dq[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))].copy()
        bad_pixel_mask = np.where(np.bitwise_and(temp_cutout_dq, DO_NOT_USE).astype(bool))
        temp_cutout[bad_pixel_mask] = np.nan
        cutouts_data[:, :, i] = temp_cutout

        datamodel.close()

    step_size = 0 # Default of 3 for a seven-row window (2*step_size + 1)

    new_bad_pixels = np.zeros_like(cutouts_data)

    if columns_to_mask is not None:

        for column in columns_to_mask:

            if column >= x0: 

                column -= int(np.round(x0))

            if 0 <= column < xsize:

                new_bad_pixels[:, column, :] = 1

                cutouts_data[:, column, :] = np.nan

            else:

                print(f'WARNING: column {column} is out of bounds for the cutout box and will not be masked.')

    if rows_to_mask is not None:

        for row in rows_to_mask:

            if row >= y0: 

                row -= int(np.round(y0))

            if 0 <= row < ysize:

                new_bad_pixels[row, position_nod_low:position_nod_upp+1, :] = 1

                cutouts_data[row, position_nod_low:position_nod_upp+1, :] = np.nan

            else:

                print(f'WARNING: row {row} is out of bounds for the cutout box and will not be masked.')

    if False: # Set to True if you would like additional per-row sigma-clipping

        for y in range(ysize):

            step_lower = int(np.amax([0, y-step_size]))
            step_upper = int(np.amin([ysize, y+step_size+1]))

            step_data = cutouts_data[step_lower:step_upper, :, :].copy()

            for z in range(max_iterations):

                step_data_median = np.nanmedian(step_data)
                step_data_madstd = astropy.stats.mad_std(step_data, ignore_nan=True)

                cut_lower = step_data_median - sigma_lower_threshold*step_data_madstd
                cut_upper = step_data_median + sigma_upper_threshold*step_data_madstd

                new_bad_pixel_indices = np.where(np.logical_or(step_data < cut_lower, cut_upper < step_data))

                if len(new_bad_pixel_indices[0]) == 0: break

                step_data[new_bad_pixel_indices] = np.nan

                new_bad_pixels[step_lower+new_bad_pixel_indices[0], new_bad_pixel_indices[1], new_bad_pixel_indices[2]] = 1

        for i, filename_clean in enumerate(filenames_clean):

            datamodel = datamodels.open(filename_clean)

            temp_dq = datamodel.dq[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))].copy()
            temp_data = datamodel.data[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))].copy()

            temp_dq[np.where(new_bad_pixels[:, :, i])] |= DO_NOT_USE; temp_data[np.where(new_bad_pixels[:, :, i])] = np.nan

            datamodel.data[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = temp_data

            datamodel.dq[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = temp_dq

            datamodel.save(filename_clean)

            datamodel.close()

    for x in range(xsize):

        for y in range(ysize):

            pixel_data = cutouts_data[y, x, :].copy()

            for z in range(max_iterations):

                pixel_data_median = np.nanmedian(pixel_data)
                pixel_data_madstd = astropy.stats.mad_std(pixel_data, ignore_nan=True)

                if pixel_data_madstd == 0.0 or not np.isfinite(pixel_data_madstd): break

                cut_lower = pixel_data_median - sigma_lower_threshold*pixel_data_madstd
                cut_upper = pixel_data_median + sigma_upper_threshold*pixel_data_madstd

                outlier_mask = np.logical_or(pixel_data < cut_lower, cut_upper < pixel_data)

                if not np.any(outlier_mask): break

                pixel_data[outlier_mask] = np.nan

                new_bad_pixels[y, x, outlier_mask] = 1

    for i, filename_clean in enumerate(filenames_clean):

        datamodel = datamodels.open(filename_clean)

        temp_dq = datamodel.dq[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))].copy()
        temp_data = datamodel.data[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))].copy()

        temp_dq[np.where(new_bad_pixels[:, :, i])] |= DO_NOT_USE; temp_data[np.where(new_bad_pixels[:, :, i])] = np.nan

        datamodel.data[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = temp_data

        datamodel.dq[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = temp_dq

        datamodel.save(filename_clean)

        datamodel.close()

    print(f'Number of new bad pixels found = {int(np.sum(new_bad_pixels))}')
    print(f'Total number of pixels used = {int(xsize*ysize*len(filenames_clean))}')
    print(f'Fraction of pixels masked = {np.sum(new_bad_pixels)/int(xsize*ysize*len(filenames_clean)):.5f}')
    print()

    return filenames_clean

###

def create_level2_associations(pathname, filenames, suffix='asn.json'):

    """
    Create Level 2 associations for background subtraction.

    Parameters:
    -----------
    pathname : str
        Path name for base directory of rate files
    filenames : list
        List of file names for rate files
    suffix : str
        Suffix for association files

    Returns:
    --------
    list : List of association files
    """

    # Ensure we have absolute paths

    if pathname is not None:

        filenames = [f'{pathname}/{filename}' for filename in filenames]

    if len(filenames) < 2:

        print('Need at least 2 files to create nod pairs for background subtraction'); return []

    # For the MIRI/LRS slit observing mode with standard two-point nod
    # Background subtraction involves pairing each exposure with its complementary nod position

    association_files = []

    # Determine nod pairs using exposure numbers
    # In standard observing, nod positions alternate (ABAB pattern)

    for i, filename in enumerate(filenames):

        # Create the Level 2 association 

        print(f'Creating association for {os.path.basename(filename)}')

        association_file = f'{os.path.splitext(filename)[0].split("_mirimage_")[0]}_spec2_{suffix}'

        association = afl.asn_from_list([f'{filename}'], rule=DMSLevel2bBase, product_name='Stage2')

        program_number = int(os.path.basename(filename).split('jw')[1][0:5])
        obs_number = int(os.path.basename(filename).split('jw')[1][5:8])

        association['program'] = f'Program_ID_JWST{program_number:05d}'
        association['asn_id'] = f'Obs{obs_number:03d}'

        association['asn_type'] = 'Stage2/Spec2'
        association['target'] = 't001'

        association['products'][0]['members'][0]['exposerr'] = 'null'

        for background_filename in filenames[(i+1)%2::2]:

            association['products'][0]['members'].append({
                'expname': os.path.normpath(background_filename),
                'exptype': 'background',
                'exposerr': 'null',
            })

        association['products'][0]['name'] = os.path.basename(filename).replace('.fits', '')

        # Write the association to a json file

        _, serialized = association.dump()

        with open(association_file, 'w') as output_file:

            output_file.write(serialized)

        association_files.append(association_file)

        print(f'  Created association file: {os.path.basename(association_file)}')

    return association_files

###

# https://jwst-pipeline.readthedocs.io/en/latest/jwst/pipeline/calwebb_spec2.html

def run_spec2_pipeline(pathname, filenames, bkg_subtract=True, offset=+1.0):

    """
    Run the Spec2 pipeline on Level 2 associations.

    Parameters:
    -----------
    pathname : str
        Path name for base directory of rate files
    filenames : list
        List of association or rates files
    bkg_subtract : bool
        Background subtraction boolean
    offset : float
        Visit offset for the trace in units of JWST/MIRI pixels, or 0.11 arcseconds

    Returns:
    --------
    list : List of calibrated files
    """

    print(f'Background Subtraction: {bkg_subtract}\n')

    if not os.path.exists(pathname):

        os.mkdir(pathname)

    # Default configuration

    temp_time = time.time()

    spec2_config = {
        'extract_1d':{ # https://jwst-pipeline.readthedocs.io/en/latest/jwst/extract_1d/index.html
            'subtract_background': False,
            'use_source_posn': True,
            'model_nod_pair': True,
        },
        'pathloss':{ # https://jwst-pipeline.readthedocs.io/en/latest/jwst/pathloss/index.html
            'skip': False,
            'source_type': 'POINT', # Other options include 'EXTENDED'
            'user_slit_loc': +0.11*offset, # This is in units of arcseconds
        },
        'srctype': { # https://jwst-pipeline.readthedocs.io/en/latest/jwst/srctype/index.html
            'skip': False,
            'source_type': 'POINT', # Other options include 'EXTENDED'
        },
        'assign_wcs':{ # https://jwst-pipeline.readthedocs.io/en/latest/jwst/assign_wcs/index.html
            'save_results': True,
        },
        'bkg_subtract':{ # https://jwst-pipeline.readthedocs.io/en/latest/jwst/background_subtraction/index.html
            'save_results': True,
            'skip': not bkg_subtract,
            'save_combined_background': True,
        },
    }

    # Run pipeline on each association

    cal_files = []

    if bkg_subtract:

        for i, association_file in enumerate(filenames):

            association_filename = os.path.basename(association_file)

            if i == 0:

                t0 = time.time()

                print(f'Processing {i+1}/{len(filenames)}: {association_filename} at time {t0}')

            else:

                t1 = time.time()

                print(f'Processing {i+1}/{len(filenames)}: {association_filename} at time {t1}', 
                    f'({t1-t0} seconds elapsed since previous checkpoint)')

                t0 = t1

            try:

                log = logging.getLogger()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler = logging.FileHandler(f'{pathname}/___Spec2Pipeline___.log')
                handler.setFormatter(formatter)
                log.addHandler(handler)

                Spec2Pipeline.call(
                    association_file,
                    steps=spec2_config,
                    save_results=True,
                    output_dir=pathname,
                )

                # Find the output cal file

                with open(association_file, 'r') as file:

                    association_data = json.load(file)

                # Get the science target name

                sci_filename = None

                for member in association_data['products'][0]['members']:

                    if member['exptype'] == 'science':

                        sci_filename = os.path.basename(member['expname'])

                        break

                if sci_filename:

                    base_name = os.path.splitext(sci_filename)[0].replace('_rate', '')

                    cal_file = os.path.join(pathname, f'{base_name}_cal.fits')

                    if os.path.exists(cal_file):

                        cal_files.append(cal_file)

                        print(f'  Created: {os.path.basename(cal_file)}')

                    elif os.path.exists(cal_file.replace('_tweak_clean', '')):

                        cal_files.append(cal_file.replace('_tweak_clean', ''))

                        print(f'  Created: {os.path.basename(cal_file.replace('_tweak_clean', ''))}')

                    elif os.path.exists(cal_file.replace('_tweak', '')):

                        cal_files.append(cal_file.replace('_tweak', ''))

                        print(f'  Created: {os.path.basename(cal_file.replace('_tweak', ''))}')

                    elif os.path.exists(cal_file.replace('_clean', '')):

                        cal_files.append(cal_file.replace('_clean', ''))

                        print(f'  Created: {os.path.basename(cal_file.replace('_clean', ''))}')

                    else:

                        print(f'  WARNING: Expected output file not found: {os.path.basename(cal_file)}')
                else:

                    print('  WARNING: Could not determine science file from association')

            except Exception as e:

                print(f'  ERROR processing {association_filename}:\n  {str(e)}')

    else:

        for i, rates_file in enumerate(filenames):

            rates_filename = os.path.basename(rates_file)

            print(f'Processing {i+1}/{len(filenames)}: {rates_filename}')

            try:

                log = logging.getLogger()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler = logging.FileHandler(f'{pathname}/___Spec2Pipeline___.log')
                handler.setFormatter(formatter)
                log.addHandler(handler)

                Spec2Pipeline.call(
                    rates_file,
                    steps=spec2_config,
                    save_results=True,
                    output_dir=pathname,
                )

                # Find the output cal file

                cal_file = os.path.join(pathname, rates_filename.replace('rate', 'cal'))

                if os.path.exists(cal_file):

                    cal_files.append(cal_file)
                    print(f'  Created: {os.path.basename(cal_file)}')

            except Exception as e:

                print(f'  ERROR processing {rates_filename}:\n  {str(e)}')

    print(f'\nSpec2 processing complete in {time.time() - temp_time:.1f} seconds. Created {len(cal_files)} cal files.')

    return cal_files

###

def background_subtract_s2d(data, mask=None, exclude_percentile=50.0, box_size=(9, 3), filter_size=(3, 3), sigma=3.0):

    """
    Subtract background from imaging data using the photutils Background2D class.

    Parameters:
    -----------
    data : array
        Two-dimensional array of imaging data, with background
    mask : array
        Two-dimensional boolean array of imaging data to be masked
    exclude_percentile : float
        Exclude boxes with at least this percentile of masked/NaN pixels
    box_size : tuple
        Box size of the 2D median filter along each axis in (ny, nx) order
    filter_size : tuple
        Window size of the 2D median filter to apply to the low-resolution background map
    sigma : float
        Number of standard deviations to be used for sigma clipping

    Returns:
    --------
    data_subtracted : array
        Two-dimensional array of imaging data, without background
    background.background : array
        Two-dimensional array of background map
    """

    sigma_clip = astropy.stats.SigmaClip(sigma=sigma, cenfunc='median', stdfunc='mad_std')

    background_estimator = MedianBackground() # SExtractorBackground(), MedianBackground(), MeanBackground()
    background = Background2D(data, mask=mask, exclude_percentile=exclude_percentile, box_size=box_size, 
        filter_size=filter_size, sigma_clip=sigma_clip, bkg_estimator=background_estimator)
    data_subtracted = data - background.background

    return data_subtracted, background.background

###

def minimization_function(scale_factor, data, bkg_master, sigma=3.0):

    """
    Defines minimization function for master background subtraction.

    Parameters:
    -----------
    scale_factor : float
        Factor that scales the master background
    data : array
        Science data that needs to be background subtracted
    bkg_master : array
        Master background data that has been pre-computed
    """

    data_flat, bkg_master_flat = data.flatten(), bkg_master.flatten()
    data_subtracted = np.square(data_flat - scale_factor*bkg_master_flat)

    sigma_clip = astropy.stats.SigmaClip(sigma=sigma, cenfunc='median', stdfunc='mad_std')
    data_subtracted_clipped = sigma_clip(data_subtracted)

    # scalar = scipy.stats.median_abs_deviation(data_subtracted_clipped)
    # scalar = np.sqrt(np.nansum(data_subtracted_clipped))

    scalar = np.nanmedian(data_subtracted_clipped)

    return scalar

###

def return_observed_wavelengths(zred=14.1796):
    
    """
    Returns observed-frame wavelengths at the provided redshift.

    Parameters:
    -----------
    zred : float
        Redshift used for calculating observed-frame wavelengths

    Returns:
    --------
    dictionary_elines_obs_wave : dict
        Dictionary of observed-frame wavelengths at the provided redshift
    """

    dictionary_elines_obs_wave = {} # microns, observed-frame

    for eline_key, eline_value in dictionary_elines_rest_wave.items():

        dictionary_elines_obs_wave[f'{eline_key.replace('rest_', '')}'] = 1e-4*eline_value*(1.0 + zred)

    return dictionary_elines_obs_wave # microns, observed-frame

###

def inspect_spectra(pathname, filenames_s2d=None, filenames_x1d=None, ellipses=False, zred=14.1796,
    colorbar='SB', offset=+1.0, bkg_dict={'box_size':(9, 3), 'filter_size':(3, 3), 'sigma':3.0},
    position_nod1=None, position_nod2=None):

    """
    Inspect and visualize rate or cal files.

    Parameters:
    -----------
    pathname : str
        Path name for base directory of rate or cal files
    filenames_s2d : list
        List of file names for s2d files
    filenames_x1d : list
        List of file names for x1d files
    ellipses : bool
        Boolean for drawing ellipses around the expected locations of prominent emission lines
    zred : float
        Assumed redshift for converting between observed-frame and rest-frame wavelengths
    colorbar : str
        Determines if surface brightnesses or signal-to-noise ratios should be plotted
    offset : float
        Visit offset for the trace in units of JWST/MIRI pixels, or 0.11 arcseconds
    bkg_dict : dict
        Dictionary of hyperparameters for the background subtraction
    position_nod1 : float
        Central trace position for Nod1 in units of JWST/MIRI pixels, or 0.11 arcseconds
    position_nod2 : float
        Central trace position for Nod2 in units of JWST/MIRI pixels, or 0.11 arcseconds
    """

    dictionary_elines = return_observed_wavelengths(zred=zred)

    list_of_line_wavelengths = [
        np.mean([dictionary_elines['wave_O2__3727'],
            dictionary_elines['wave_O2__3729']]),
        dictionary_elines['wave_Hb__4863'],
        dictionary_elines['wave_O3__4959'],
        dictionary_elines['wave_O3__5007'],
        dictionary_elines['wave_Ha__6565'],
    ]

    if not filenames_s2d and not filenames_x1d:

        print('No s2d and/or x1d files to inspect!')

        return

    elif not filenames_x1d:

        # Loop through the list of file names for the s2d files...

        for temp_index, filename_s2d in enumerate(filenames_s2d):

            if pathname is None: 

                temp_filename_s2d = filename_s2d

            else: 

                temp_filename_s2d = f'{pathname}/{filename_s2d}'

            # Opens the relevant data...

            with fits.open(f'{temp_filename_s2d}') as hdul_s2d:

                wavelength_data_s2d = np.flip(hdul_s2d['WAVELENGTH'].data, axis=0).T
                err_data = np.flip(hdul_s2d['ERR'].data, axis=0).T
                sci_data = np.flip(hdul_s2d['SCI'].data, axis=0).T

            # Start plotting the science data...

            figsizex, figsizey = 12, 12
            xmin, xmax, xstep = +4.875, +10.375, +0.125
            xticks = [+5.0, +5.5, +6.0, +6.5, +7.0, +7.5, +8.0, +8.5, +9.0, +9.5, +10.0]

            plt.close()
            fig = plt.figure(figsize=(figsizex, figsizey), constrained_layout=True)
            grid = fig.add_gridspec(3, 1, height_ratios=[1.0, 1.0, 1.0], hspace=0.1, wspace=0.1)

            suptitle = filename_s2d.split('/')[-1]
            
            fig.suptitle(fr'$\texttt{{{suptitle}}}$', x=0.515, y=1.0275, fontsize=20)

            # Clean the science data...

            if colorbar == 'SNR': data = sci_data/err_data
            else: data = sci_data

            index_xmin = max(0, np.argmin(np.absolute(np.nanmean(wavelength_data_s2d, axis=0) - xmin)) + 1)
            index_xmax = min(wavelength_data_s2d.shape[1] - 1, np.argmin(np.absolute(np.nanmean(wavelength_data_s2d, axis=0) - xmax)) + 0)
            temp_xmin = np.nanmean(wavelength_data_s2d[:, index_xmin - 1])
            temp_xmax = np.nanmean(wavelength_data_s2d[:, index_xmax + 1])
            temp_condition = np.logical_and(temp_xmin < wavelength_data_s2d, wavelength_data_s2d < temp_xmax)

            data_masked = data.copy()
            data_masked[~temp_condition] = np.nan
            data_masked_sigma_clipped = astropy.stats.sigma_clip(data_masked, sigma=3.0, 
                cenfunc='median', stdfunc='mad_std', masked=True)

            vmin_zscale, vmax_zscale = ZScaleInterval().get_limits(data_masked)
            # vmin_zscale, vmax_zscale = -1.0*np.amax([vmin_zscale, vmax_zscale]), +1.0*np.amax([vmin_zscale, vmax_zscale])
            # vmin_zscale, vmax_zscale = +1.0*np.nanmin(data_masked_sigma_clipped), +1.0*np.nanmax(data_masked_sigma_clipped)

            # Subtract the background...

            data_masked_subtracted, background_estimate = background_subtract_s2d(data_masked[0:data.shape[0], index_xmin:index_xmax],
                box_size=bkg_dict['box_size'], filter_size=bkg_dict['filter_size'], sigma=bkg_dict['sigma'])

            # Iterate through the axis grid...

            for index, axis in enumerate(grid):

                if index == 0: 

                    temp_data = data_masked[0:data.shape[0], index_xmin:index_xmax]
                    temp_title = r'$\mathrm{SCI\ Extension}$'

                elif index == 1: 

                    temp_data = background_estimate
                    temp_title = r'$\mathrm{Background\ Model}$'

                else: 

                    temp_data = data_masked_subtracted
                    temp_title = r'$\left(\mathrm{SCI\ Extension}\right) - \left(\mathrm{Background\ Model}\right)$'

                #

                ax = plt.subplot(axis)

                ax.tick_params(axis='both', which='major', direction='out', 
                    bottom=True, top=True, left=False, right=False, length=8, width=3, labelsize=16)
                ax.tick_params(axis='both', which='minor', direction='out', 
                    bottom=True, top=True, left=False, right=False, length=6, width=3, labelsize=16)

                # https://matplotlib.org/stable/plot_types/arrays/pcolormesh.html
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pcolormesh.html
                # https://discourse.julialang.org/t/heatmap-with-irregularly-spaced-grids/77259

                xx, yy = np.meshgrid(np.nanmean(wavelength_data_s2d[:, index_xmin:index_xmax], axis=0), np.arange(0, data.shape[0], 1))
                temp_image = ax.pcolormesh(xx, yy, temp_data, vmin=vmin_zscale, vmax=vmax_zscale, cmap=cmap, 
                    shading='nearest', edgecolors='face', lw=0)

                ax.set_xlim(xmin, xmax)
                ax.set_xticks(xticks); ax.set_yticks([])
                ax.xaxis.set_minor_locator(MultipleLocator(xstep))
                ax.yaxis.set_minor_locator(AutoMinorLocator(4))

                ymin, ymax = ax.get_ylim()
                bbox = {'boxstyle': 'round, pad=0.5', 'facecolor': 'w', 'edgecolor': 'k', 'linewidth':2}
                ax.text(0.5*(xmin + xmax), 0.875*ymax, temp_title, fontsize=12, color='k', 
                    ha='center', va='center', rotation=+0, bbox=bbox)

                if index == 2:

                    ax.set_xlabel(r'$\mathrm{Observed\ Wavelength}\ \left[ \mathrm{microns} \right]$', fontsize=20)

                else:

                    ax.set_xticklabels([])

                #

                if ellipses and position_nod1 is not None and position_nod2 is not None:

                    wavelengths = np.nanmean(wavelength_data_s2d, axis=0)

                    width = 3.0 # pixels

                    for line_wavelength in list_of_line_wavelengths:

                        line_index = np.argmin(np.absolute(wavelengths - line_wavelength)) + 1

                        line_width = wavelengths[int(line_index + width)] - wavelengths[int(line_index - width)]

                        Ellipse_line_nod1 = patches.Ellipse((line_wavelength, position_nod1+offset), 
                            width=line_width, height=2.0*width, color='k', lw=2, ls='-', fill=False, alpha=1.0)
                        Ellipse_line_nod2 = patches.Ellipse((line_wavelength, position_nod2+offset), 
                            width=line_width, height=2.0*width, color='k', lw=2, ls='-', fill=False, alpha=1.0)

                        ax.add_patch(Ellipse_line_nod1); ax.add_patch(Ellipse_line_nod2)

                #

                if index == 0: 

                    ax_top = ax.twiny()

                    ax_top.tick_params(axis='both', which='major', direction='out', 
                        top=True, bottom=False, right=False, left=False, length=8, width=3, labelsize=20)
                    ax_top.tick_params(axis='both', which='minor', direction='out', 
                        top=True, bottom=False, right=False, left=False, length=6, width=3, labelsize=20)

                    xlabel = fr'$\mathrm{{Rest-Frame\ Wavelength}}\ \mathrm{{at}}\ z = {zred:.2f}'
                    xlabel += fr'\ \left[ \mathrm{{microns}} \right]$'

                    ax_top.set_xlabel(xlabel, fontsize=20, labelpad=12)
                    ax_top.set_xlim(xmin/(1.0 + zred), xmax/(1.0 + zred))
                    ax_top.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(4))

                #

                for axis in ['top','bottom','left','right']: 

                    ax.spines[axis].set_linewidth(3)

                #

                if index == 2:

                    cbar = fig.colorbar(temp_image, ax=ax, location='bottom', shrink=1.0, pad=0.15)

                    cbar.ax.tick_params(axis='both', which='major', direction='out', 
                        bottom=True, top=False, left=False, right=False, length=8, width=3, labelsize=16)
                    cbar.ax.tick_params(axis='both', which='minor', direction='out', 
                        bottom=True, top=False, left=False, right=False, length=6, width=3, labelsize=16)

                    if colorbar == 'SNR':

                        cbar.set_label(r'$\mathrm{Signal-}\mathrm{to-}\mathrm{Noise\ Ratio}$', fontsize=20, labelpad=8)

                    else: 

                        cbar.set_label(r'$\mathrm{Surface\ Brightness\ \left[ MJy/sr \right]}$', fontsize=20, labelpad=8)

                    cbar.ax.xaxis.set_major_locator(plt.MaxNLocator(7))

                    cbar.ax.xaxis.set_tick_params(pad=12)

                    cbar_ticklabels = cbar.ax.get_xticklabels()

                    for temp_xticklabel in cbar_ticklabels: temp_xticklabel.set_va('center_baseline')

                    for axis in ['top','bottom','left','right']: 

                        cbar.outline.set_linewidth(3)

            # Save the files...

            if pathname is None:

                plt.savefig(f'{filename_s2d.replace('fits', 'pdf')}', dpi=300, bbox_inches='tight')
                plt.savefig(f'{filename_s2d.replace('fits', 'png')}', dpi=300, bbox_inches='tight')
                plt.savefig(f'{filename_s2d.replace('fits', 'jpg')}', dpi=300, bbox_inches='tight')

            else:

                plt.savefig(f'{pathname}/{filename_s2d.replace('fits', 'pdf')}', dpi=300, bbox_inches='tight')
                plt.savefig(f'{pathname}/{filename_s2d.replace('fits', 'png')}', dpi=300, bbox_inches='tight')
                plt.savefig(f'{pathname}/{filename_s2d.replace('fits', 'jpg')}', dpi=300, bbox_inches='tight')

    else:

        # Loop through the list of file names for the s2d and x1d files

        for temp_index, (filename_s2d, filename_x1d) in enumerate(zip(filenames_s2d, filenames_x1d)):

            if pathname is None: temp_filename_s2d = filename_s2d; temp_filename_x1d = filename_x1d
            else: temp_filename_s2d = f'{pathname}/{filename_s2d}'; temp_filename_x1d = f'{pathname}/{filename_x1d}'

            with fits.open(f'{temp_filename_s2d}') as hdul_s2d:

                wavelength_data_s2d = np.flip(hdul_s2d['WAVELENGTH'].data, axis=0).T
                err_data = np.flip(hdul_s2d['ERR'].data, axis=0).T
                sci_data = np.flip(hdul_s2d['SCI'].data, axis=0).T

            with fits.open(f'{temp_filename_x1d}') as hdul_x1d:
                
                try:

                    data_x1d = hdul_x1d['EXTRACT1D'].data

                except Exception:

                    data_x1d = hdul_x1d['COMBINE1D'].data

                column_names = data_x1d.columns.names
                flux_error_data = data_x1d[np.array(column_names)[np.char.find(column_names, 'ERROR') != -1][0]]
                wavelength_data = data_x1d.field(np.where(np.array(column_names) == 'WAVELENGTH')[0][0])
                flux_data = data_x1d.field(np.where(np.array(column_names) == 'FLUX')[0][0])

                try: EXTRXSTR, EXTRXSTP = hdul_x1d[1].header['EXTRXSTR'], hdul_x1d[1].header['EXTRXSTP']
                except Exception: EXTRXSTR, EXTRXSTP = 0, 64

            # Plot the science data...

            figsizex, figsizey = 12, 10
            xmin, xmax, xstep = +4.875, +10.375, +0.125
            xticks = [+5.0, +5.5, +6.0, +6.5, +7.0, +7.5, +8.0, +8.5, +9.0, +9.5, +10.0]

            plt.close()
            fig = plt.figure(figsize=(figsizex, figsizey), constrained_layout=True)
            grid = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.0], hspace=0.1, wspace=0.1)

            suptitle = filename_s2d.split('/')[-1]

            fig.suptitle(fr'$\texttt{{{suptitle.replace('_s2d', '')}}}$', x=0.515, y=1.0275, fontsize=20)

            for index, axis in enumerate(grid):

                if index == 0:

                    ax = plt.subplot(axis)

                    ax.tick_params(axis='both', which='major', direction='out', 
                        bottom=True, top=True, left=False, right=False, length=8, width=3, labelsize=16)
                    ax.tick_params(axis='both', which='minor', direction='out', 
                        bottom=True, top=True, left=False, right=False, length=6, width=3, labelsize=16)

                    #

                    data = sci_data

                    index_xmin = max(0, np.argmin(np.absolute(np.nanmean(wavelength_data_s2d, axis=0) - xmin)))
                    index_xmax = min(wavelength_data_s2d.shape[1] - 1, np.argmin(np.absolute(np.nanmean(wavelength_data_s2d, axis=0) - xmax)))
                    temp_xmin = np.nanmean(wavelength_data_s2d[:, index_xmin - 1])
                    temp_xmax = np.nanmean(wavelength_data_s2d[:, index_xmax + 1])
                    temp_condition = np.logical_and(temp_xmin <= wavelength_data_s2d, wavelength_data_s2d < temp_xmax)

                    data_masked = data.copy()
                    data_masked[~temp_condition] = np.nan
                    vmin_zscale, vmax_zscale = ZScaleInterval().get_limits(data_masked)
                    vmin_zscale, vmax_zscale = -1.0*np.amax([vmin_zscale, vmax_zscale]), +1.0*np.amax([vmin_zscale, vmax_zscale])

                    temp_data, background_estimate = background_subtract_s2d(data_masked[0:data.shape[0], index_xmin:index_xmax],
                        box_size=bkg_dict['box_size'], filter_size=bkg_dict['filter_size'], sigma=bkg_dict['sigma'])

                    # https://matplotlib.org/stable/plot_types/arrays/pcolormesh.html
                    # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pcolormesh.html
                    # https://discourse.julialang.org/t/heatmap-with-irregularly-spaced-grids/77259

                    xx, yy = np.meshgrid(np.nanmean(wavelength_data_s2d[:, index_xmin:index_xmax], axis=0), 
                        np.arange(0, data.shape[0], 1))
                    temp_image = ax.pcolormesh(xx, yy, temp_data, vmin=vmin_zscale, vmax=vmax_zscale, cmap=cmap, 
                        shading='nearest', edgecolors='face', lw=0)
                    ymin, ymax = ax.get_ylim()

                    # Specifies whether or not to use the default extraction profile from the pipeline's reference files

                    if False:

                        default_reference = '/Users/JakeHelton/crds_cache/references/jwst/miri/jwst_miri_extract1d_0006.json'

                        modified_reference = default_reference.replace('/Users/JakeHelton/crds_cache/references/jwst/miri/', 
                            pathname.replace('Stage1', 'Stage2'))

                        with open(default_reference) as default_reference_file:

                            default_reference_json = json.load(default_reference_file)

                        xstart = default_reference_json['apertures'][0]['xstart']
                        xstop = default_reference_json['apertures'][0]['xstop']

                        hlines = [ymax - EXTRXSTR + offset, ymax - EXTRXSTP + offset]

                        ax.hlines(hlines, xmin, xmax, colors=colors_5[3], ls='-', lw=3, alpha=1.0, zorder=2)

                    else:

                        temp_xarray = np.linspace(xmin, xmax, 1001)

                        temp_condition = np.logical_and(~np.isnan(wave_psf), ~np.isnan(fwhms_pixels))

                        interpolation = scipy.interpolate.interp1d(wave_psf[temp_condition], 
                            np.array(fwhms_pixels)[temp_condition], kind='cubic')
                        fwhms_pixels_interpolated = interpolation(temp_xarray)

                        upper_extraction = (np.mean([EXTRXSTR, EXTRXSTP]) + 
                            fwhms_pixels_interpolated*np.sqrt(2*np.log(2))+offset)*np.ones(temp_xarray.shape)
                        lower_extraction = (np.mean([EXTRXSTR, EXTRXSTP]) - 
                            fwhms_pixels_interpolated*np.sqrt(2*np.log(2))+offset)*np.ones(temp_xarray.shape)

                        ax.plot(temp_xarray, upper_extraction, c=colors_5[3], ls='-', lw=3, alpha=1.0, zorder=2)
                        ax.plot(temp_xarray, lower_extraction, c=colors_5[3], ls='-', lw=3, alpha=1.0, zorder=2)

                    ax.vlines(list_of_line_wavelengths, ymax-10+offset, ymax+offset, 
                        colors=colors_5[3], ls='-', lw=3, alpha=1.0, zorder=2)

                    ax.vlines(list_of_line_wavelengths, ymin-offset, ymin+10+offset, 
                        colors=colors_5[3], ls='-', lw=3, alpha=1.0, zorder=2)

                    #

                    ax.set_xlim(xmin, xmax)
                    ax.set_xticks(xticks); ax.set_xticklabels([]); ax.set_yticks([])
                    ax.xaxis.set_minor_locator(MultipleLocator(xstep))
                    ax.yaxis.set_minor_locator(AutoMinorLocator(4))
                    ax.set_ylim(ymin, ymax)

                    cbar = fig.colorbar(temp_image, ax=ax, location='top', shrink=1.0, pad=0.075)

                    cbar.ax.tick_params(axis='both', which='major', direction='out', 
                        bottom=False, top=True, left=False, right=False, length=8, width=3, labelsize=16)
                    cbar.ax.tick_params(axis='both', which='minor', direction='out', 
                        bottom=False, top=True, left=False, right=False, length=6, width=3, labelsize=16)

                    if colorbar == 'SNR':

                        cbar.set_label(r'$\mathrm{Signal-}\mathrm{to-}\mathrm{Noise\ Ratio}$', fontsize=20, labelpad=12)

                    else: 

                        cbar.set_label(r'$\mathrm{Surface\ Brightness\ \left[ MJy/sr \right]}$', fontsize=20, labelpad=12)

                    cbar.ax.xaxis.set_major_locator(plt.MaxNLocator(7))

                    cbar.ax.xaxis.set_tick_params(pad=12)

                    cbar_ticklabels = cbar.ax.get_xticklabels()

                    for temp_xticklabel in cbar_ticklabels: temp_xticklabel.set_va('center_baseline')

                    for axis in ['top','bottom','left','right']: 

                        ax.spines[axis].set_linewidth(3); cbar.outline.set_linewidth(3)

                else:

                    ax = plt.subplot(axis)

                    #

                    ax.set_xlabel(r'$\mathrm{Observed\ Wavelength}\ \left[ \mathrm{microns} \right]$', fontsize=20)
                    ax.set_ylabel(r'$\mathrm{Flux\ Density}\ \left[ \mathrm{\mu Jy} \right]$', fontsize=20, labelpad=8)

                    ax.tick_params(axis='both', which='major', direction='out', 
                        bottom=True, top=True, left=True, right=True, length=8, width=3, labelsize=16)
                    ax.tick_params(axis='both', which='minor', direction='out', 
                        bottom=True, top=True, left=True, right=True, length=6, width=3, labelsize=16)

                    x, y, yerr = wavelength_data, 1e+6*flux_data, 1e+6*flux_error_data
                    ax.fill_between(x, -1.0*yerr, +1.0*yerr, step='mid', color='darkgray', lw=0, alpha=0.6, zorder=1)
                    ax.plot(x, y, ds='steps-mid', c='k', lw=3, zorder=2)

                    ax.set_xlim(xmin, xmax); ax.set_xticks(xticks)
                    ax.xaxis.set_minor_locator(MultipleLocator(xstep))
                    ax.yaxis.set_minor_locator(AutoMinorLocator(4))

                    ax_top = ax.twiny()
                    ax_top.tick_params(axis='both', which='major', direction='out', 
                        top=True, bottom=False, right=False, left=False, length=8, width=3, labelsize=20)
                    ax_top.tick_params(axis='both', which='minor', direction='out', 
                        top=True, bottom=False, right=False, left=False, length=6, width=3, labelsize=20)

                    xlabel = fr'$\mathrm{{Rest-Frame\ Wavelength}}\ \mathrm{{at}}\ z = {zred:.2f}'
                    xlabel += fr'\ \left[ \mathrm{{microns}} \right]$'

                    ax_top.set_xlabel(xlabel, fontsize=20, labelpad=12)
                    ax_top.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(4))
                    ax_top.set_xlim(xmin/(1.0 + zred), xmax/(1.0 + zred))

                    xmin, xmax = ax.get_xlim()
                    ymin, ymax = ax.get_ylim()
                    xarray = np.linspace(xmin, xmax, 1001)
                    ax.plot(xarray, np.zeros(xarray.shape), c='goldenrod', ls='-', lw=3, zorder=0)

                    temp_y = y # astropy.stats.sigma_clip(y, sigma=3.0, maxiters=10, cenfunc='median', stdfunc='mad_std')
                    ymin = np.nanmin(temp_y[np.logical_and(xmin <= x, x <= xmax)])
                    ymax = np.nanmax(temp_y[np.logical_and(xmin <= x, x <= xmax)])
                    ax.set_ylim(1.1*ymin, 1.1*ymax)

                    ax.vlines(list_of_line_wavelengths, 1.1*ymin, 1.1*ymax, colors=colors_5[3], ls=':', lw=3, alpha=1.0, zorder=0)

                    for axis in ['top','bottom','left','right']: 

                        ax.spines[axis].set_linewidth(3)

            # Save the files...

            if pathname is None:

                plt.savefig(f'{filename_x1d.replace('fits', 'pdf')}', dpi=300, bbox_inches='tight')
                plt.savefig(f'{filename_x1d.replace('fits', 'png')}', dpi=300, bbox_inches='tight')
                plt.savefig(f'{filename_x1d.replace('fits', 'jpg')}', dpi=300, bbox_inches='tight')

            else:

                plt.savefig(f'{pathname}/{filename_x1d.replace('fits', 'pdf')}', dpi=300, bbox_inches='tight')
                plt.savefig(f'{pathname}/{filename_x1d.replace('fits', 'png')}', dpi=300, bbox_inches='tight')
                plt.savefig(f'{pathname}/{filename_x1d.replace('fits', 'jpg')}', dpi=300, bbox_inches='tight')

###

def clean_cal_files(filenames, sigma_lower_threshold=3.0, sigma_upper_threshold=3.0, max_iterations=int(1e+1),
    columns_to_mask=None, rows_to_mask=None, mask_trace_width=5):

    """
    This function cleans the cal files by combining all of the available exposures and sigma clipping.

    Parameters
    ----------
    filenames : list of str
        Paths to cal FITS files to modify (the function writes new files, does not overwrite originals).
    sigma_lower_threshold : float
        The lower threshold to be used for sigma clipping the available exposures.
    sigma_upper_threshold : float
        The upper threshold to be used for sigma clipping the available exposures.
    max_iterations : int
        The maximum number of iterations to be used for sigma clipping.
    columns_to_mask : list of int
        Detector columns to flag as DO_NOT_USE due to contamination.
    rows_to_mask : list of int
        Detector rows to flag as DO_NOT_USE due to contamination.
    mask_trace_width : int
        Half-width of the mask around the trace in units of JWST/MIRI pixels (0.11 arcsec/pixel)
    """

    # Defines the approximate location of the cutout box to be used

    DO_NOT_USE = dqflags.pixel['DO_NOT_USE']

    print(f'Cleaning cal files...')

    if len(filenames) < 4:

        print(f'Skipping clean_cal_files: need >= 4 files for reliable cross-exposure '
            f'sigma clipping, but only {len(filenames)} were provided.')

        return

    try:

        with datamodels.open(filenames[0]) as temp_datamodel: bbox = temp_datamodel.meta.wcs.bounding_box

        x0, x1 = bbox[0] # cross-dispersion (column) direction
        y0, y1 = bbox[1] # dispersion (row) direction

        xsize, ysize = int(np.round(x1 - x0)), int(np.round(y1 - y0))

    except Exception:

        x0, x1 = +303, +347 # cross-dispersion (column) direction
        y0, y1 =   +7, +394 # dispersion (row) direction

        xsize, ysize = int(np.round(x1 - x0)), int(np.round(y1 - y0))

    cutouts_data = np.zeros((ysize, xsize, len(filenames)))

    filenames_assign_wcs_nod1 = [filename.replace('_cal.fits', '_assign_wcs.fits') for filename in filenames[0::2]]
    filenames_assign_wcs_nod2 = [filename.replace('_cal.fits', '_assign_wcs.fits') for filename in filenames[1::2]]

    position_nod1, position_nod2 = get_nod_positions_from_wcs(filenames_assign_wcs_nod1, filenames_assign_wcs_nod2, verbose=True)

    position_nod1_low = int(np.round(position_nod1 - mask_trace_width))
    position_nod1_upp = int(np.round(position_nod1 + mask_trace_width))

    position_nod2_low = int(np.round(position_nod2 - mask_trace_width))
    position_nod2_upp = int(np.round(position_nod2 + mask_trace_width))

    for i, filename in enumerate(filenames):

        datamodel = datamodels.open(filename)

        temp_dq, temp_data = datamodel.dq.copy(), datamodel.data.copy()

        temp_cutout = temp_data[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))].copy()
        temp_cutout_dq = temp_dq[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))].copy()
        bad_pixel_mask = np.where(np.bitwise_and(temp_cutout_dq, DO_NOT_USE).astype(bool))
        temp_cutout[bad_pixel_mask] = np.nan
        cutouts_data[:, :, i] = temp_cutout

        datamodel.close()

    step_size = 0 # Default of 3 for a seven-row window (2*step_size + 1)

    new_bad_pixels = np.zeros_like(cutouts_data)

    if columns_to_mask is not None:

        for column in columns_to_mask:

            if column >= x0: 

                column -= int(np.round(x0))

            if 0 <= column < xsize:

                new_bad_pixels[:, column, :] = 1

                cutouts_data[:, column, :] = np.nan

            else:

                print(f'WARNING: column {column} is out of bounds for the cutout box and will not be masked.')

    if rows_to_mask is not None:

        for row in rows_to_mask:

            if row >= y0: 

                row -= int(np.round(y0))

            if 0 <= row < ysize:

                new_bad_pixels[row, position_nod1_low:position_nod1_upp+1, :] = 1
                new_bad_pixels[row, position_nod2_low:position_nod2_upp+1, :] = 1

                cutouts_data[row, position_nod1_low:position_nod1_upp+1, :] = np.nan
                cutouts_data[row, position_nod2_low:position_nod2_upp+1, :] = np.nan

            else:

                print(f'WARNING: row {row} is out of bounds for the cutout box and will not be masked.')

    if True:

        for y in range(ysize):

            step_lower = int(np.amax([0, y-step_size]))
            step_upper = int(np.amin([ysize, y+step_size+1]))

            step_data = cutouts_data[step_lower:step_upper, :, :].copy()

            for z in range(max_iterations):

                step_data_median = np.nanmedian(step_data)
                step_data_madstd = astropy.stats.mad_std(step_data, ignore_nan=True)

                cut_lower = step_data_median - sigma_lower_threshold*step_data_madstd
                cut_upper = step_data_median + sigma_upper_threshold*step_data_madstd

                new_bad_pixel_indices = np.where(np.logical_or(step_data < cut_lower, cut_upper < step_data))

                if len(new_bad_pixel_indices[0]) == 0: break

                step_data[new_bad_pixel_indices] = np.nan

                new_bad_pixels[step_lower+new_bad_pixel_indices[0], new_bad_pixel_indices[1], new_bad_pixel_indices[2]] = 1

        for i, filename in enumerate(filenames):

            datamodel = datamodels.open(filename)

            temp_dq = datamodel.dq[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))].copy()
            temp_data = datamodel.data[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))].copy()

            temp_dq[np.where(new_bad_pixels[:, :, i])] |= DO_NOT_USE; temp_data[np.where(new_bad_pixels[:, :, i])] = np.nan

            datamodel.data[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = temp_data

            datamodel.dq[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = temp_dq

            datamodel.save(filename)

            datamodel.close()

    for x in range(xsize):

        for y in range(ysize):

            pixel_data = cutouts_data[y, x, :].copy()

            for z in range(max_iterations):

                pixel_data_median = np.nanmedian(pixel_data)
                pixel_data_madstd = astropy.stats.mad_std(pixel_data, ignore_nan=True)

                if pixel_data_madstd == 0.0 or not np.isfinite(pixel_data_madstd): break

                cut_lower = pixel_data_median - sigma_lower_threshold*pixel_data_madstd
                cut_upper = pixel_data_median + sigma_upper_threshold*pixel_data_madstd

                outlier_mask = np.logical_or(pixel_data < cut_lower, cut_upper < pixel_data)

                if not np.any(outlier_mask): break

                pixel_data[outlier_mask] = np.nan

                new_bad_pixels[y, x, outlier_mask] = 1

    for i, filename in enumerate(filenames):

        datamodel = datamodels.open(filename)

        temp_dq = datamodel.dq[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))].copy()
        temp_data = datamodel.data[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))].copy()

        temp_dq[np.where(new_bad_pixels[:, :, i])] |= DO_NOT_USE; temp_data[np.where(new_bad_pixels[:, :, i])] = np.nan

        datamodel.data[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = temp_data

        datamodel.dq[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = temp_dq

        datamodel.save(filename)

        datamodel.close()

    print(f'Number of new bad pixels found = {int(np.sum(new_bad_pixels))}')
    print(f'Total number of pixels used = {int(xsize*ysize*len(filenames))}')
    print(f'Fraction of pixels masked = {np.sum(new_bad_pixels)/int(xsize*ysize*len(filenames)):.5f}')
    print()

###

def subtract_row_medians(filenames, sigma_lower_threshold=2.0, sigma_upper_threshold=2.0, max_iterations=int(1e+1)):

    """
    Defines function for subtracting the median row-by-row for a list of files, ideally cal files.

    Parameters:
    -----------
    filenames : list
        List of file names for subtracting the median row-by-row, ideally cal files
    sigma_lower_threshold : float
        The lower threshold to be used for sigma clipping the available exposures.
    sigma_upper_threshold : float
        The upper threshold to be used for sigma clipping the available exposures.
    max_iterations : int
        The maximum number of iterations to be used for sigma clipping.
    """

    # Opens a data model for each filename and iterates through each of the rows

    for i, filename in enumerate(filenames):

        # Calculates median and subtracts it

        datamodel = datamodels.open(filename)

        data_bbox = datamodel.meta.wcs.bounding_box

        x0, x1 = data_bbox[0]; y0, y1 = data_bbox[1]

        old_data_cutout = datamodel.data.copy()[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))]
        new_data_cutout = datamodel.data.copy()[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))]
        median_data_cutout = datamodel.data.copy()[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))]

        for row_index in range(old_data_cutout.shape[0]):

            sigma_clipping = SigmaClip(
                sigma_lower=sigma_lower_threshold,
                sigma_upper=sigma_upper_threshold,
                maxiters=max_iterations,
                cenfunc='median',
                stdfunc='mad_std',
            )

            temp_median = np.ma.median(sigma_clipping(old_data_cutout[row_index, :]))

            median_data_cutout[row_index, :] = temp_median

            new_data_cutout[row_index, :] -= temp_median

        datamodel.data[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))] = new_data_cutout

        datamodel.save(filename)

        datamodel.close()

###

# https://jwst-pipeline.readthedocs.io/en/latest/jwst/extract_1d/index.html

def find_trace(filename, psf_width=5, verbose=True):

    """
    Find the WCS-predicted trace location for a MIRI/LRS exposure.

    Reads a calibrated or assign_wcs-stage fits file and uses the WCS and
    target coordinates stored in the metadata to predict the spectral trace
    position on the detector.  The WCS for each nod exposure already encodes
    the nod pointing offset, so the same target coordinates map to a different
    detector position per nod without any manual correction from the APT file.

    Parameters:
    -----------
    filename : str
        Path to a MIRI/LRS calibrated or assign_wcs fits file
    psf_width : int, optional
        Half-width of the PSF mask in pixels; default is 5
    verbose : boolean
        Whether or not to return print statements

    Returns:
    --------
    trace_location : numpy.ndarray
        Cross-dispersion trace position at each row within the bounding box,
        relative to the left edge of the bounding box
    y_plot : numpy.ndarray
        Row indices corresponding to trace_location, relative to the bounding box
    source_offset : float
        Visit-level cross-dispersion offset in MIRI pixels; the nod component
        is removed so the value is consistent across nod positions within an
        observation and varies between observations by the APT-programmed
        visit-level pointing offset
    """

    # Open the FITS file as a JWST datamodel

    model = datamodels.open(filename)

    # Extract dispersion axis and WCS metadata

    dispaxis = model.meta.wcsinfo.dispersion_direction
    full_shape = model.data.shape[-2:]
    bbox = model.meta.wcs.bounding_box
    wcs_ref = model.meta.wcs

    # Compute the middle dispersion coordinate and the reference wavelength

    middle_disp, middle_xdisp, middle_wl = source_location.middle_from_wcs(
        wcs_ref, bbox, dispaxis)

    # Define the bounding box limits in detector coordinates

    y0 = int(np.ceil(bbox[1][0]))
    y1 = int(np.ceil(bbox[1][1]))
    x0 = int(np.ceil(bbox[0][0]))
    x1 = int(np.ceil(bbox[0][1]))

    # Project the target coordinates onto the detector using the WCS.
    # meta.target.ra/dec is the fixed catalog position; the WCS for each
    # exposure encodes the actual pointing, so backward_transform maps the
    # same target to a different detector position for each nod and visit.

    target_ra = model.meta.target.ra
    target_dec = model.meta.target.dec

    x_source, y_source = wcs_ref.backward_transform(target_ra, target_dec, middle_wl)

    if verbose:

        print(f'Target RA: {target_ra:.6f} degrees, Dec: {target_dec:.6f} degrees')
        print(f'Detector source position: x = {x_source:.3f}, y = {y_source:.3f}')

    # Compute the full trace from the WCS-predicted source position

    full_trace = source_location.trace_from_wcs(
        exp_type=model.meta.exposure.type,
        shape=full_shape,
        bounding_box=bbox,
        wcs_ref=wcs_ref,
        source_x=x_source,
        source_y=y_source,
        dispaxis=dispaxis,
    )

    # Trim the trace to the bounding box and construct PSF mask boundaries

    trace_location = full_trace[y0:y1] - x0
    y_plot = np.array(range(0, y1 - y0))

    psf_upper = trace_location.astype(int) + psf_width
    psf_lower = trace_location.astype(int) - psf_width

    max_x = x1 - x0 + 1

    psf_lower[psf_lower < 0] = 0
    psf_upper[psf_upper > max_x] = max_x

    # Visit-level cross-dispersion offset in MIRI pixels.
    # meta.dither.dithered_ra/dec is the visit center on sky (identical for
    # both nod positions within an observation, differing between observations).
    # x_offset/0.11 is the total commanded dither (visit + nod); subtracting
    # the WCS-derived nod component (x_source - x_visit_center) isolates the
    # visit-level offset.

    dithered_ra = model.meta.dither.dithered_ra
    dithered_dec = model.meta.dither.dithered_dec

    x_visit_center, _ = wcs_ref.backward_transform(dithered_ra, dithered_dec, middle_wl)

    source_offset = model.meta.dither.x_offset/0.11 - (x_source - x_visit_center)

    if verbose: print(f'Visit offset: {source_offset:.3f} pixels')

    model.close()

    return trace_location, y_plot, source_offset

###

def tapered_column_extraction(extraction_width=3.0):

    """
    Determines the FWHM as a function of wavelength for the tapered column extraction (i.e., optimal PSF extraction).

    Parameters:
    -----------
    extraction_width : float
        Extraction width scaling factor...
    """

    # https://jwst-docs.stsci.edu/jwst-mid-infrared-instrument/miri-performance/miri-point-spread-functions

    # FWHM values for each of the MIRI/Imaging PSFs

    FWHMs = np.c_[
        [ 5.589,  7.528,  9.883, 11.298, 12.712, 14.932, 17.875, 20.563, 25.147], # wavelength, microns
        [ 0.207,  0.269,  0.328,  0.375,  0.420,  0.488,  0.591,  0.674,  0.803], # FWHM, arcseconds
        [ 1.882,  2.445,  2.982,  3.409,  3.818,  4.436,  5.373,  6.127,  7.300], # FWHM, pixels
    ]

    # Fit a line to the FWHM values as a function of wavelength

    x, y = FWHMs[:, 0], FWHMs[:, 2]*(extraction_width/2.0)

    line = models.Linear1D()
    fit = fitting.LinearLSQFitter()
    fitted_line = fit(line, x, y)

    # Quick figure to visualize the fit to the FWHM values as a function of wavelength

    plt.close()
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111)

    ax.tick_params(axis='both', which='major', direction='out', 
        bottom=True, top=True, left=True, right=True, length=8, width=3, labelsize=16)
    ax.tick_params(axis='both', which='minor', direction='out', 
        bottom=True, top=True, left=True, right=True, length=6, width=3, labelsize=16)

    ax.set_xlabel(r'$\mathrm{Observed\ Wavelength}\ \left[ \mathrm{microns} \right]$', fontsize=24)
    ax.set_ylabel(r'$\mathrm{FWHM}\ \left[ \mathrm{pixels} \right]$', fontsize=24, labelpad=4)

    xmin, xmax = 3.75, 28.75
    ax.set_xlim(xmin, xmax)
    ax.set_xticks([5.0, 10.0, 15.0, 20.0, 25.0])
    ax.xaxis.set_minor_locator(MultipleLocator(1.25))

    ymin, ymax = 0.0, 16.0
    ax.set_ylim(ymin, ymax)
    ax.set_yticks([0.0, 4.0, 8.0, 12.0, 16.0])
    ax.yaxis.set_minor_locator(MultipleLocator(1.00))

    x_array = np.linspace(xmin, xmax, num=int(1e+3))
    ax.plot(x, y, c='darkturquoise', mec='darkgrey', marker='o', ms=16, mew=3, lw=3, ls='', alpha=1.0, 
        label=fr'$\mathrm{{{extraction_width/2.0:.1f} \times FWHM\ Values}}$', zorder=1)
    ax.plot(x_array, fitted_line(x_array), c='k', ls='-', lw=3, alpha=1.0, 
        label=r'$\mathrm{Best-Fit\ Line}$', zorder=0)

    handles, labels = ax.get_legend_handles_labels(); ordering = [0, 1]
    handles, labels = [handles[i] for i in ordering], [labels[i] for i in ordering]
    legend = plt.legend(handles, labels, loc='upper center', ncol=2, fontsize=16, framealpha=1)
    legend.get_frame().set_edgecolor('darkgrey')
    legend.get_frame().set_linewidth(3)

    for axis in ['top','bottom','left','right']: 

        ax.spines[axis].set_linewidth(3)

    plt.show()

    # Returns the fitted line

    return fitted_line

###

def plot_slit_overlay(directories, zred=14.1796):

    """
    Plots the slit overlays from each of the visits on an RGB cutout surrounding the target galaxy.

    Parameters:
    -----------
    directories : dict
        List of dictionaries of directories
    zred : float
        Redshift used for calculating physical sizes from angular separations
    """

    # Reads in thumbnails to overlay slit on an RGB image around the target galaxy

    try:

        F444W = fits.open(sorted(glob.glob(f'{directories[0]["Thumbnails"]}/*F444W*.fits'))[0])
        F277W = fits.open(sorted(glob.glob(f'{directories[0]["Thumbnails"]}/*F277W*.fits'))[0])
        F115W = fits.open(sorted(glob.glob(f'{directories[0]["Thumbnails"]}/*F115W*.fits'))[0])

        F444W_head, F444W_data = F444W[1].header, F444W[1].data
        F277W_head, F277W_data = F277W[1].header, F277W[1].data
        F115W_head, F115W_data = F115W[1].header, F115W[1].data

        F444W_wcs = WCS(F444W_head)
        F277W_wcs = WCS(F277W_head)
        F115W_wcs = WCS(F115W_head)

        F444W.close()
        F277W.close()
        F115W.close()

    except Exception:

        MULTI = fits.open(sorted(glob.glob(f'{directories[0]['Thumbnails']}/*.fits'))[0])

        F444W_head, F444W_data = MULTI['F444W-CLEAR'].header, MULTI['F444W-CLEAR'].data
        F277W_head, F277W_data = MULTI['F277W-CLEAR'].header, MULTI['F277W-CLEAR'].data
        F115W_head, F115W_data = MULTI['F115W-CLEAR'].header, MULTI['F115W-CLEAR'].data

        F444W_wcs = WCS(F444W_head)
        F277W_wcs = WCS(F277W_head)
        F115W_wcs = WCS(F115W_head)

        MULTI.close()

    image_R = F444W_data.copy()
    image_G = F277W_data.copy()
    image_B = F115W_data.copy()

    image_max = np.amax([np.amax(image_R), np.amax(image_G), np.amax(image_B)])
    image_min = np.amin([np.amin(image_R), np.amin(image_G), np.amin(image_B)])

    extreme = +1.25 # 1.0*np.amax([image_max, np.absolute(image_min)]) # nJy per pixel

    # Defines relevant plotting hyperparameters, i.e., pixel scale in arcsec/pixel and radius

    if True:

        pixel_scale = astropy.wcs.utils.proj_plane_pixel_scales(F444W_wcs)[0]*3600.0 # arcsec/pixel

    else:

        pixel_scale = np.sqrt(np.square(F444W_wcs.wcs.cd[0, 0]) + np.square(F444W_wcs.wcs.cd[1, 0]))*3600.0 \
            if hasattr(F444W_wcs.wcs, 'cd') and F444W_wcs.wcs.cd is not None \
            else abs(F444W_wcs.wcs.cdelt[0])*3600.0 # arcsec/pixel

    radius = 0.175/pixel_scale

    # Determines locations for the edges of the slits using the header information from the s2d files

    Coordinates = []

    for i, directory in enumerate(directories):

        temp_temp_pathname = directory['Spec2'].replace('Stage2', 'Default_Pipeline_Stage2')

        filenames_assign_wcs = sorted(glob.glob(os.path.join(temp_temp_pathname, '*assign_wcs.fits')))

        if not filenames_assign_wcs: 

            temp_temp_pathname = directory['Spec2']

            filenames_assign_wcs = sorted(glob.glob(os.path.join(temp_temp_pathname, '*assign_wcs.fits')))

        for j, filename_assign_wcs in enumerate(filenames_assign_wcs[::2]):

            model_Nod1 = datamodels.open(filename_assign_wcs)

            sregion_Nod1 = model_Nod1.meta.wcsinfo.s_region
            target_RA_Nod1 =float(model_Nod1.meta.target.ra)
            target_DEC_Nod1 = float(model_Nod1.meta.target.dec)
            nod_number_Nod1 = model_Nod1.meta.dither.position_number
            obs_number_Nod1 = model_Nod1.meta.observation.observation_number
            footprint_Nod1 = util.sregion_to_footprint(sregion_Nod1)

            slit_RAs_Nod1 = np.array(footprint_Nod1[:, 0], dtype=float)
            slit_DECs_Nod1 = np.array(footprint_Nod1[:, 1], dtype=float)
            slit_DECs_Nod1 = np.append(slit_DECs_Nod1, slit_DECs_Nod1[0]).tolist()
            slit_RAs_Nod1 = np.append(slit_RAs_Nod1, slit_RAs_Nod1[0]).tolist()

            model_Nod2 = datamodels.open(filename_assign_wcs.replace('00001', '00002'))

            sregion_Nod2 = model_Nod2.meta.wcsinfo.s_region
            target_RA_Nod2 =float(model_Nod2.meta.target.ra)
            target_DEC_Nod2 = float(model_Nod2.meta.target.dec)
            nod_number_Nod2 = model_Nod2.meta.dither.position_number
            obs_number_Nod2 = model_Nod2.meta.observation.observation_number
            footprint_Nod2 = util.sregion_to_footprint(sregion_Nod2)

            slit_RAs_Nod2 = np.array(footprint_Nod2[:, 0], dtype=float)
            slit_DECs_Nod2 = np.array(footprint_Nod2[:, 1], dtype=float)
            slit_DECs_Nod2 = np.append(slit_DECs_Nod2, slit_DECs_Nod2[0]).tolist()
            slit_RAs_Nod2 = np.append(slit_RAs_Nod2, slit_RAs_Nod2[0]).tolist()

            assert obs_number_Nod1 == obs_number_Nod2, f'Observation numbers for Nod1 and Nod2 must match.'

            ObsNumber = obs_number_Nod1

            Coordinates.append([[ObsNumber], 
                [slit_RAs_Nod1, slit_DECs_Nod1], [slit_RAs_Nod2, slit_DECs_Nod2], 
                [target_RA_Nod1, target_DEC_Nod1], [target_RA_Nod2, target_DEC_Nod2], 
            ])

    # Plots the slit on an RGB image around the target galaxy using the previously read in thumbnails

    plt.close()
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111)

    xs = np.max([image_R.shape[0], image_G.shape[0], image_B.shape[0]])
    ys = np.max([image_R.shape[1], image_G.shape[1], image_B.shape[1]])

    img = np.zeros((xs, ys, 3))

    img[:, :, 0] = image_R
    img[:, :, 1] = image_G
    img[:, :, 2] = image_B

    if False:

        img[:, :, 0] = scipy.ndimage.gaussian_filter(image_R, sigma=0.269/2.0/pixel_scale, truncate=5.0)
        img[:, :, 1] = scipy.ndimage.gaussian_filter(image_G, sigma=0.269/2.0/pixel_scale, truncate=5.0)
        img[:, :, 2] = scipy.ndimage.gaussian_filter(image_B, sigma=0.269/2.0/pixel_scale, truncate=5.0)

    img_max = np.amax(img)

    img_min = 1e+6*np.amin(img[img > 0.0])

    clipped_R = np.clip(image_R, img_min, img_max)
    clipped_G = np.clip(image_G, img_min, img_max)
    clipped_B = np.clip(image_B, img_min, img_max)

    img[:, :, 0] = 1.00*(clipped_R - img_min)/(img_max - img_min)
    img[:, :, 1] = 1.25*(clipped_G - img_min)/(img_max - img_min)
    img[:, :, 2] = 1.25*(clipped_B - img_min)/(img_max - img_min)

    if True:

        log_clipped_R = np.log10(clipped_R)
        log_clipped_G = np.log10(clipped_G)
        log_clipped_B = np.log10(clipped_B)

        img_max = np.amax([log_clipped_R, log_clipped_G, log_clipped_B])
        img_min = np.amin([log_clipped_R, log_clipped_G, log_clipped_B])

        img[:, :, 0] = 1.00*(log_clipped_R - img_min)/(img_max - img_min)
        img[:, :, 1] = 1.25*(log_clipped_G - img_min)/(img_max - img_min)
        img[:, :, 2] = 1.25*(log_clipped_B - img_min)/(img_max - img_min)

    img[img > 1.0] = 1.0; img[np.isnan(img)] = 0.0

    if False:norm = ImageNormalize(img, interval=ZScaleInterval(), stretch=LogStretch())
    else: norm = ImageNormalize(img, interval=ZScaleInterval(), stretch=LinearStretch())

    ax.imshow(img, origin='lower', aspect='equal', norm=norm)

    xmin, xmax = ax.get_xlim(); xcen = (xmax - xmin)/2.0
    ymin, ymax = ax.get_ylim(); ycen = (ymax - ymin)/2.0

    temp_factor = 8.0
    temp_xmin, temp_xmax = xcen - (xmax - xmin)/temp_factor, xcen + (xmax - xmin)/temp_factor
    temp_ymin, temp_ymax = ycen - (ymax - ymin)/temp_factor, ycen + (ymax - ymin)/temp_factor
    ax.set_xlim(temp_xmin, temp_xmax)
    ax.set_ylim(temp_ymin, temp_ymax)

    if True:

        temp_colors = sns.color_palette('husl', 2*len(Coordinates))

        for i, Coordinate in enumerate(Coordinates):

            ObsNumber = Coordinate[0][0]

            coords_slit_Nod1 = F444W_wcs.world_to_pixel(SkyCoord(Coordinate[1][0], Coordinate[1][1], frame=ICRS, unit='deg'))
            coords_slit_Nod2 = F444W_wcs.world_to_pixel(SkyCoord(Coordinate[2][0], Coordinate[2][1], frame=ICRS, unit='deg'))

            coords_target_Nod1 = F444W_wcs.world_to_pixel(SkyCoord(Coordinate[3][0], Coordinate[3][1], frame=ICRS, unit='deg'))
            coords_target_Nod2 = F444W_wcs.world_to_pixel(SkyCoord(Coordinate[4][0], Coordinate[4][1], frame=ICRS, unit='deg'))

            ax.plot(coords_slit_Nod1[0].tolist(), coords_slit_Nod1[1].tolist(), 
                color=temp_colors[2*i+0], ls='-', lw=4.5, alpha=0.5, label=fr'$\mathrm{{Obs{ObsNumber},\,Nod1}}$', zorder=i)
            ax.plot(coords_slit_Nod2[0].tolist(), coords_slit_Nod2[1].tolist(), 
                color=temp_colors[2*i+1], ls='-', lw=4.5, alpha=0.5, label=fr'$\mathrm{{Obs{ObsNumber},\,Nod2}}$', zorder=i)

            ax.plot(coords_target_Nod1[0].tolist(), coords_target_Nod1[1].tolist(), 
                color='w', ls=' ', marker='x', ms=12, mew=4.5, alpha=0.5)
            ax.plot(coords_target_Nod2[0].tolist(), coords_target_Nod2[1].tolist(), 
                color='w', ls=' ', marker='x', ms=12, mew=4.5, alpha=0.5)

    # fig.suptitle(r'\boldmath$\mathrm{JWST/NIRCam\ False-}\mathrm{Color\ RGB}$', x=0.515, y=0.945, fontsize=20)
    fig.suptitle(r'$\mathrm{JWST/NIRCam\ False-}\mathrm{Color\ RGB}$', x=0.515, y=0.945, fontsize=20)

    ax.set_xlabel(''); ax.set_ylabel('')
    ax.set_xticks([]); ax.set_yticks([])

    width = 1.0

    if True:

        ax.arrow(0.945*(temp_xmax - temp_xmin) + temp_xmin, 0.05*(temp_ymax - temp_ymin) + temp_ymin, dx=0.0, dy=+20.0, 
            width=width, head_width=3.0*width, head_length=3.0*width, color='w')
        ax.arrow(0.948*(temp_xmax - temp_xmin) + temp_xmin, 0.05*(temp_ymax - temp_ymin) + temp_ymin, dx=-20.0, dy=0.0, 
            width=width, head_width=3.0*width, head_length=3.0*width, color='w')

        ax.text(0.945*(temp_xmax - temp_xmin) + temp_xmin, 0.225*(temp_ymax - temp_ymin) + temp_ymin, r'\boldmath$\mathrm{N}$', 
            fontsize=16, color='w', ha='center', va='center')
        ax.text(0.775*(temp_xmax - temp_xmin) + temp_xmin, 0.0475*(temp_ymax - temp_ymin) + temp_ymin, r'\boldmath$\mathrm{E}$', 
            fontsize=16, color='w', ha='center', va='center')

    if False: # Whether or not to plot a scalebar in the lower left of the image

        scalebar_arcsec = 0.6; scalebar_half_pix = scalebar_arcsec/pixel_scale/2.0

        ax.errorbar(0.20*(xmax - xmin) + xmin, 0.057*(ymax - ymin) + ymin, xerr=scalebar_half_pix, yerr=0,
            marker='none', markerfacecolor='none', markeredgecolor='none', 
            color='w', lw=3, capsize=6.0, capthick=3.0)

        ax.text(0.20*(xmax - xmin) + xmin, 0.15*(ymax - ymin) + ymin, 
            fr'\boldmath${scalebar_arcsec:.1f}^{{\prime\prime}}$', 
            fontsize=16, color='w', ha='center', va='center')

        if zred is not None:

            physical_size_kpc = (scalebar_arcsec*u.arcsec/cosmo.arcsec_per_kpc_proper(zred)).to(u.kpc).value

            ax.text(0.20*(xmax - xmin) + xmin, 0.10*(ymax - ymin) + ymin, 
                fr'\boldmath${physical_size_kpc:.1f}\ \mathrm{{pkpc}}$', 
                fontsize=16, color='w', ha='center', va='center')

    handles, labels = ax.get_legend_handles_labels()
    N = len(handles); ordering = list(range(0, N, 2)) + list(range(1, N, 2))
    handles, labels = [handles[i] for i in ordering], [labels[i] for i in ordering]
    legend = ax.legend(handles, labels, loc='upper center', ncol=2, fontsize=16, framealpha=1)
    legend.get_frame().set_edgecolor('darkgrey')
    legend.get_frame().set_linewidth(3)

    # ax.legend().set_visible(True)

    for axis in ['top','bottom','left','right']:

        ax.spines[axis].set_linewidth(4.5); ax.spines[axis].set_edgecolor('dimgrey')

    plt.savefig(f'{directory['Spec2']}/Slit_Locations.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'{directory['Spec2']}/Slit_Locations.png', dpi=300, bbox_inches='tight')
    plt.savefig(f'{directory['Spec2']}/Slit_Locations.jpg', dpi=300, bbox_inches='tight')

    plt.savefig(f'{temp_temp_pathname}/Slit_Locations.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'{temp_temp_pathname}/Slit_Locations.png', dpi=300, bbox_inches='tight')
    plt.savefig(f'{temp_temp_pathname}/Slit_Locations.jpg', dpi=300, bbox_inches='tight')

    plt.show()

###

def inspect_column_and_row_sums(pathname, filenames_1, filenames_2, offset=+1.0,
    position_nod1=None, position_nod2=None):

    """
    Inspect and visualize the files by looking at the sums along the columns or rows.
    Columns correspond to the cross-dispersion or spatial direction.
    Rows correspond to the dispersion or wavelength direction.

    Parameters:
    -----------
    pathname : string
        Pathname for saving figures
    filenames_1 : list
        List of file names for input files to plot in the upper panel
    filenames_2 : list
        List of file names for input files to plot in the lower panel
    offset : float
        Visit offset for the trace in units of JWST/MIRI pixels, or 0.11 arcseconds
    position_nod1 : float
        Central trace position for Nod1 in units of JWST/MIRI pixels, or 0.11 arcseconds
    position_nod2 : float
        Central trace position for Nod2 in units of JWST/MIRI pixels, or 0.11 arcseconds
    """

    # Reads in the input files and sums along the columns and rows

    exp_numbers_Nod1_1, exp_numbers_Nod2_1, exp_numbers_Nod1_2, exp_numbers_Nod2_2 = [], [], [], []
    obs_numbers_Nod1_1, obs_numbers_Nod2_1, obs_numbers_Nod1_2, obs_numbers_Nod2_2 = [], [], [], []

    columns_sums_Nod1_1, columns_sums_Nod2_1, row_sums_Nod1_1, row_sums_Nod2_1 = [], [], [], []
    columns_sums_Nod1_2, columns_sums_Nod2_2, row_sums_Nod1_2, row_sums_Nod2_2 = [], [], [], []

    for i, filenames in enumerate([filenames_1, filenames_2]):

        for j, temp_filename in enumerate(filenames):

            model_cal = datamodels.open(temp_filename)
            bbox_cal = model_cal.meta.wcs.bounding_box
            position_number = model_cal.meta.dither.position_number
            observation_number= model_cal.meta.observation.observation_number
            exposure_number = int(model_cal.meta.observation.activity_id) // 2

            x0, x1 = bbox_cal[0]
            y0, y1 = bbox_cal[1]

            cutout_cal = model_cal.data[int(np.round(y0)):int(np.round(y1)), int(np.round(x0)):int(np.round(x1))]

            column_sum_cal = np.nansum(cutout_cal, axis=0)
            row_sum_cal = np.nansum(cutout_cal, axis=-1)

            if i == 0:

                if position_number == 1: 

                    exp_numbers_Nod1_1.append(exposure_number)
                    obs_numbers_Nod1_1.append(observation_number)
                    columns_sums_Nod1_1.append(column_sum_cal)
                    row_sums_Nod1_1.append(row_sum_cal)

                if position_number == 2: 

                    exp_numbers_Nod2_1.append(exposure_number)
                    obs_numbers_Nod2_1.append(observation_number)
                    columns_sums_Nod2_1.append(column_sum_cal)
                    row_sums_Nod2_1.append(row_sum_cal)

            elif i == 1:

                if position_number == 1: 

                    exp_numbers_Nod1_2.append(exposure_number)
                    obs_numbers_Nod1_2.append(observation_number)
                    columns_sums_Nod1_2.append(column_sum_cal)
                    row_sums_Nod1_2.append(row_sum_cal)

                if position_number == 2: 

                    exp_numbers_Nod2_2.append(exposure_number)
                    obs_numbers_Nod2_2.append(observation_number)
                    columns_sums_Nod2_2.append(column_sum_cal)
                    row_sums_Nod2_2.append(row_sum_cal)

    # Plots the sums along the columns first

    figsizex, figsizey = 12, 10

    plt.close()
    fig = plt.figure(figsize=(figsizex, figsizey), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0], width_ratios=[1.0, 1.0], hspace=0.1, wspace=0.1)
    ax1, ax2 = fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1])
    ax3, ax4 = fig.add_subplot(grid[1, 0]), fig.add_subplot(grid[1, 1])

    ax1.tick_params(axis='both', which='major', direction='out', 
        bottom=True, top=True, left=True, right=True, length=8, width=3, labelsize=16)
    ax1.tick_params(axis='both', which='minor', direction='out', 
        bottom=True, top=True, left=True, right=True, length=6, width=3, labelsize=16)

    ax2.tick_params(axis='both', which='major', direction='out', 
        bottom=True, top=True, left=True, right=True, length=8, width=3, labelsize=16)
    ax2.tick_params(axis='both', which='minor', direction='out', 
        bottom=True, top=True, left=True, right=True, length=6, width=3, labelsize=16)

    ax3.tick_params(axis='both', which='major', direction='out', 
        bottom=True, top=True, left=True, right=True, length=8, width=3, labelsize=16)
    ax3.tick_params(axis='both', which='minor', direction='out', 
        bottom=True, top=True, left=True, right=True, length=6, width=3, labelsize=16)

    ax4.tick_params(axis='both', which='major', direction='out', 
        bottom=True, top=True, left=True, right=True, length=8, width=3, labelsize=16)
    ax4.tick_params(axis='both', which='minor', direction='out', 
        bottom=True, top=True, left=True, right=True, length=6, width=3, labelsize=16)

    xmin, ymin = 0.0, 0.0

    xmax = np.amax([
        np.array(columns_sums_Nod1_1).shape[1] if len(columns_sums_Nod1_1) > 0 else 1.0,
        np.array(columns_sums_Nod2_1).shape[1] if len(columns_sums_Nod2_1) > 0 else 1.0,
        np.array(columns_sums_Nod1_2).shape[1] if len(columns_sums_Nod1_2) > 0 else 1.0,
        np.array(columns_sums_Nod2_2).shape[1] if len(columns_sums_Nod2_2) > 0 else 1.0,
    ])

    if np.any(['combined' not in temp_filename for temp_filename in filenames_2]):

        _ymax_candidates_ = [
            *([np.amax(columns_sums_Nod1_1)] if len(columns_sums_Nod1_1) > 0 else []),
            *([np.amax(columns_sums_Nod2_1)] if len(columns_sums_Nod2_1) > 0 else []),
        ]; ymax = np.amax(_ymax_candidates_) if _ymax_candidates_ else 1.0

    else:

        _ymax_candidates_ = [
            *([np.amax(columns_sums_Nod1_1)] if len(columns_sums_Nod1_1) > 0 else []),
            *([np.amax(columns_sums_Nod2_1)] if len(columns_sums_Nod2_1) > 0 else []),
            *([np.amax(columns_sums_Nod1_2)] if len(columns_sums_Nod1_2) > 0 else []),
            *([np.amax(columns_sums_Nod2_2)] if len(columns_sums_Nod2_2) > 0 else []),
        ]; ymax = np.amax(_ymax_candidates_) if _ymax_candidates_ else 1.0

    for i, temp_sums in enumerate([columns_sums_Nod1_1, columns_sums_Nod2_1]):

        temp_colors = sns.color_palette('husl', len(temp_sums))

        if i == 0: 

            temp_ax = ax1; nod_position = position_nod1

            temp_ax.set_ylabel(r'$\mathrm{Column\ Sums\ [DN/s]}$', fontsize=20)

            temp_ax.set_title(r'$\mathrm{Summed\ Values\ for\ Nod\ 1,}$' + '\n' r'$\mathrm{Before\ Nod\ Subtraction}$', 
                fontsize=20, pad=16)

        elif i == 1: 

            temp_ax = ax2; nod_position = position_nod2

            temp_ax.set_title(r'$\mathrm{Summed\ Values\ for\ Nod\ 2,}$' + '\n' r'$\mathrm{Before\ Nod\ Subtraction}$', 
                fontsize=20, pad=16)

            temp_ax.set_yticklabels([])

        for j, temp_sum in enumerate(temp_sums):

            if j % 4 == 0: temp_ls = '-'
            elif j % 4 == 1: temp_ls = '--'
            elif j % 4 == 2: temp_ls = ':'
            elif j % 4 == 3: temp_ls = (0, (3, 1, 1, 1, 1, 1))

            xarray = np.arange(len(temp_sum))

            exp_list = exp_numbers_Nod1_1 if i == 0 else exp_numbers_Nod2_1
            obs_list = obs_numbers_Nod1_1 if i == 0 else obs_numbers_Nod2_1

            temp_label = fr'$\mathrm{{Obs}}{obs_list[j]},\,\mathrm{{Nod}}{i+1},\,\mathrm{{Exp}}{exp_list[j]}$'

            temp_ax.plot(xarray, temp_sum, color=temp_colors[j], ls=temp_ls, lw=3, alpha=1.0, label=temp_label, zorder=2)

            if nod_position is not None:

                temp_ax.vlines(nod_position+offset, -1.0*ymax, +2.0*ymax, colors='dimgrey', ls='--', lw=3, alpha=1.0, zorder=0)

                if i == 0:

                    temp_ax.text(nod_position+offset+1.0, ymax/+4.0, r'$\leftarrow \mathrm{Center\ of\ Trace}$', 
                        fontsize=20, c='dimgrey', ha='left', va='center', zorder=0)

                if i == 1:

                    temp_ax.text(nod_position+offset-1.0, ymax/+4.0, r'$\mathrm{Center\ of\ Trace} \rightarrow$', 
                        fontsize=20, c='dimgrey', ha='right', va='center', zorder=0)

            temp_ax.xaxis.set_minor_locator(AutoMinorLocator(4))
            temp_ax.yaxis.set_minor_locator(AutoMinorLocator(4))

            temp_ax.set_xlim(round(-0.05*xmax, 0), round(+1.05*xmax, 0))
            temp_ax.set_ylim(ymin, round(+1.1*ymax, -2))

            temp_ax.set_xticklabels([])

    handles, labels = ax1.get_legend_handles_labels()
    legend = ax1.legend(handles, labels, loc='lower center', ncol=2, fontsize=12, framealpha=1)
    legend.get_frame().set_edgecolor('darkgrey')
    legend.get_frame().set_linewidth(3)

    handles, labels = ax2.get_legend_handles_labels()
    legend = ax2.legend(handles, labels, loc='lower center', ncol=2, fontsize=12, framealpha=1)
    legend.get_frame().set_edgecolor('darkgrey')
    legend.get_frame().set_linewidth(3)

    for i, temp_sums in enumerate([columns_sums_Nod1_2, columns_sums_Nod2_2]):

        temp_colors = sns.color_palette('husl', len(temp_sums))

        if i == 0: 

            temp_ax = ax3; nod_position = position_nod1

            temp_ax.set_ylabel(r'$\mathrm{Column\ Sums\ [DN/s]}$', fontsize=20)

            temp_ax.set_title(r'$\mathrm{Summed\ Values\ for\ Nod\ 1,}$' + '\n' r'$\mathrm{After\ Nod\ Subtraction}$', 
                fontsize=20, pad=16)

        elif i == 1: 

            temp_ax = ax4; nod_position = position_nod2

            temp_ax.set_title(r'$\mathrm{Summed\ Values\ for\ Nod\ 2,}$' + '\n' r'$\mathrm{After\ Nod\ Subtraction}$', 
                fontsize=20, pad=16)

            temp_ax.set_yticklabels([])

        for j, temp_sum in enumerate(temp_sums):

            if j % 4 == 0: temp_ls = '-'
            elif j % 4 == 1: temp_ls = '--'
            elif j % 4 == 2: temp_ls = ':'
            elif j % 4 == 3: temp_ls = (0, (3, 1, 1, 1, 1, 1))

            xarray = np.arange(len(temp_sum))

            temp_ax.plot(xarray, temp_sum, color=temp_colors[j], ls=temp_ls, lw=3, alpha=1.0, zorder=2)

            if nod_position is not None:

                temp_ax.vlines(nod_position+offset, -1.0*ymax, +2.0*ymax, colors='dimgrey', ls='--', lw=3, alpha=1.0, zorder=0)

            temp_ax.plot(np.linspace(-0.1*xmax, +1.1*xmax, 1001), np.zeros(1001), color='k', ls='-', lw=3, alpha=1.0, zorder=0)

            temp_ax.xaxis.set_minor_locator(AutoMinorLocator(4))
            temp_ax.yaxis.set_minor_locator(AutoMinorLocator(4))

            temp_ax.set_xlim(round(-0.05*xmax, 0), round(+1.05*xmax, 0))
            temp_ax.set_ylim(round(-1.1e-2*ymax, 0), round(+1.1e-2*ymax, 0))

        temp_ax.set_xlabel(r'$\mathrm{Column\ Number}$', fontsize=20)

    for axis in ['top','bottom','left','right']:

        ax1.spines[axis].set_linewidth(3.0)
        ax2.spines[axis].set_linewidth(3.0)
        ax3.spines[axis].set_linewidth(3.0)
        ax4.spines[axis].set_linewidth(3.0)

    plt.savefig(f'{pathname}/Sums_Along_Columns.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'{pathname}/Sums_Along_Columns.png', dpi=300, bbox_inches='tight')
    plt.savefig(f'{pathname}/Sums_Along_Columns.jpg', dpi=300, bbox_inches='tight')

    plt.show()

    # Plots the sums along the rows next

    figsizex, figsizey = 12, 10

    plt.close()
    fig = plt.figure(figsize=(figsizex, figsizey), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0], width_ratios=[1.0, 1.0], hspace=0.3, wspace=0.1)
    ax1, ax2 = fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1])
    ax3, ax4 = fig.add_subplot(grid[1, 0]), fig.add_subplot(grid[1, 1])

    ax1.tick_params(axis='both', which='major', direction='out', 
        bottom=True, top=True, left=True, right=True, length=8, width=3, labelsize=16)
    ax1.tick_params(axis='both', which='minor', direction='out', 
        bottom=True, top=True, left=True, right=True, length=6, width=3, labelsize=16)

    ax2.tick_params(axis='both', which='major', direction='out', 
        bottom=True, top=True, left=True, right=True, length=8, width=3, labelsize=16)
    ax2.tick_params(axis='both', which='minor', direction='out', 
        bottom=True, top=True, left=True, right=True, length=6, width=3, labelsize=16)

    ax3.tick_params(axis='both', which='major', direction='out', 
        bottom=True, top=True, left=True, right=True, length=8, width=3, labelsize=16)
    ax3.tick_params(axis='both', which='minor', direction='out', 
        bottom=True, top=True, left=True, right=True, length=6, width=3, labelsize=16)

    ax4.tick_params(axis='both', which='major', direction='out', 
        bottom=True, top=True, left=True, right=True, length=8, width=3, labelsize=16)
    ax4.tick_params(axis='both', which='minor', direction='out', 
        bottom=True, top=True, left=True, right=True, length=6, width=3, labelsize=16)

    xmin, ymin = 0.0, 0.0

    xmax = np.amax([
        np.array(row_sums_Nod1_1).shape[1] if len(row_sums_Nod1_1) > 0 else 1.0,
        np.array(row_sums_Nod2_1).shape[1] if len(row_sums_Nod2_1) > 0 else 1.0,
        np.array(row_sums_Nod1_2).shape[1] if len(row_sums_Nod1_2) > 0 else 1.0,
        np.array(row_sums_Nod2_2).shape[1] if len(row_sums_Nod2_2) > 0 else 1.0,
    ])
    _ymax_candidates_ = [
        *([np.amax(row_sums_Nod1_1)] if len(row_sums_Nod1_1) > 0 else []),
        *([np.amax(row_sums_Nod2_1)] if len(row_sums_Nod2_1) > 0 else []),
        *([np.amax(row_sums_Nod1_2)] if len(row_sums_Nod1_2) > 0 else []),
        *([np.amax(row_sums_Nod2_2)] if len(row_sums_Nod2_2) > 0 else []),
    ]; ymax = np.amax(_ymax_candidates_) if _ymax_candidates_ else 1.0

    for i, temp_sums in enumerate([row_sums_Nod1_1, row_sums_Nod2_1]):

        temp_colors = sns.color_palette('husl', len(temp_sums))

        if i == 0: 

            temp_ax = ax1

            temp_ax.set_ylabel(r'$\mathrm{Row\ Sums\ [DN/s]}$', fontsize=20)

            temp_ax.set_title(r'$\mathrm{Summed\ Values\ for\ Nod\ 1,}$' + '\n' r'$\mathrm{Before\ Nod\ Subtraction}$', 
                fontsize=20, pad=16)

        elif i == 1: 

            temp_ax = ax2

            temp_ax.set_title(r'$\mathrm{Summed\ Values\ for\ Nod\ 2,}$' + '\n' r'$\mathrm{Before\ Nod\ Subtraction}$', 
                fontsize=20, pad=16)

            temp_ax.set_yticklabels([])

        for j, temp_sum in enumerate(temp_sums):

            if j % 4 == 0: temp_ls = '-'
            elif j % 4 == 1: temp_ls = '--'
            elif j % 4 == 2: temp_ls = ':'
            elif j % 4 == 3: temp_ls = (0, (3, 1, 1, 1, 1, 1))

            xarray = np.arange(len(temp_sum))

            exp_list = exp_numbers_Nod1_1 if i == 0 else exp_numbers_Nod2_1
            obs_list = obs_numbers_Nod1_1 if i == 0 else obs_numbers_Nod2_1

            temp_label = fr'$\mathrm{{Obs}}{obs_list[j]},\,\mathrm{{Nod}}{i+1},\,\mathrm{{Exp}}{exp_list[j]}$'
            
            temp_ax.plot(xarray, temp_sum, color=temp_colors[j], ls=temp_ls, lw=3, alpha=1.0, label=temp_label, zorder=2)

            temp_ax.xaxis.set_minor_locator(AutoMinorLocator(4))
            temp_ax.yaxis.set_minor_locator(AutoMinorLocator(4))

            temp_ax.set_xlim(round(-0.05*xmax, 0), round(+1.05*xmax, 0))
            temp_ax.set_ylim(ymin, round(+1.1*ymax, -2))

            temp_ax.set_xticklabels([])

    handles, labels = ax1.get_legend_handles_labels()
    legend = ax1.legend(handles, labels, loc='lower center', ncol=2, fontsize=12, framealpha=1)
    legend.get_frame().set_edgecolor('darkgrey')
    legend.get_frame().set_linewidth(3)

    handles, labels = ax2.get_legend_handles_labels()
    legend = ax2.legend(handles, labels, loc='lower center', ncol=2, fontsize=12, framealpha=1)
    legend.get_frame().set_edgecolor('darkgrey')
    legend.get_frame().set_linewidth(3)

    for i, temp_sums in enumerate([row_sums_Nod1_2, row_sums_Nod2_2]):

        temp_colors = sns.color_palette('husl', len(temp_sums))

        if i == 0: 

            temp_ax = ax3

            temp_ax.set_ylabel(r'$\mathrm{Row\ Sums\ [DN/s]}$', fontsize=20)

            temp_ax.set_title(r'$\mathrm{Summed\ Values\ for\ Nod\ 1,}$' + '\n' r'$\mathrm{After\ Nod\ Subtraction}$', 
                fontsize=20, pad=16)

        elif i == 1: 

            temp_ax = ax4

            temp_ax.set_title(r'$\mathrm{Summed\ Values\ for\ Nod\ 2,}$' + '\n' r'$\mathrm{After\ Nod\ Subtraction}$', 
                fontsize=20, pad=16)

            temp_ax.set_yticklabels([])

        for j, temp_sum in enumerate(temp_sums):

            if j % 4 == 0: temp_ls = '-'
            elif j % 4 == 1: temp_ls = '--'
            elif j % 4 == 2: temp_ls = ':'
            elif j % 4 == 3: temp_ls = (0, (3, 1, 1, 1, 1, 1))

            xarray = np.arange(len(temp_sum))

            temp_ax.plot(xarray, temp_sum, color=temp_colors[j], ls=temp_ls, lw=3, alpha=1.0, zorder=2)

            temp_ax.plot(np.linspace(-0.1*xmax, +1.1*xmax, 1001), np.zeros(1001), color='k', ls='-', lw=3, alpha=1.0, zorder=0)

            temp_ax.xaxis.set_minor_locator(AutoMinorLocator(4))
            temp_ax.yaxis.set_minor_locator(AutoMinorLocator(4))

            temp_ax.set_xlim(round(-0.05*xmax, 0), round(+1.05*xmax, 0))
            temp_ax.set_ylim(round(-1.1e-2*ymax, 0), round(+1.1e-2*ymax, 0))

        temp_ax.set_xlabel(r'$\mathrm{Row\ Number}$', fontsize=20)

    for axis in ['top','bottom','left','right']:

        ax1.spines[axis].set_linewidth(3.0)
        ax2.spines[axis].set_linewidth(3.0)
        ax3.spines[axis].set_linewidth(3.0)
        ax4.spines[axis].set_linewidth(3.0)

    plt.savefig(f'{pathname}/Sums_Along_Rows.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'{pathname}/Sums_Along_Rows.png', dpi=300, bbox_inches='tight')
    plt.savefig(f'{pathname}/Sums_Along_Rows.jpg', dpi=300, bbox_inches='tight')

    plt.show()

###

def create_level3_association(pathname, filenames, suffix='association.json'):

    """
    Create Level 3 association for combining multiple calibrated files.

    Parameters:
    -----------
    pathname : str
        Path name for base directory of cal files
    filenames : list
        List of file names for cal files

    Returns:
    --------
    list : List of association files
    str : Path to association file
    """

    if not filenames:

        print('No calibrated files to create Level 3 association'); return None

    # Ensure we have absolute paths and create association file

    if pathname is not None:

        filenames = [f'{pathname}/{filename}' for filename in filenames]

        association_file = os.path.join(pathname, f'Stage3_{suffix}')

    else:

        association_file = os.path.join(os.path.dirname(filenames[0]), f'Stage3_{suffix}')

    # Create the Level 3 association

    print(f'Creating Level 3 association with {len(filenames)} files')

    association = afl.asn_from_list(filenames, rule=DMS_Level3_Base, product_name='Stage3')

    program_number = int(os.path.basename(filenames[0]).split('jw')[1][0:5])
    obs_number = int(os.path.basename(filenames[0]).split('jw')[1][5:8])

    association['program'] = f'Program_ID_JWST{program_number:05d}'
    association['asn_id'] = f'Obs{obs_number:03d}'

    association['asn_type'] = 'Stage3/Spec3'
    association['target'] = 't001'

    for i, filename in enumerate(filenames):

        association['products'][0]['members'][i]['exposerr'] = 'null'

        temp_obs_number = int(os.path.basename(filename).split('jw')[1][5:8])

        association['products'][0]['members'][i]['asn_candidate'] = f'[(\'o{temp_obs_number:03d}\', \'observation\')]'

    if 'all' not in suffix.lower(): 

        association['products'][0]['name'] = f'jw{program_number:05d}_obs{obs_number:03d}_t001_miri_p750l'

    else: 

        association['products'][0]['name'] = f'jw{program_number:05d}_obsAll_t001_miri_p750l'

        association['asn_id'] = 'ObsAll'

    # Write the association to a json file

    _, serialized = association.dump()

    with open(association_file, 'w') as output_file:

        output_file.write(serialized)

    print(f'Created association file: {os.path.basename(association_file)}')

    return association_file

###

# https://jwst-pipeline.readthedocs.io/en/latest/jwst/pipeline/calwebb_spec3.html

def run_spec3_pipeline(pathname, association_file, extraction_type='optimal', resample_spec=False, sigma=3.0, offset=+1.0):

    """
    Run the Spec3 pipeline on Level 3 association.

    Parameters:
    -----------
    pathname : str
        Path name for base directory of cal files
    association_file : str
        Name of association file for processing
    extraction_type : str
        Type of extraction ('box' or 'optimal')
    resample_spec : boolean
        Whether or not to perform resampling
    sigma : float
        Sigma clipping threshold
    offset : float
        Visit offset for the trace in units of JWST/MIRI pixels, or 0.11 arcseconds

    Returns:
    --------
    dict : Dictionary with paths to output files
    """

    if not os.path.exists(pathname):

        os.mkdir(pathname)

    if not association_file or not os.path.exists(association_file):

        print('No valid association file provided')

        return {}

    # Default configuration

    temp_time = time.time()

    spec3_config = {
        'extract_1d': { # https://jwst-pipeline.readthedocs.io/en/latest/jwst/extract_1d/index.html
            'extraction_type': 'optimal',
            'subtract_background': False,
            'optimize_psf_location': True, # Flag to enable PSF location optimization during optimal extraction
            'use_source_posn': True, # Uses the RA and DEC of the header to find the trace location
            'model_nod_pair': True, # Flag for fitting a negative trace during optimal extraction
            'apply_apcorr': False, # Turn this off if doing optimal extraction
            'save_profile': True,
            'save_residual_image': True,
            'position_offset': +1.0*offset, # This is in units of pixels (0.11 arcsec/pixel)
        },
        'resample_spec': { # https://jwst-pipeline.readthedocs.io/en/latest/jwst/resample_spec/index.html
            'skip': not resample_spec, # Turn this off if extraction should be performed with the cal files
        },
        'pixel_replace': { # https://jwst-pipeline.readthedocs.io/en/latest/jwst/pixel_replace/index.html
            'skip': True, # Do not include the pixel_replace step if doing optimal extraction
        },
        'outlier_detection': { # https://jwst-pipeline.readthedocs.io/en/latest/jwst/outlier_detection/index.html
            'skip': True, # It seems that Spec3 outlier detection does not work well for the data set from PID 08544
            'snr': f'{sigma:.1f} {sigma-1.0:.1f}', # SNR values to use for identifying bad pixels; default is '5.0 3.0'
            'save_intermediate_results': True,
        },
    }

    if extraction_type.lower() == 'box':

        spec3_config['extract_1d']['extraction_type'] = extraction_type.lower()
        spec3_config['extract_1d']['optimize_psf_location'] = False
        spec3_config['extract_1d']['model_nod_pair'] = False
        spec3_config['extract_1d']['apply_apcorr'] = True

    elif extraction_type.lower() != 'optimal':

        raise ValueError(f'Unknown extraction type: {extraction_type.lower()} (Must be one of "box" or "optimal").')

    # Run pipeline on the association

    print(f'Processing: {os.path.basename(association_file)}')

    try:

        log = logging.getLogger()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = logging.FileHandler(f'{pathname}/___Spec3Pipeline___.log')
        handler.setFormatter(formatter)
        log.addHandler(handler)

        Spec3Pipeline.call(
            association_file,
            steps=spec3_config,
            save_results=True,
            output_dir=pathname,
        )

        # Find the output files

        output_files = {
            's2d': os.path.join(pathname, 'Stage3_s2d.fits'),
            'x1d': os.path.join(pathname, 'Stage3_x1d.fits')
        }

        for key, file_path in output_files.items():

            if os.path.exists(file_path):

                print(f'  Created: {os.path.basename(file_path)}')

            else:

                print(f'  WARNING: Expected output file not found: {os.path.basename(file_path)}')

                output_files[key] = None

        print(f'\nSpec3 processing complete in {time.time() - temp_time:.1f} seconds. Created {len(output_files)} output files.')

        return output_files

    except Exception as e:

        print(f'  ERROR processing {os.path.basename(association_file)}: {str(e)}')

        return {}

###

def run_pipeline_full(directories, stage1=True, stage2=True, stage3=True, tweak=True, sigma=3.0, extraction_type='optimal',
    bkg_subtract_list=[True, False], extra_directories_for_spec3=[], mask_trace_width=5, offset=+1.0, zred=14.1796):

    """
    Run the three stages of the pipeline (Detector1, Spec2, and Spec3), starting with the uncal files.

    Parameters:
    -----------
    directories : dict
        Dictionary of directories
    stage1 : bool
        Whether or not to run Stage 1 (Det1) of the pipeline
    stage2 : bool
        Whether or not to run Stage 2 (Spec2) of the pipeline
    stage3 : bool
        Whether or not to run Stage 3 (Spec3) of the pipeline
    tweak : bool
        Whether or not to tweak the reference coordinates before running Stage 2 of the pipeline
    sigma : float
        Sigma clipping threshold
    extraction_type : str
        Type of extraction ('box' or 'optimal')
    bkg_subtract_list : list
        List of options for background subtraction
    extra_directories_for_spec3 : list
        List of extra directories for Spec3 processing
    mask_trace_width : int
        Half-width of the mask around the trace in units of JWST/MIRI pixels (0.11 arcsec/pixel)
    offset : float
        Source offset in units of JWST/MIRI pixels (0.11 arcsec/pixel)
    zred : float
        Redshift used for calculating observed-frame wavelengths
    """

    # First runs Stage 1 of the pipeline to produce the cal files from the raw ("uncal") data

    if stage1:

        run_detector1_pipeline(directories, custom_steps=None)

    # Inspect the full images from the rate files produced by Stage 1 of the pipeline

    filenames_rates = sorted(glob.glob(os.path.join(directories['Det1'], '*_mirimage_rate.fits')))
    filenames_rateints = sorted(glob.glob(os.path.join(directories['Det1'], '*_mirimage_rateints.fits')))

    if tweak and directories['CoordinateShift'] is not None:

        tweak_reference_coordinates(filenames_rates, coordinate_shift=directories['CoordinateShift'], 
            offset_additional=(+0.0, +0.0), write_suffix='_tweak_rate.fits')

        filenames_rates = sorted(glob.glob(os.path.join(directories['Det1'], '*_mirimage_tweak_rate.fits')))

        temp_filename_infix = 'mirimage_tweak_clean'

    else:

        temp_filename_infix = 'mirimage_clean'

    # Runs Stage 2 of the JWST pipeline, with or without background subtraction

    if stage2:

        # Cleans the rate files produced by Stage 1 of the pipeline with sigma clipping

        filenames_rates = clean_rate_files(directories['Det1'], filenames_rates, sigma_lower_threshold=sigma, sigma_upper_threshold=sigma,
            columns_to_mask=directories['ColumnsToMask'], rows_to_mask=directories['RowsToMask'], mask_trace_width=mask_trace_width)

        # Inspect the full images from the rate files produced by Stage 1 of the pipeline

        inspect_files(None, filenames_rates)

        for bkg_subtract in bkg_subtract_list:

            # Creates the Level 2 association files, if necessary

            if bkg_subtract:

                temp_pathname = directories['Spec2'].replace('Stage2', 'Default_Pipeline_Stage2')

                if not os.path.exists(temp_pathname): os.mkdir(temp_pathname)

                if directories['AssociationFiles'] is None:

                    level2_association_files = create_level2_associations(None, filenames_rates, suffix='asn_clean.json')

                else:

                    temp_AssociationFiles = directories['AssociationFiles']
                    temp_AssociationFiles[0] = [temp.replace('MAST', 'Default_Pipeline_Stage2') for temp in temp_AssociationFiles[0]]
                    temp_AssociationFiles[1] = [temp.replace('MAST', 'Default_Pipeline_Stage3') for temp in temp_AssociationFiles[1]]
                    directories['AssociationFiles'] = temp_AssociationFiles

                    level2_association_files = directories['AssociationFiles'][0]

                cal_files = run_spec2_pipeline(temp_pathname, level2_association_files, bkg_subtract=bkg_subtract, offset=offset)

            else:

                temp_pathname = directories['Spec2']

                if directories['AssociationFiles'] is None:

                    level2_association_files = create_level2_associations(None, filenames_rates, suffix='asn_clean.json')

                else:

                    temp_AssociationFiles = directories['AssociationFiles']
                    temp_AssociationFiles[0] = [temp.replace('MAST', 'Stage2') for temp in temp_AssociationFiles[0]]
                    temp_AssociationFiles[1] = [temp.replace('MAST', 'Stage3') for temp in temp_AssociationFiles[1]]
                    directories['AssociationFiles'] = temp_AssociationFiles

                    level2_association_files = directories['AssociationFiles'][0]

                cal_files = run_spec2_pipeline(temp_pathname, level2_association_files, bkg_subtract=bkg_subtract, offset=offset)

            # Defines the various filenames to be used throughout (cal, s2d, x1d, bsub, assign_wcs)

            filenames_cal = sorted(glob.glob(os.path.join(temp_pathname, f'*{temp_filename_infix}_cal.fits')))
            filenames_s2d = sorted(glob.glob(os.path.join(temp_pathname, f'*{temp_filename_infix}_s2d.fits')))
            filenames_x1d = sorted(glob.glob(os.path.join(temp_pathname, f'*{temp_filename_infix}_x1d.fits')))

            filenames_bsub = sorted(glob.glob(os.path.join(temp_pathname, f'*{temp_filename_infix}_bsub.fits')))
            filenames_assign_wcs = sorted(glob.glob(os.path.join(temp_pathname, f'*{temp_filename_infix}_assign_wcs.fits')))

            filenames_assign_wcs_nod1 = sorted(glob.glob(os.path.join(temp_pathname, f'*00001_{temp_filename_infix}_assign_wcs.fits')))
            filenames_assign_wcs_nod2 = sorted(glob.glob(os.path.join(temp_pathname, f'*00002_{temp_filename_infix}_assign_wcs.fits')))

            filenames_x1d = [filename_x1d for filename_x1d in filenames_x1d if 'combined' not in filename_x1d]
            filenames_s2d = [filename_s2d for filename_s2d in filenames_s2d if 'combined' not in filename_s2d]

            filenames_s2d = [filename_s2d for filename_s2d in filenames_s2d if 'outlier' not in filename_s2d]

            # Determines the central trace position for each assign_wcs file, separately for the two nod positions

            position_nod1, position_nod2 = get_nod_positions_from_wcs(filenames_assign_wcs_nod1, filenames_assign_wcs_nod2, verbose=True)

            # Determines the complete trace location for each assign_wcs file, then determines the offset of this visit

            trace_locations, source_offsets = [], []

            for filename in filenames_assign_wcs: 

                trace_location, y_plot, source_offset = find_trace(filename, verbose=False)

                trace_locations.append(trace_location); source_offsets.append(source_offset)

            trace_location = np.array(trace_location); source_offsets = np.array(source_offsets)

            offset = np.mean(np.absolute(source_offsets[1::2]) - np.absolute(source_offsets[0::2]))/2.0

            # Inspect the slit placements on the sky

            plot_slit_overlay([directories], zred=zred)

            # Inspect the full images from the cal files

            inspect_files(None, filenames_cal)

            # Inspect the spectra using only the s2d files

            inspect_spectra(None, filenames_s2d, None, ellipses=False, zred=zred, 
                offset=offset, position_nod1=position_nod1, position_nod2=position_nod2)

            # Inspect the spectra using both the s2d and x1d files

            inspect_spectra(None, filenames_s2d, filenames_x1d, ellipses=False, zred=zred, offset=offset)

            # Background subtract the s2d files by taking the difference between nods one and two

            if not bkg_subtract:

                filenames = []

                # Loop through the list of file names for s2d files

                for index, filename_s2d in enumerate(filenames_s2d[::2]):

                    with fits.open(f'{filename_s2d}') as hdul_s2d:

                        nod1_wavelength_data_s2d = np.flip(hdul_s2d['WAVELENGTH'].data, axis=0).T
                        nod1_err_data = np.flip(hdul_s2d['ERR'].data, axis=0).T
                        nod1_sci_data = np.flip(hdul_s2d['SCI'].data, axis=0).T

                    with fits.open(f'{filename_s2d.replace('00001', '00002')}') as hdul_s2d:

                        nod2_wavelength_data_s2d = np.flip(hdul_s2d['WAVELENGTH'].data, axis=0).T
                        nod2_err_data = np.flip(hdul_s2d['ERR'].data, axis=0).T
                        nod2_sci_data = np.flip(hdul_s2d['SCI'].data, axis=0).T

                    wavelength_data_s2d = nod1_wavelength_data_s2d
                    err_data = np.sqrt(np.square(nod1_err_data) + np.square(nod2_err_data))/np.sqrt(2)
                    sci_data = nod1_sci_data - nod2_sci_data; sci_data -= np.nanmedian(sci_data, axis=0)

                    # Makes figure to illustrate sums along the rows and columns before and after self-subtraction

                    with fits.open(f'{filename_s2d}') as hdul_s2d:

                        hdul_s2d['ERR'].data = np.flip((+1.0*err_data).T, axis=0)
                        hdul_s2d['SCI'].data = np.flip((+1.0*sci_data).T, axis=0)

                        HISTORY = 'Background subtracted by taking the difference between nods one and two.'

                        hdul_s2d[0].header['HISTORY'] = HISTORY

                        filename_s2d_bsub = f'{filename_s2d.replace('_s2d.fits', '_bsub.fits')}'
                        hdul_s2d.writeto(f'{filename_s2d_bsub}', overwrite=True)
                        filenames.append(filename_s2d_bsub)

                    with fits.open(f'{filename_s2d.replace('00001', '00002')}') as hdul_s2d:

                        hdul_s2d['ERR'].data = np.flip((+1.0*err_data).T, axis=0)
                        hdul_s2d['SCI'].data = np.flip((-1.0*sci_data).T, axis=0)

                        HISTORY = 'Background subtracted by taking the difference between nods one and two.'

                        hdul_s2d[0].header['HISTORY'] = HISTORY

                        filename_s2d_bsub = f'{filename_s2d.replace('00001', '00002').replace('_s2d.fits', '_bsub.fits')}'
                        hdul_s2d.writeto(f'{filename_s2d_bsub}', overwrite=True)
                        filenames.append(filename_s2d_bsub)

                # Inspect the background subtracted s2d files

                inspect_spectra(None, filenames, None, ellipses=True, zred=zred, 
                    offset=offset, position_nod1=position_nod1, position_nod2=position_nod2)

            # Loop through the list of file names for s2d files

            if not bkg_subtract:

                for i in [0, 1]:

                    if not filenames[i::2]: continue

                    for j, filename in enumerate(filenames[i::2]):

                        with fits.open(f'{filename}') as hdul_s2d:

                            wavelength_data_s2d = np.flip(hdul_s2d['WAVELENGTH'].data, axis=0).T
                            var_poisson_data = np.flip(hdul_s2d['VAR_POISSON'].data, axis=0).T
                            var_rnoise_data = np.flip(hdul_s2d['VAR_RNOISE'].data, axis=0).T
                            var_flat_data = np.flip(hdul_s2d['VAR_FLAT'].data, axis=0).T
                            err_data = np.flip(hdul_s2d['ERR'].data, axis=0).T
                            sci_data = np.flip(hdul_s2d['SCI'].data, axis=0).T

                            if j == 0: 

                                N = len(filenames[i::2])

                                array_var_poisson_data = np.zeros((N, var_poisson_data.shape[0], var_poisson_data.shape[1]))
                                array_var_rnoise_data = np.zeros((N, var_rnoise_data.shape[0], var_rnoise_data.shape[1]))
                                array_var_flat_data = np.zeros((N, var_flat_data.shape[0], var_flat_data.shape[1]))
                                array_err_data = np.zeros((N, err_data.shape[0], err_data.shape[1]))
                                array_sci_data = np.zeros((N, sci_data.shape[0], sci_data.shape[1]))

                            array_var_poisson_data[j] = var_poisson_data
                            array_var_rnoise_data[j] = var_rnoise_data
                            array_var_flat_data[j] = var_flat_data
                            array_err_data[j] = err_data
                            array_sci_data[j] = sci_data

                    # Calculates weighted average from the three visits

                    array_var_poisson_data = 1.0/np.sum(1.0/array_var_poisson_data, axis=0)
                    array_var_rnoise_data = 1.0/np.sum(1.0/array_var_rnoise_data, axis=0)
                    array_var_flat_data = 1.0/np.sum(1.0/array_var_flat_data, axis=0)

                    err_data = np.sqrt(np.sum(np.square(array_err_data), axis=0))/array_err_data.shape[0]
                    err_data[np.isnan(err_data)] = np.inf; err_data[~np.isfinite(err_data)] = np.inf
                    sci_data = astropy.stats.biweight_location(array_sci_data, axis=0)

                    trace_mask = np.zeros(sci_data.shape, dtype=bool)

                    for nod_pos in [position_nod1+offset, position_nod2+offset]:

                        row_hi = min(sci_data.shape[0], int(np.round(nod_pos))+mask_trace_width+1)
                        row_lo = max(0, int(np.round(nod_pos))-mask_trace_width)

                        trace_mask[row_lo:row_hi, :] = True

                    try:

                        # sci_data, _ = background_subtract_s2d(sci_data, box_size=(43, 3), filter_size=(3, 3), sigma=sigma, mask=trace_mask)

                        sci_data, _ = background_subtract_s2d(sci_data, box_size=(9, 3), filter_size=(3, 3), sigma=sigma, mask=trace_mask)
                        sci_data, _ = background_subtract_s2d(sci_data, box_size=(3, 9), filter_size=(3, 3), sigma=sigma, mask=trace_mask)
                        sci_data, _ = background_subtract_s2d(sci_data, box_size=(3, 3), filter_size=(3, 3), sigma=sigma, mask=trace_mask)

                    except ValueError as error:

                        print(f'WARNING: background_subtract_s2d failed, skipping 2D background subtraction ({error})')

                    with fits.open(f'{filenames[i]}') as hdul_s2d:

                        hdul_s2d['VAR_POISSON'].data = np.flip(array_var_poisson_data.T, axis=0)
                        hdul_s2d['VAR_RNOISE'].data = np.flip(array_var_rnoise_data.T, axis=0)
                        hdul_s2d['VAR_FLAT'].data = np.flip(array_var_flat_data.T, axis=0)
                        hdul_s2d['ERR'].data = np.flip(err_data.T, axis=0)
                        hdul_s2d['SCI'].data = np.flip(sci_data.T, axis=0)

                        HISTORY = 'Performs background subtraction by taking the difference between nods one and two. '
                        HISTORY += 'Combined the background subtracted images by taking the weighted average.'

                        hdul_s2d[0].header['HISTORY'] = HISTORY

                        filenames_split = os.path.basename(filenames[i]).split('_'); _filename_ = ''

                        for i, filename_split in enumerate(filenames_split):

                            if i != 1: _filename_ += f'{filename_split}_'

                        _filename_ = _filename_.replace('.fits_', '_combined.fits')

                        DO_NOT_USE = dqflags.pixel['DO_NOT_USE']

                        hdul_s2d[0].header['S_RESAMP'] = 'SKIPPED'
                        hdul_s2d[0].header['FILENAME'] = _filename_

                        dq_data = np.where(hdul_s2d['WHT'].data == 0, DO_NOT_USE, 0).astype(np.uint32)
                        hdul_s2d.insert(hdul_s2d.index_of('WAVELENGTH'), fits.ImageHDU(data=dq_data, name='DQ'))

                        hdul_s2d.writeto(f'{directories['Spec2']}/{_filename_}', overwrite=True)

                    # Inspect the background subtracted s2d files

                    filenames_bsub = filenames

                    bkg_dict = {'box_size':(3, 3), 'filter_size':(3, 3), 'sigma':sigma}

                    inspect_spectra(directories['Spec2'], [_filename_], None, ellipses=True, zred=zred, 
                        bkg_dict=bkg_dict, offset=offset, position_nod1=position_nod1, position_nod2=position_nod2)

            # Inspect sums along the columns and rows

            inspect_column_and_row_sums(temp_pathname, filenames_1=filenames_assign_wcs, filenames_2=filenames_bsub, offset=offset)

            # Cleans the cal files produced by Stage 2 of the pipeline with sigma clipping

            clean_cal_files(filenames_cal, sigma_lower_threshold=sigma, sigma_upper_threshold=sigma,
                columns_to_mask=directories['ColumnsToMask'], rows_to_mask=directories['RowsToMask'], mask_trace_width=mask_trace_width)

            # Subtracts the medians out row-by-row for the cal files

            subtract_row_medians(filenames_cal, sigma_lower_threshold=sigma-1.0, sigma_upper_threshold=sigma-1.0)

    # Runs Stage 3 of the JWST pipeline, with or without background subtraction

    if stage3:

        for bkg_subtract in bkg_subtract_list:

            # Creates the Level 3 association files, if necessary
            # If extra directories are provided, one association file is made using the cal files in the main directory
            # While another association file is made using the cal files from all of the directories (main plus any extras)

            if bkg_subtract:

                temp_pathname = directories['Spec2'].replace('Stage2', 'Default_Pipeline_Stage2')

                filenames_cal = sorted(glob.glob(os.path.join(temp_pathname, f'*{temp_filename_infix}_cal.fits')))

                if directories['AssociationFiles'] is None:

                    if extra_directories_for_spec3:

                        all_filenames_cal = filenames_cal.copy()

                        obs_number = int(os.path.basename(filenames_cal[0]).split('jw')[1][5:8])

                        association_inputs = [(filenames_cal, f'Obs{obs_number:03d}_association.json')]

                        for extra_directories in extra_directories_for_spec3:

                            if bkg_subtract:

                                temp_temp_pathname = extra_directories['Spec2'].replace('Stage2', 'Default_Pipeline_Stage2')

                            else:

                                temp_temp_pathname = extra_directories['Spec2']

                            extra_filenames_cal = glob.glob(os.path.join(temp_temp_pathname, f'*{temp_filename_infix}_cal.fits'))

                            all_filenames_cal.extend(extra_filenames_cal)
                        
                        association_inputs.append((all_filenames_cal, 'All_association.json'))

                    else:

                        obs_numbers = set(int(os.path.basename(f).split('jw')[1][5:8]) 
                            for f in filenames_cal)

                        if len(obs_numbers) > 1:

                            association_inputs = [(filenames_cal, 'All_association.json')]

                        else:

                            association_inputs = [(filenames_cal, f'Obs{next(iter(obs_numbers)):03d}_association.json')]

                    level3_association_files = [create_level3_association(None, filenames, 
                        suffix=suffix) for filenames, suffix in association_inputs]

                else:

                    level3_association_files = [(directories['AssociationFiles'][1][0], 'association.json')]

            else:

                temp_pathname = directories['Spec2']

                temp_filename = f'*{temp_filename_infix}_bsub_combined.fits'

                filenames_bsub = sorted(glob.glob(os.path.join(temp_pathname, temp_filename)))

                if extra_directories_for_spec3:

                    all_filenames_bsub = filenames_bsub.copy()

                    obs_number = int(os.path.basename(filenames_bsub[0]).split('jw')[1][5:8])

                    association_inputs = [(filenames_bsub, f'Obs{obs_number:03d}_combined_association.json')]

                    for extra_directories in extra_directories_for_spec3:

                        if bkg_subtract:

                            temp_temp_pathname = extra_directories['Spec2'].replace('Stage2', 'Default_Pipeline_Stage2')

                        else:

                            temp_temp_pathname = extra_directories['Spec2']

                        temp_temp_filename = f'*{temp_filename_infix}_bsub_combined.fits'

                        extra_filenames_bsub = glob.glob(os.path.join(temp_temp_pathname, temp_temp_filename))

                        all_filenames_bsub.extend(extra_filenames_bsub)

                    association_inputs.append((all_filenames_bsub, 'All_combined_association.json'))

                else:

                    obs_numbers = set(int(os.path.basename(f).split('jw')[1][5:8]) 
                        for f in filenames_bsub)

                    if len(obs_numbers) > 1:

                        association_inputs = [(filenames_bsub, 'All_combined_association.json')]

                    else:

                        association_inputs = [(filenames_bsub, f'Obs{next(iter(obs_numbers)):03d}_combined_association.json')]

                level3_association_files = [create_level3_association(None, filenames, 
                    suffix=suffix) for filenames, suffix in association_inputs]

            # Runs Stage 3 of the JWST pipeline, once using the s2d files and another time using the cal files
            # Jake prefers working with the s2d files while Jane prefers working with the cal files

            if bkg_subtract: 

                temp_pathname = directories['Spec3'].replace('Stage3', 'Default_Pipeline_Stage3')

                if not os.path.exists(temp_pathname): os.mkdir(temp_pathname)

            else: 

                temp_pathname = directories['Spec3']

            # Runs Stage 3 of the JWST pipeline for each association file in the list of assocation files

            for level3_association_file in level3_association_files:

                output_files = run_spec3_pipeline(temp_pathname, level3_association_file, 
                    extraction_type=extraction_type, resample_spec=True, sigma=sigma) # With s2d files

                output_files = run_spec3_pipeline(temp_pathname, level3_association_file, 
                    extraction_type=extraction_type, resample_spec=False, sigma=sigma) # With cal files

            # Inspect the spectra using the Stage 3 s2d and x1d files

            filenames_c1d = sorted(glob.glob(os.path.join(temp_pathname, '*p750l_c1d.fits')))
            filenames_s2d = sorted(glob.glob(os.path.join(temp_pathname, '*p750l_s2d.fits')))
            filenames_x1d = sorted(glob.glob(os.path.join(temp_pathname, '*p750l_x1d.fits')))

            filenames_c1d = [filename_c1d.split('/')[-1] for filename_c1d in filenames_c1d]
            filenames_s2d = [filename_s2d.split('/')[-1] for filename_s2d in filenames_s2d]
            filenames_x1d = [filename_x1d.split('/')[-1] for filename_x1d in filenames_x1d]

            filenames_s2d = [filename_s2d for filename_s2d in filenames_s2d if 'outlier' not in filename_s2d]

            inspect_spectra(temp_pathname, filenames_s2d, filenames_c1d, zred=zred, colorbar='SNR') # Options include 'SB' and 'SNR'
            inspect_spectra(temp_pathname, filenames_s2d, filenames_x1d, zred=zred, colorbar='SNR') # Options include 'SB' and 'SNR'

        # Create figure to compare fluxes and errors for the different reductions of the 1D spectra

        temp_pathname_1, temp_pathname_2 = directories['Spec3'], directories['Spec3'].replace('Stage3', 'Default_Pipeline_Stage3')

        try:

            filename_1 = sorted(glob.glob(os.path.join(temp_pathname_1, '*_c1d.fits')))[-1]
            filename_2 = sorted(glob.glob(os.path.join(temp_pathname_1, '*_x1d.fits')))[-1]
            filename_3 = sorted(glob.glob(os.path.join(temp_pathname_2, '*_c1d.fits')))[-1]
            filename_4 = sorted(glob.glob(os.path.join(temp_pathname_2, '*_x1d.fits')))[-1]

            list_of_filenames = [filename_1, filename_2, filename_3, filename_4]

        except Exception:

            filename_3 = sorted(glob.glob(os.path.join(temp_pathname_2, '*_c1d.fits')))[0]
            filename_4 = sorted(glob.glob(os.path.join(temp_pathname_2, '*_x1d.fits')))[0]

            list_of_filenames = [filename_3, filename_4]

        list_of_labels = [
            r'$\mathrm{Custom\ Pipeline\ Using}\ \texttt{cal}\ \mathrm{Files}$', 
            r'$\mathrm{Custom\ Pipeline\ Using}\ \texttt{s2d}\ \mathrm{Files}$', 
            r'$\mathrm{Default\ Pipeline\ Using}\ \texttt{cal}\ \mathrm{Files}$', 
            r'$\mathrm{Default\ Pipeline\ Using}\ \texttt{s2d}\ \mathrm{Files}$', 
        ]

        list_of_flux_data, list_of_wavelength_data, list_of_flux_error_data = [], [], []

        for temp_filename in list_of_filenames:

            with fits.open(f'{temp_filename}') as hdul_x1d:

                try:

                    temp_data_x1d = hdul_x1d['EXTRACT1D'].data

                except Exception:

                    temp_data_x1d = hdul_x1d['COMBINE1D'].data

                temp_column_names = temp_data_x1d.columns.names
                temp_flux_error_data = temp_data_x1d[np.array(temp_column_names)[np.char.find(temp_column_names, 'ERROR') != -1][0]]
                temp_wavelength_data = temp_data_x1d.field(np.where(np.array(temp_column_names) == 'WAVELENGTH')[0][0])
                temp_flux_data = temp_data_x1d.field(np.where(np.array(temp_column_names) == 'FLUX')[0][0])

                list_of_flux_data.append(temp_flux_data)
                list_of_wavelength_data.append(temp_wavelength_data)
                list_of_flux_error_data.append(temp_flux_error_data)

        x = [np.array(temp_list) for temp_list in list_of_wavelength_data]
        y = [1e+6*np.array(temp_list) for temp_list in list_of_flux_data]
        yerr = [1e+6*np.array(temp_list) for temp_list in list_of_flux_error_data]

        # Creates multiple specutils Spectrum1D objects in order to smooth these spectra by a factor of two
        # https://specutils.readthedocs.io/en/stable/manipulation.html#resampling

        spec, smooth_spec, smooth_x, smooth_y, smooth_yerr = [], [], [], [], []

        for temp_x, temp_y, temp_yerr in zip(x, y, yerr):

            temp_uncertainty = astropy.nddata.StdDevUncertainty(1e-6*temp_yerr*u.Jy)

            temp_spec = specutils.Spectrum1D(spectral_axis=temp_x*u.m, flux=1e-6*temp_y*u.Jy, uncertainty=temp_uncertainty)

            temp_smooth_spec = 1e+6*box_smooth(temp_spec, width=2)

            spec.append(temp_spec)
            smooth_y.append(temp_smooth_spec.flux.value)
            smooth_yerr.append(temp_smooth_spec.uncertainty.quantity.value)
            smooth_x.append(temp_smooth_spec.spectral_axis.value)
            smooth_spec.append(temp_smooth_spec)

        # Plot the science data...

        figsizex, figsizey = 12, 6
        xmin, xmax, xstep = +4.875, +10.375, +0.125
        xticks = [+5.0, +5.5, +6.0, +6.5, +7.0, +7.5, +8.0, +8.5, +9.0, +9.5, +10.0]

        for i in range(2):

            if i == 0:

                temp_x = [np.array(temp_list) for temp_list in x]
                temp_y = [np.array(temp_list) for temp_list in y]

                temp_filename_pdf = 'Stage3_comparison_x1d_and_c1d_flux.pdf'
                temp_filename_png = 'Stage3_comparison_x1d_and_c1d_flux.png'
                temp_filename_jpg = 'Stage3_comparison_x1d_and_c1d_flux.jpg'

            else:

                temp_x = [np.array(temp_list) for temp_list in smooth_x]
                temp_y = [np.array(temp_list) for temp_list in smooth_y]

                temp_filename_pdf = 'Stage3_smoothed_comparison_x1d_and_c1d_flux.pdf'
                temp_filename_png = 'Stage3_smoothed_comparison_x1d_and_c1d_flux.png'
                temp_filename_jpg = 'Stage3_smoothed_comparison_x1d_and_c1d_flux.jpg'

            #

            plt.close()
            fig = plt.figure(figsize=(figsizex, figsizey))
            ax = fig.add_subplot(111)

            ax.set_xlabel(r'$\mathrm{Observed\ Wavelength}\ \left[ \mathrm{microns} \right]$', fontsize=20)
            ax.set_ylabel(r'$\mathrm{Flux\ Density}\ \left[ \mathrm{\mu Jy} \right]$', fontsize=20, labelpad=8)

            ax.tick_params(axis='both', which='major', direction='out', 
                bottom=True, top=True, left=True, right=True, length=8, width=3, labelsize=16)
            ax.tick_params(axis='both', which='minor', direction='out', 
                bottom=True, top=True, left=True, right=True, length=6, width=3, labelsize=16)

            temp_colors = sns.color_palette('husl', len(list_of_filenames))

            ymins, ymaxs = [], []

            for j, (temp_temp_x, temp_temp_y) in enumerate(zip(temp_x, temp_y)):

                ax.plot(temp_temp_x, temp_temp_y, ds='steps-mid', c=temp_colors[j], ls='-', lw=3, alpha=0.6, 
                    label=list_of_labels[j], zorder=2)

                ymins.append(np.nanmin(temp_temp_y[np.logical_and(xmin <= temp_temp_x, temp_temp_x <= xmax)]))
                ymaxs.append(np.nanmax(temp_temp_y[np.logical_and(xmin <= temp_temp_x, temp_temp_x <= xmax)]))

            ax.set_xlim(xmin, xmax); ax.set_xticks(xticks)
            ax.xaxis.set_minor_locator(MultipleLocator(xstep))
            ax.yaxis.set_minor_locator(AutoMinorLocator(4))

            xlabel = fr'$\mathrm{{Rest-Frame\ Wavelength}}\ \mathrm{{at}}\ z = {zred:.2f}'
            xlabel += fr'\ \left[ \mathrm{{microns}} \right]$'

            ax_top = ax.twiny()
            ax_top.tick_params(axis='both', which='major', direction='out', 
                top=True, bottom=False, right=False, left=False, length=8, width=3, labelsize=20)
            ax_top.tick_params(axis='both', which='minor', direction='out', 
                top=True, bottom=False, right=False, left=False, length=6, width=3, labelsize=20)
            ax_top.set_xlabel(xlabel, fontsize=20, labelpad=12)
            ax_top.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(4))
            ax_top.set_xlim(xmin/(1.0 + zred), xmax/(1.0 + zred))

            xmin, xmax = ax.get_xlim()
            ymin, ymax = ax.get_ylim()
            xarray = np.linspace(xmin, xmax, 1001)
            ax.plot(xarray, np.zeros(xarray.shape), c='goldenrod', ls='-', lw=3, zorder=0)

            ymin, ymax = np.nanmin(ymins), np.nanmax(ymaxs)

            amax = np.amax([np.absolute(ymin), np.absolute(ymax)])

            ax.set_ylim(-1.1*amax, +1.1*amax)

            dictionary_elines = return_observed_wavelengths(zred=zred)

            list_of_line_wavelengths = [
                np.mean([dictionary_elines['wave_O2__3727'],
                    dictionary_elines['wave_O2__3729']]),
                dictionary_elines['wave_Hb__4863'],
                dictionary_elines['wave_O3__4959'],
                dictionary_elines['wave_O3__5007'],
                dictionary_elines['wave_Ha__6565'],
            ]

            ax.vlines(list_of_line_wavelengths, -1.1*amax, +1.1*amax, colors='grey', ls=':', lw=3, alpha=1.0, zorder=0)

            handles, labels = ax.get_legend_handles_labels()
            ordering = np.arange(len(list_of_filenames)).tolist()
            handles, labels = [handles[i] for i in ordering], [labels[i] for i in ordering]
            legend = ax.legend(handles, labels, loc='lower center', ncol=2, fontsize=16, framealpha=1)
            legend.get_frame().set_edgecolor('darkgrey')
            legend.get_frame().set_linewidth(3)

            for axis in ['top','bottom','left','right']: 

                ax.spines[axis].set_linewidth(3)

            # Save the files...

            plt.savefig(f'{directories['Analysis']}/{temp_filename_pdf}', dpi=300, bbox_inches='tight')
            plt.savefig(f'{directories['Analysis']}/{temp_filename_png}', dpi=300, bbox_inches='tight')
            plt.savefig(f'{directories['Analysis']}/{temp_filename_jpg}', dpi=300, bbox_inches='tight')

    # Finished!

###

def plot_full_spectrum(pathname, pathname_s2d, pathname_x1d, zred=14.1796, galaxy_name=r'\boldmath$\mathrm{JADES-GS-z14-0}$', 
    colorbar='SNR', wavelength_psf=None, fwhms_pixels=None, additional_offset=+0.0, f_noise=+1.0, 
    xmin=+4.875, xmax=+10.375):

    """
    Plot the full 2D and 1D MIRI/LRS spectrum for a given galaxy.

    Produces a two-panel figure -- the top panel shows the 2D spectral image
    (s2d) with PSF-based extraction boundaries and emission-line markers,
    and the bottom panel shows the 1D spectrum (x1d) with the same line
    markers and a Balmer-limit indicator.

    Saves both a raw and an LSF-smoothed version to 'pathname'.

    Parameters:
    -----------
    pathname : str
        Directory in which to save the output figures
    pathname_s2d : str
        Full path to the s2d FITS file
    pathname_x1d : str
        Full path to the x1d FITS file
    zred : float
        Redshift used to compute observed-frame emission-line wavelengths
    galaxy_name : str
        Galaxy identifier to be used as the figure suptitle (LaTeX accepted)
    colorbar : str
        Colorbar quantity for the 2D panel -- 'SNR' for the signal-to-noise per
        pixel, or any other value for the per-pixel surface brightness in MJy/sr
    wavelength_psf : array_like or None
        Wavelength array [microns] for the PSF FWHM profile; if None, then the
        extraction-boundary overlay is omitted and the smooth variant is skipped
    fwhms_pixels : array_like or None
        FWHM [pixels] at each `wavelength_psf` wavelength; if None, same as above
    additional_offset : float
        Pixel offset added to the extraction-profile centre (EXTRXSTR + EXTRXSTP) / 2
    f_noise : float
        Empirical noise inflation factor applied to the 1D error spectrum
    xmin : float
        Minimum observed wavelength [microns] for the plot's x-axis
    xmax : float
        Maximum observed wavelength [microns] for the plot's x-axis

    Returns:
    --------
    None
    """

    # Compute observed-frame emission-line wavelengths at the target redshift

    elines = return_observed_wavelengths(zred)

    wave_O2__3727 = elines['wave_O2__3727']
    wave_O2__3729 = elines['wave_O2__3729']
    wave_Hb__4863 = elines['wave_Hb__4863']
    wave_O3__4959 = elines['wave_O3__4959']
    wave_O3__5007 = elines['wave_O3__5007']
    wave_Ha__6565 = elines['wave_Ha__6565']

    wavelengths_lines = np.array([
        np.mean([wave_O2__3727, wave_O2__3729]),
        wave_Hb__4863,
        wave_O3__4959,
        wave_O3__5007,
        wave_Ha__6565,
    ])

    vlines = wavelengths_lines

    # Read the 2D spectral image

    with fits.open(pathname_s2d) as hdul_s2d:

        wavelength_data_s2d = np.flip(hdul_s2d['WAVELENGTH'].data, axis=0).T

        err_data = np.flip(hdul_s2d['ERR'].data, axis=0).T
        sci_data = np.flip(hdul_s2d['SCI'].data, axis=0).T

        PIXAR_A2 = hdul_s2d[1].header['PIXAR_A2']

    # Read the 1D extracted spectrum

    with fits.open(pathname_x1d) as hdul_x1d:

        try:

            data_x1d = hdul_x1d['EXTRACT1D'].data
            column_names = data_x1d.columns.names

            flux_error_data = data_x1d[np.array(column_names)[np.char.find(column_names, 'ERROR') != -1][0]]
            wavelength_data = data_x1d.field(np.where(np.array(column_names) == 'WAVELENGTH')[0][0])
            flux_data = data_x1d.field(np.where(np.array(column_names) == 'FLUX')[0][0])

        except:

            data_x1d = hdul_x1d['COMBINE1D'].data
            column_names = data_x1d.columns.names

            flux_error_data = data_x1d[np.array(column_names)[np.char.find(column_names, 'ERROR') != -1][0]][::-1]
            wavelength_data = data_x1d.field(np.where(np.array(column_names) == 'WAVELENGTH')[0][0])[::-1]
            flux_data = data_x1d.field(np.where(np.array(column_names) == 'FLUX')[0][0])[::-1]

        try:

            EXTRXSTR, EXTRXSTP = hdul_x1d[1].header['EXTRXSTR'], hdul_x1d[1].header['EXTRXSTP']

        except:

            EXTRXSTR, EXTRXSTP = 0, 60

    # Compute extraction boundaries and LSF-smoothed spectrum when PSF arrays are available

    xstep = +0.125
    temp_xarray = np.linspace(xmin, xmax, 1001)

    upper_extraction, lower_extraction = None, None
    smoothed_flux_data, smoothed_flux_error_data = None, None

    if wavelength_psf is not None and fwhms_pixels is not None:

        temp_condition = np.logical_and(~np.isnan(wavelength_psf), ~np.isnan(fwhms_pixels))

        interp_psf = scipy.interpolate.interp1d(wavelength_psf[temp_condition],
            np.array(fwhms_pixels)[temp_condition], kind='cubic')

        fwhms_interpolated = interp_psf(temp_xarray)

        central_pixel = np.mean([EXTRXSTR, EXTRXSTP]) + additional_offset

        upper_extraction = (central_pixel + fwhms_interpolated*(2.0/np.sqrt(2*np.log(2))))*np.ones(temp_xarray.shape)
        lower_extraction = (central_pixel - fwhms_interpolated*(2.0/np.sqrt(2*np.log(2))))*np.ones(temp_xarray.shape)

        interp_lsf = scipy.interpolate.interp1d(wavelength_psf[temp_condition],
            np.array(fwhms_pixels)[temp_condition],
            kind='cubic', fill_value='extrapolate')

        fwhms_lsf = interp_lsf(wavelength_data)/(2.0*np.sqrt(2*np.log(2))); fwhms_lsf *= 2.0*0.11*fwhms_lsf/0.47

        spec_data = specutils.Spectrum1D(
            spectral_axis=wavelength_data*u.um, flux=flux_data*u.uJy,
            uncertainty=astropy.nddata.StdDevUncertainty(flux_error_data*u.uJy))

        lsf_flux, lsf_flux_err = [], []

        for idx, temp_fwhm in enumerate(fwhms_lsf):

            temp_smoothed = gaussian_smooth(spec_data, stddev=np.amax([1e-3, temp_fwhm]))
            lsf_flux_err.append(temp_smoothed.uncertainty.quantity.value[idx])
            lsf_flux.append(temp_smoothed.flux.value[idx])

        smoothed_flux_data, smoothed_flux_error_data = np.array(lsf_flux), np.array(lsf_flux_err)

    # Axis ticks and figure layout

    smooth_variants = [True, False] if smoothed_flux_data is not None else [False]

    xticks = list(np.arange(np.ceil(xmin/0.5)/2.0, xmax, 0.5))

    for smooth in smooth_variants:

        figsizex, figsizey = 12, 8

        plt.close()
        fig = plt.figure(figsize=(figsizex, figsizey), constrained_layout=True)
        grid = matplotlib.gridspec.GridSpec(2, 1, height_ratios=[1.0, 1.0], hspace=0.125, wspace=0.125)

        fig.suptitle(galaxy_name, x=0.515, y=1.025, fontsize=20)

        for panel_index, panel_axis in enumerate(grid):

            if panel_index == 0:

                # 2D spectral image panel

                ax = plt.subplot(panel_axis)

                ax.tick_params(axis='both', which='major', direction='out',
                    bottom=True, top=True, left=True, right=True, length=8, width=3, labelsize=16)
                ax.tick_params(axis='both', which='minor', direction='out',
                    bottom=True, top=True, left=True, right=True, length=6, width=3, labelsize=16)

                data = sci_data/err_data if colorbar == 'SNR' else sci_data

                index_xmin = np.argmin(np.absolute(np.nanmean(wavelength_data_s2d, axis=0) - xmin))
                index_xmax = np.argmin(np.absolute(np.nanmean(wavelength_data_s2d, axis=0) - xmax))

                temp_xmin = np.nanmean(wavelength_data_s2d[:, index_xmin - 1])
                temp_xmax = np.nanmean(wavelength_data_s2d[:, index_xmax + 1])

                temp_cond = np.logical_and(temp_xmin <= wavelength_data_s2d, wavelength_data_s2d < temp_xmax)

                data_masked = data.copy()
                data_masked[~temp_cond] = np.nan
                vmin_zscale, vmax_zscale = ZScaleInterval().get_limits(data_masked)

                if colorbar == 'SNR': vmin_zscale, vmax_zscale = -3.75, +3.75

                xx, yy = np.meshgrid(np.nanmean(wavelength_data_s2d[:, index_xmin:index_xmax], axis=0),
                    np.arange(0, data.shape[0], 1))

                temp_image = ax.pcolormesh(xx, yy, data[:, index_xmin:index_xmax], vmin=vmin_zscale, vmax=vmax_zscale,
                    cmap=cmap, shading='face', edgecolors='face', lw=0, rasterized=True)

                ymin_2d, ymax_2d = ax.get_ylim()

                ax.vlines(vlines, ymax_2d-10+1, ymax_2d+1, colors=colors_5[3], ls='-', lw=3, alpha=1.0, zorder=2)
                ax.vlines(vlines, ymin_2d+1, ymin_2d+10+1, colors=colors_5[3], ls='-', lw=3, alpha=1.0, zorder=2)

                if upper_extraction is not None and lower_extraction is not None:

                    ax.plot(temp_xarray, upper_extraction, c=colors_5[3], ls='-', lw=3, alpha=1.0, zorder=2)
                    ax.plot(temp_xarray, lower_extraction, c=colors_5[3], ls='-', lw=3, alpha=1.0, zorder=2)

                ax.set_xlim(xmin, xmax)
                ax.set_ylim(0.0, data.shape[0])
                ax.set_xticks(xticks); ax.set_xticklabels([])
                ax.xaxis.set_minor_locator(MultipleLocator(xstep))
                ax.yaxis.set_minor_locator(AutoMinorLocator(4))

                ax.set_ylabel(r'$\mathrm{Pixels}$' + '\n' +
                    fr'$\left[ \mathrm{{{np.sqrt(PIXAR_A2):.2f}}}\ \mathrm{{arcsec/pixel}} \right]$',
                    fontsize=20, labelpad=8)

                cbar = fig.colorbar(temp_image, ax=ax, location='top', shrink=1.0, pad=0.1)

                cbar.ax.tick_params(axis='both', which='major', direction='out',
                    bottom=False, top=True, left=False, right=False, length=8, width=3, labelsize=16)
                cbar.ax.tick_params(axis='both', which='minor', direction='out',
                    bottom=False, top=True, left=False, right=False, length=6, width=3, labelsize=16)

                if colorbar == 'SNR':

                    cbar.set_label(r'$\mathrm{Signal\mathrm{-}to\mathrm{-}Noise\ Ratio\ Per\ Pixel}$', fontsize=20, labelpad=12)

                else:

                    cbar.set_label(r'$\mathrm{Surface\ Brightness\ \left[ MJy/sr \right]}$', fontsize=20, labelpad=12)

                cbar.ax.xaxis.set_major_locator(plt.MaxNLocator(8))
                cbar.ax.set_xticklabels(cbar.ax.get_xticklabels(), va='center_baseline')
                cbar.ax.xaxis.set_tick_params(pad=12)
                cbar.outline.set_linewidth(3)

                for spine in ['top', 'bottom', 'left', 'right']: ax.spines[spine].set_linewidth(3)

            else:

                # 1D spectrum panel

                ax = plt.subplot(panel_axis)

                ax.set_xlabel(r'$\mathrm{Observed\ Wavelength}\ \left[ \mathrm{microns} \right]$', fontsize=20)
                ax.set_ylabel(r'$\mathrm{Flux\ Density}\ \left[ \mathrm{\mu Jy} \right]$', fontsize=20, labelpad=14)

                ax.tick_params(axis='both', which='major', direction='out',
                    bottom=True, top=True, left=True, right=True, length=8, width=3, labelsize=16)
                ax.tick_params(axis='both', which='minor', direction='out',
                    bottom=True, top=True, left=True, right=True, length=6, width=3, labelsize=16)

                if not smooth: x, y, yerr = wavelength_data, 1e+6*flux_data, f_noise*1e+6*flux_error_data
                else: x, y, yerr = wavelength_data, 1e+6*smoothed_flux_data, f_noise*1e+6*smoothed_flux_error_data

                ax.fill_between(x, -1.0*yerr, +1.0*yerr, step='mid', color='darkgray', lw=0, alpha=0.6, zorder=1)
                ax.plot(x, y, ds='steps-mid', c='k', lw=3, zorder=2)

                ax.set_xlim(xmin, xmax)
                ax.set_xticks(xticks)
                ax.set_yticks([-0.4, +0.0, +0.4, +0.8])
                ax.xaxis.set_minor_locator(MultipleLocator(xstep))
                ax.yaxis.set_minor_locator(AutoMinorLocator(4))

                xarray = np.linspace(xmin, xmax, 1001)
                ax.plot(xarray, np.zeros(xarray.shape), c='goldenrod', ls='-', lw=3, zorder=0)

                ymin_1d, ymax_1d = -0.4, +0.8

                ax.set_ylim(ymin_1d, ymax_1d)
                ax.vlines(vlines, ymin_1d-1e-2, ymax_1d, colors=colors_5[3], ls=':', lw=3, alpha=1.0, zorder=0)

                xspan = xmax - xmin

                if np.logical_and(xmin < np.mean([wave_O2__3727, wave_O2__3729]), np.mean([wave_O2__3727, wave_O2__3729]) < xmax):

                    ax.text(np.mean([wave_O2__3727, wave_O2__3729])+0.01*xspan, 0.950*ymax_1d,
                        r'\boldmath$\leftarrow [\mathrm{OII}]\ \lambda\lambda 3727{,\:\!}3729$',
                        c=colors_5[3], fontsize=14, ha='left', va='top', zorder=2)

                if np.logical_and(xmin < wave_Hb__4863, wave_Hb__4863 < xmax):

                    ax.text(wave_Hb__4863-0.01*xspan, 0.945*ymax_1d,
                        r'\boldmath$\mathrm{H}\beta \rightarrow$',
                        c=colors_5[3], fontsize=14, ha='right', va='top', zorder=2)

                if np.logical_and(xmin < wave_O3__5007, wave_O3__5007 < xmax):

                    ax.text(wave_O3__5007+0.01*xspan, 0.950*ymax_1d,
                        r'\boldmath$\leftarrow [\mathrm{OIII}]\ \lambda\lambda 4959{,\:\!}5007$',
                        c=colors_5[3], fontsize=14, ha='left', va='top', zorder=2)

                if np.logical_and(xmin < wave_Ha__6565, wave_Ha__6565 < xmax):

                    ax.text(wave_Ha__6565-0.01*xspan, 0.941*ymax_1d,
                        r'\boldmath$\mathrm{H}\alpha \rightarrow$',
                        c=colors_5[3], fontsize=14, ha='right', va='top', zorder=2)

                if np.logical_and(xmin < 0.3646*(1.0+zred), 0.3646*(1.0+zred) < xmax):

                    ax.vlines(0.3646*(1.0+zred), ymin_1d, +0.0, colors='grey', ls=':', lw=3, alpha=1.0, zorder=0)

                    ax.text(0.3646*(1.0+zred)-0.094*xspan, 0.53*ymin_1d,
                        r'\boldmath$\mathrm{Balmer}$' + '\n' + r'\boldmath$\mathrm{Limit} \rightarrow$',
                        c='grey', fontsize=14, ha='left', va='top', zorder=2)

                for spine in ['top', 'bottom', 'left', 'right']: ax.spines[spine].set_linewidth(3)

        temp_filename = 'Full_Spectrum_Smooth' if smooth else 'Full_Spectrum'

        plt.savefig(f'{pathname}/{temp_filename}.pdf', dpi=300, bbox_inches='tight')
        plt.savefig(f'{pathname}/{temp_filename}.png', dpi=300, bbox_inches='tight')
        plt.savefig(f'{pathname}/{temp_filename}.jpg', dpi=300, bbox_inches='tight')

        plt.show()

###

def get_resolving_power(wavelength):

    """
    Determines the resolving power at a given wavelength for the emission line fitting.

    Parameters:
    -----------
    wavelength : float
        Wavelength, in units of microns
    """

    # Returns spectral resolving power of the MIRI/LRS

    return fitted_line(wavelength)

###

def model_EmissionLinesAndContinuum_O2(wave, x0, x1, x2, zred, eline_sigma, flux_O2__Doub, ratio_O2__Doub):

    """
    Model fitting function to be used by lmfit centered around [OII].

    Parameters:
    -----------
    wave : array
        Array of wavelengths, in units of microns
    x0 : float
        Zeroth component of the underlying continuum
    x1 : float
        First component for the underlying continuum
    x2 : float
        Second component for the underlying continuum
    zred : float
        Redshift, to be used on the red end of the spectrum
    eline_sigma : float
        Velocity dispersion for the emission lines, in units of km/s
    flux_O2__Doub : float
        Flux of the [OII] doublet, in the same units as the input spectrum
    ratio_O2__Doub : float
        Emission line ratio of the [OII] doublet
    """

    # Calculates observed-frame wavelengths

    obs_wave_O2__3727 = 1e-4*rest_wave_O2__3727*(1.0 + zred) # microns, observed-frame
    obs_wave_O2__3729 = 1e-4*rest_wave_O2__3729*(1.0 + zred) # microns, observed-frame

    # Calculates the velocity dispersions after convolving with the line-spread function

    sigma_O2__3727 = np.sqrt(
        np.square((eline_sigma/c_kms)*obs_wave_O2__3727) + 
        np.square(obs_wave_O2__3727/(2.355*get_resolving_power(obs_wave_O2__3727))))
    sigma_O2__3729 = np.sqrt(
        np.square((eline_sigma/c_kms)*obs_wave_O2__3729) + 
        np.square(obs_wave_O2__3729/(2.355*get_resolving_power(obs_wave_O2__3729))))

    # Calculate the line fluxes in the [OII] doublet 

    flux_O2__3727 = flux_O2__Doub/(1.0 + ratio_O2__Doub)
    flux_O2__3729 = flux_O2__Doub/(1.0 + 1.0/ratio_O2__Doub)

    # Calculates the peak line fluxes

    peak_O2__3727 = flux_O2__3727/np.sqrt(2*np.pi*np.square(sigma_O2__3727))
    peak_O2__3729 = flux_O2__3729/np.sqrt(2*np.pi*np.square(sigma_O2__3729))

    # Calculates the Gaussian emission line fluxes

    Gaussian_O2__3727 = peak_O2__3727*np.exp(-np.square((wave - obs_wave_O2__3727)/sigma_O2__3727)/2.0)
    Gaussian_O2__3729 = peak_O2__3729*np.exp(-np.square((wave - obs_wave_O2__3729)/sigma_O2__3729)/2.0)

    # Calculates the continuum model

    continuum = x0 + x1*wave + x2*np.square(wave)

    # Returns the total model

    model = continuum + Gaussian_O2__3727 + Gaussian_O2__3729

    return model

###

def model_EmissionLinesAndContinuum_O3(wave, x0, x1, x2, zred, eline_sigma, flux_Hb__4863, flux_O3__5007):

    """
    Model fitting function to be used by lmfit centered around Hbeta+[OIII].

    Parameters:
    -----------
    wave : array
        Array of wavelengths, in units of microns
    x0 : float
        Zeroth component of the underlying continuum
    x1 : float
        First component for the underlying continuum
    x2 : float
        Second component for the underlying continuum
    zred : float
        Redshift, to be used on the red end of the spectrum
    eline_sigma : float
        Velocity dispersion for the emission lines, in units of km/s
    flux_Hb__4863 : float
        Flux of the Hbeta emission line, in the same units as the input spectrum
    flux_O3__5007 : float
        Flux of the [OIII] emission lines, in the same units as the input spectrum
    """

    # Calculates observed-frame wavelengths

    obs_wave_Hb__4863 = 1e-4*rest_wave_Hb__4863*(1.0 + zred) # microns, observed-frame
    obs_wave_O3__4959 = 1e-4*rest_wave_O3__4959*(1.0 + zred) # microns, observed-frame
    obs_wave_O3__5007 = 1e-4*rest_wave_O3__5007*(1.0 + zred) # microns, observed-frame

    # Calculates the velocity dispersions after convolving with the line-spread function

    sigma_Hb__4863 = np.sqrt(
        np.square((eline_sigma/c_kms)*obs_wave_Hb__4863) + 
        np.square(obs_wave_Hb__4863/(2.355*get_resolving_power(obs_wave_Hb__4863))))
    sigma_O3__4959 = np.sqrt(
        np.square((eline_sigma/c_kms)*obs_wave_O3__4959) + 
        np.square(obs_wave_O3__4959/(2.355*get_resolving_power(obs_wave_O3__4959))))
    sigma_O3__5007 = np.sqrt(
        np.square((eline_sigma/c_kms)*obs_wave_O3__5007) + 
        np.square(obs_wave_O3__5007/(2.355*get_resolving_power(obs_wave_O3__5007))))

    # Calculates the peak line fluxes

    peak_Hb__4863 = flux_Hb__4863/np.sqrt(2*np.pi*np.square(sigma_Hb__4863))
    peak_O3__5007 = flux_O3__5007/np.sqrt(2*np.pi*np.square(sigma_O3__5007))

    peak_O3__4959  = peak_O3__5007/O3_ratio

    # Calculates the Gaussian emission line fluxes

    Gaussian_Hb__4863 = peak_Hb__4863*np.exp(-np.square((wave - obs_wave_Hb__4863)/sigma_Hb__4863)/2.0)
    Gaussian_O3__4959 = peak_O3__4959*np.exp(-np.square((wave - obs_wave_O3__4959)/sigma_O3__4959)/2.0)
    Gaussian_O3__5007 = peak_O3__5007*np.exp(-np.square((wave - obs_wave_O3__5007)/sigma_O3__5007)/2.0)

    # Calculates the continuum model

    continuum = x0 + x1*wave + x2*np.square(wave)

    # Returns the total model

    model = continuum + Gaussian_Hb__4863 + Gaussian_O3__4959 + Gaussian_O3__5007

    return model

###

def model_EmissionLinesAndContinuum_He1(wave, x0, x1, x2, zred, eline_sigma, flux_He1_5876):

    """
    Model fitting function to be used by lmfit centered around Halpha.

    Parameters:
    -----------
    wave : array
        Array of wavelengths, in units of microns
    x0 : float
        Zeroth component of the underlying continuum
    x1 : float
        First component for the underlying continuum
    x2 : float
        Second component for the underlying continuum
    zred : float
        Redshift, to be used on the red end of the spectrum
    eline_sigma : float
        Velocity dispersion for the emission lines, in units of km/s
    flux_He1_5876 : float
        Flux of the He1 5876 emission line, in the same units as the input spectrum
    """

    # Calculates observed-frame wavelengths

    obs_wave_He1_5876 = 1e-4*rest_wave_He1_5876*(1.0 + zred) # microns, observed-frame

    # Calculates the velocity dispersions after convolving with the line-spread function

    sigma_He1_5876 = np.sqrt(
        np.square((eline_sigma/c_kms)*obs_wave_He1_5876) + 
        np.square(obs_wave_He1_5876/(2.355*get_resolving_power(obs_wave_He1_5876))))

    # Calculates the peak line fluxes

    peak_He1_5876 = flux_He1_5876/np.sqrt(2*np.pi*np.square(sigma_He1_5876))

    # Calculates the Gaussian emission line fluxes

    Gaussian_He1_5876 = peak_He1_5876*np.exp(-np.square((wave - obs_wave_He1_5876)/sigma_He1_5876)/2.0)

    # Calculates the continuum model

    continuum = x0 + x1*wave + x2*np.square(wave)

    # Returns the total model

    model = continuum + Gaussian_He1_5876

    return model

###

def model_EmissionLinesAndContinuum_Ha(wave, x0, x1, x2, zred, eline_sigma, flux_Ha__6565):

    """
    Model fitting function to be used by lmfit centered around Halpha.

    Parameters:
    -----------
    wave : array
        Array of wavelengths, in units of microns
    x0 : float
        Zeroth component of the underlying continuum
    x1 : float
        First component for the underlying continuum
    x2 : float
        Second component for the underlying continuum
    zred : float
        Redshift, to be used on the red end of the spectrum
    eline_sigma : float
        Velocity dispersion for the emission lines, in units of km/s
    flux_Ha__6565 : float
        Flux of the Halpha emission line, in the same units as the input spectrum
    """

    # Calculates observed-frame wavelengths

    obs_wave_Ha__6565 = 1e-4*rest_wave_Ha__6565*(1.0 + zred) # microns, observed-frame

    # Calculates the velocity dispersions after convolving with the line-spread function

    sigma_Ha__6565 = np.sqrt(
        np.square((eline_sigma/c_kms)*obs_wave_Ha__6565) + 
        np.square(obs_wave_Ha__6565/(2.355*get_resolving_power(obs_wave_Ha__6565))))

    # Calculates the peak line fluxes

    peak_Ha__6565 = flux_Ha__6565/np.sqrt(2*np.pi*np.square(sigma_Ha__6565))

    # Calculates the Gaussian emission line fluxes

    Gaussian_Ha__6565 = peak_Ha__6565*np.exp(-np.square((wave - obs_wave_Ha__6565)/sigma_Ha__6565)/2.0)

    # Calculates the continuum model

    continuum = x0 + x1*wave + x2*np.square(wave)

    # Returns the total model

    model = continuum + Gaussian_Ha__6565

    return model

###

def model_EmissionLinesAndContinuum_Ha_with_S2(wave, x0, x1, x2, zred, eline_sigma, flux_Ha__6565, flux_S2__Doub, ratio_S2__Doub):

    """
    Model fitting function to be used by lmfit centered around Halpha.

    Parameters:
    -----------
    wave : array
        Array of wavelengths, in units of microns
    x0 : float
        Zeroth component of the underlying continuum
    x1 : float
        First component for the underlying continuum
    x2 : float
        Second component for the underlying continuum
    zred : float
        Redshift, to be used on the red end of the spectrum
    eline_sigma : float
        Velocity dispersion for the emission lines, in units of km/s
    flux_Ha__6565 : float
        Flux of the Halpha emission line, in the same units as the input spectrum
    flux_S2__Doub : float
        Flux of the [SII] doublet, in the same units as the input spectrum
    ratio_S2__Doub : float
        Emission line ratio of the [SII] doublet
    """

    # Calculates observed-frame wavelengths

    obs_wave_Ha__6565 = 1e-4*rest_wave_Ha__6565*(1.0 + zred) # microns, observed-frame
    obs_wave_S2__6716 = 1e-4*rest_wave_S2__6716*(1.0 + zred) # microns, observed-frame
    obs_wave_S2__6731 = 1e-4*rest_wave_S2__6731*(1.0 + zred) # microns, observed-frame

    # Calculates the velocity dispersions after convolving with the line-spread function

    sigma_Ha__6565 = np.sqrt(
        np.square((eline_sigma/c_kms)*obs_wave_Ha__6565) + 
        np.square(obs_wave_Ha__6565/(2.355*get_resolving_power(obs_wave_Ha__6565))))
    sigma_S2__6716 = np.sqrt(
        np.square((eline_sigma/c_kms)*obs_wave_S2__6716) + 
        np.square(obs_wave_S2__6716/(2.355*get_resolving_power(obs_wave_S2__6716))))
    sigma_S2__6731 = np.sqrt(
        np.square((eline_sigma/c_kms)*obs_wave_S2__6731) + 
        np.square(obs_wave_S2__6731/(2.355*get_resolving_power(obs_wave_S2__6731))))

    # Calculate the line fluxes in the [SII] doublet 

    flux_S2__6716 = flux_S2__Doub/(1.0 + ratio_S2__Doub)
    flux_S2__6731 = flux_S2__Doub/(1.0 + 1.0/ratio_S2__Doub)

    # Calculates the peak line fluxes

    peak_Ha__6565 = flux_Ha__6565/np.sqrt(2*np.pi*np.square(sigma_Ha__6565))
    peak_S2__6716 = flux_S2__6716/np.sqrt(2*np.pi*np.square(sigma_S2__6716))
    peak_S2__6731 = flux_S2__6731/np.sqrt(2*np.pi*np.square(sigma_S2__6731))

    # Calculates the Gaussian emission line fluxes

    Gaussian_Ha__6565 = peak_Ha__6565*np.exp(-np.square((wave - obs_wave_Ha__6565)/sigma_Ha__6565)/2.0)
    Gaussian_S2__6716 = peak_S2__6716*np.exp(-np.square((wave - obs_wave_S2__6716)/sigma_S2__6716)/2.0)
    Gaussian_S2__6731 = peak_S2__6731*np.exp(-np.square((wave - obs_wave_S2__6731)/sigma_S2__6731)/2.0)

    # Calculates the continuum model

    continuum = x0 + x1*wave + x2*np.square(wave)

    # Returns the total model

    model = continuum + Gaussian_Ha__6565 + Gaussian_S2__6716 + Gaussian_S2__6731

    return model

###

# When scale_covar is True, lmfit automatically scales the covariance matrix by the reduced chi-squared statistic. This is done to 
# account for the possibility that the input weights (or estimated uncertainties) are relative rather than absolute. If the model 
# fit is good and the input uncertainties accurately reflect the true uncertainties in the data, the reduced chi-squared should 
# be close to 1. If it's significantly different from 1, scaling the covariance matrix provides more realistic parameter uncertainties.

# One might choose to set scale_covar equal to False if they have very precise knowledge of their data uncertainties and are 
# confident that they are absolute. In such cases, you are essentially telling lmfit not to adjust the covariance matrix 
# based on the goodness of fit, as you believe your initial uncertainty estimates are already correct.

def emission_line_fitting(pathname, zred, wave, flux, flux_error, scale_covar=True, include_S2=True, 
    bootstrap=int(1e+2)):

    """
    Emission line fitting...

    Parameters:
    -----------
    pathname : str
        Path name for base directory to save output files
    zred : float
        Redshift used for calculating observed-frame wavelengths
    wave : np.array
        Array of wavelength values, in units of microns
    flux : np.array
        Array of flux values, in units of Jy
    flux_error : np.array
        Array of err values, in units of Jy
    scale_covar : bool
        Boolean for lmfit automatically scaling the covariance matrix by the reduced chi-squared statistic
    include_S2 : bool
        Boolean for lmfit fitting the [SII] 6716,6731 emission lines alongside Halpha
    bootstrap : int
        Number of bootstrap resamples to complete
    """

    # Defines hyperparameters for the model fitting...

    assert bootstrap > 0 and type(bootstrap) is int

    method, nanpolicy = 'leastsq', 'omit'

    x0_bool, x0_init, x0_min, x0_max = True, 0.0, -1e+2, +1e+2
    x1_bool, x1_init, x1_min, x1_max = True, 0.0, -1e+2, +1e+2
    x2_bool, x2_init, x2_min, x2_max = False, 0.0, -1e+2, +1e+2
    zred_bool, zred_init, zred_min, zred_max = True, zred, zred - 1e-1, zred + 1e-1
    eline_sigma_bool, eline_sigma_init, eline_sigma_min, eline_sigma_max = True, 1e+2, 1e+1, 1e+4
    flux_min, flux_max = 0.0, 1e+3 # None, None
    flux_prediction = 1e+1
    wave_delta = +0.5

    if include_S2: flux_prediction_S2 = flux_prediction/10.0
    else: flux_prediction_S2 = 0.0

    # Bootstrap resamples to provide accurate uncertainty estimates

    if bootstrap > 1: flux_bootstrapped = np.random.normal(loc=flux, scale=flux_error, size=(bootstrap, flux.shape[0]))

    else: flux_bootstrapped = [flux]

    Results_df = None

    for index in range(bootstrap):

        # Makes the relevant directories for saving the results

        if not os.path.exists(f'{pathname}/bootstrap_{index:03d}'): os.mkdir(f'{pathname}/bootstrap_{index:03d}')

        try:

            # First performs the model fitting for the region centered around Hbeta+[OIII]
            # The redshift and velocity dispersion derived here will be used for other emission lines to provide robust uncertainties

            Parameters_O3 = lmfit.Parameters()

            Parameters_O3.add_many(
                ('x0', x0_init, x0_bool, x0_min, x0_max),
                ('x1', x1_init, x1_bool, x1_min, x1_max),
                ('x2', x2_init, x2_bool, x2_min, x2_max),
                ('zred', zred_init, zred_bool, zred_min, zred_max),
                ('eline_sigma', eline_sigma_init, eline_sigma_bool, eline_sigma_min, eline_sigma_max),
                ('flux_Hb__4863', flux_prediction/10.0, True, flux_min, flux_max),
                ('flux_O3__5007', flux_prediction/3.0, True, flux_min, flux_max),
            )

            spec_model_O3 = lmfit.Model(model_EmissionLinesAndContinuum_O3, missing='drop')

            xmin_O3 = 1e-4*np.mean([rest_wave_Hb__4863, rest_wave_O3__5007])*(1.0 + zred) - wave_delta
            xmax_O3 = 1e-4*np.mean([rest_wave_Hb__4863, rest_wave_O3__5007])*(1.0 + zred) + wave_delta

            temp_mask = np.ones(flux.shape)

            mask = np.logical_and(temp_mask, np.logical_and(xmin_O3 <= wave, wave <= xmax_O3))

            Results_O3 = spec_model_O3.fit(np.flip(1e+9*flux_bootstrapped[index][mask]), 
                params=Parameters_O3, method=method, nanpolicy=nanpolicy, scale_covar=scale_covar, 
                weights=1.0/np.flip(1e+9*flux_error[mask]), 
                wave=np.flip(1e+0*wave[mask]))

            if bootstrap == 1: print(Results_O3.fit_report())
            temp_string = Results_O3.summary()['model']
            temp_string = temp_string[temp_string.find('(')+1:temp_string.find(')')]
            np.save(f'{pathname}/bootstrap_{index:03d}/Results_{temp_string.replace('model_', '')}.npy', 
                Results_O3.summary(), allow_pickle=True)
            if bootstrap == 1: plt.close(); Results_O3.plot(); plt.show(); plt.close()

            # Sets up the model parameters for the remaining emission line windows

            _eline_sigma_ = Results_O3.params['eline_sigma'].value

            _zred_ = Results_O3.params['zred'].value

            Parameters_O2 = lmfit.Parameters()
            Parameters_He1 = lmfit.Parameters()
            Parameters_Ha = lmfit.Parameters()

            Parameters_O2.add_many(
                ('x0', x0_init, True, x0_min, x0_max),
                ('x1', x1_init, True, x1_min, x1_max),
                ('x2', x2_init, False, x2_min, x2_max),
                ('zred', _zred_, False, zred_min, zred_max),
                ('eline_sigma', _eline_sigma_, False, eline_sigma_min, eline_sigma_max),
                ('flux_O2__Doub', flux_prediction/10.0, True, flux_min, flux_max),
                ('ratio_O2__Doub', 1.0, False, 0.2, 4.0),
            )

            Parameters_He1.add_many(
                ('x0', x0_init, True, x0_min, x0_max),
                ('x1', x1_init, False, x1_min, x1_max),
                ('x2', x2_init, False, x2_min, x2_max),
                ('zred', zred_init, zred_bool, zred_min, zred_max),
                ('eline_sigma', eline_sigma_init, eline_sigma_bool, eline_sigma_min, eline_sigma_max),
                ('flux_He1_5876', flux_prediction/10.0, True, flux_min, flux_max),
            )

            Parameters_Ha.add_many(
                ('x0', x0_init, True, x0_min, x0_max),
                ('x1', x1_init, False, x1_min, x1_max),
                ('x2', x2_init, False, x2_min, x2_max),
                ('zred', zred_init, zred_bool, zred_min, zred_max),
                ('eline_sigma', eline_sigma_init, eline_sigma_bool, eline_sigma_min, eline_sigma_max),
                ('flux_Ha__6565', flux_prediction/1.0, True, flux_min, flux_max),
                ('flux_S2__Doub', flux_prediction_S2, include_S2, flux_min, flux_max),
                ('ratio_S2__Doub', 1.0, False, 0.2, 4.0),
            )

            spec_model_O2 = lmfit.Model(model_EmissionLinesAndContinuum_O2, missing='drop')

            xmin_O2 = 1e-4*np.mean([rest_wave_O2__3727, rest_wave_O2__3729])*(1.0 + _zred_) - wave_delta
            xmax_O2 = 1e-4*np.mean([rest_wave_O2__3727, rest_wave_O2__3729])*(1.0 + _zred_) + wave_delta

            spec_model_He1 = lmfit.Model(model_EmissionLinesAndContinuum_He1, missing='drop')

            xmin_He1 = 1e-4*rest_wave_He1_5876*(1.0 + _zred_) - wave_delta
            xmax_He1 = 1e-4*rest_wave_He1_5876*(1.0 + _zred_) + wave_delta

            if include_S2:

                mean_rest_wave_S2 = np.mean([rest_wave_S2__6716, rest_wave_S2__6731])

                spec_model_Ha = lmfit.Model(model_EmissionLinesAndContinuum_Ha_with_S2, missing='drop')

                xmin_Ha = 1e-4*np.mean([rest_wave_Ha__6565, mean_rest_wave_S2])*(1.0 + _zred_) - wave_delta
                xmax_Ha = 1e-4*np.mean([rest_wave_Ha__6565, mean_rest_wave_S2])*(1.0 + _zred_) + wave_delta

            else:

                spec_model_Ha = lmfit.Model(model_EmissionLinesAndContinuum_Ha, missing='drop')

                xmin_Ha = 1e-4*rest_wave_Ha__6565*(1.0 + _zred_) - wave_delta
                xmax_Ha = 1e-4*rest_wave_Ha__6565*(1.0 + _zred_) + wave_delta

            # Performs the model fitting for the region centered around [OII]

            mask = np.logical_and(temp_mask, np.logical_and(xmin_O2 <= wave, wave <= xmax_O2))

            Results_O2 = spec_model_O2.fit(np.flip(1e+9*flux_bootstrapped[index][mask]), 
                params=Parameters_O2, method=method, nanpolicy=nanpolicy, scale_covar=scale_covar, 
                weights=1.0/np.flip(1e+9*flux_error[mask]), 
                wave=np.flip(1e+0*wave[mask]))

            if bootstrap == 1: print(Results_O2.fit_report())
            temp_string = Results_O2.summary()['model']
            temp_string = temp_string[temp_string.find('(')+1:temp_string.find(')')]
            np.save(f'{pathname}/bootstrap_{index:03d}/Results_{temp_string.replace('model_', '')}.npy', 
                Results_O2.summary(), allow_pickle=True)
            if bootstrap == 1: plt.close(); Results_O2.plot(); plt.show(); plt.close()

            # Performs the model fitting for the region centered around HeI

            mask = np.logical_and(temp_mask, np.logical_and(xmin_He1 <= wave, wave <= xmax_He1))

            Results_He1 = spec_model_He1.fit(np.flip(1e+9*flux_bootstrapped[index][mask]), 
                params=Parameters_He1, method=method, nanpolicy=nanpolicy, scale_covar=scale_covar, 
                weights=1.0/np.flip(1e+9*flux_error[mask]), 
                wave=np.flip(1e+0*wave[mask]))

            if bootstrap == 1: print(Results_He1.fit_report())
            temp_string = Results_He1.summary()['model']
            temp_string = temp_string[temp_string.find('(')+1:temp_string.find(')')]
            np.save(f'{pathname}/bootstrap_{index:03d}/Results_{temp_string.replace('model_', '')}.npy', 
                Results_He1.summary(), allow_pickle=True)
            if bootstrap == 1: plt.close(); Results_He1.plot(); plt.show(); plt.close()

            # Performs the model fitting for the region centered around Halpha

            mask = np.logical_and(temp_mask, np.logical_and(xmin_Ha <= wave, wave <= xmax_Ha))

            Results_Ha = spec_model_Ha.fit(np.flip(1e+9*flux_bootstrapped[index][mask]), 
                params=Parameters_Ha, method=method, nanpolicy=nanpolicy, scale_covar=scale_covar, 
                weights=1.0/np.flip(1e+9*flux_error[mask]), 
                wave=np.flip(1e+0*wave[mask]))

            if bootstrap == 1: print(Results_Ha.fit_report())
            temp_string = Results_Ha.summary()['model']
            temp_string = temp_string[temp_string.find('(')+1:temp_string.find(')')]
            np.save(f'{pathname}/bootstrap_{index:03d}/Results_{temp_string.replace('model_', '')}.npy', 
                Results_Ha.summary(), allow_pickle=True)
            if bootstrap == 1: plt.close(); Results_Ha.plot(); plt.show(); plt.close()

            # Creates pandas dataframe for storing all of the results of the model fitting

            var_names = np.concatenate([['model', 'x0', 'x1', 'zred', 'eline_sigma'], 
                Results_O2.var_names, Results_O3.var_names, Results_He1.var_names, Results_Ha.var_names])
            _, indices = np.unique(var_names, return_index=True)
            columns = var_names[np.sort(indices)]

            if Results_df is None: Results_df = pd.DataFrame(columns=columns)

            for i, Results in enumerate([Results_O2, Results_O3, Results_He1, Results_Ha]):

                model = Results.summary()['model']

                dictionary = {'model': model[model.find('(')+1:model.find(')')].replace('model_', '')}

                for j, column in enumerate(columns[1:]):

                    if column in Results.var_names:

                        if 'eline_sigma' in column: 

                            units = u.km/u.s

                        elif 'flux' in column: 

                            if 'O2__Doub' in column: temp_wave = 1e-4*np.mean([rest_wave_O2__3727, rest_wave_O2__3729])*(1.0 + zred)*u.um
                            elif 'Hb__4863' in column: temp_wave = 1e-4*rest_wave_Hb__4863*(1.0+zred)*u.um
                            elif 'O3__4959' in column: temp_wave = 1e-4*rest_wave_O3__4959*(1.0+zred)*u.um
                            elif 'O3__5007' in column: temp_wave = 1e-4*rest_wave_O3__5007*(1.0+zred)*u.um
                            elif 'He1_5876' in column: temp_wave = 1e-4*rest_wave_He1_5876*(1.0+zred)*u.um
                            elif 'Ha__6565' in column: temp_wave = 1e-4*rest_wave_Ha__6565*(1.0+zred)*u.um
                            elif 'S2__Doub' in column: temp_wave = 1e-4*np.mean([rest_wave_S2__6716, rest_wave_S2__6731])*(1.0 + zred)*u.um

                            units = u.um*(1e-3*u.uJy).to(u.erg/u.s/np.square(u.cm)/u.Hz) # (micron)*(erg/s/cm^2/Hz)
                            units *= astropy.constants.c/(np.square(temp_wave)) # erg/s/cm^2
                            units = (units).to(u.erg/u.s/np.square(u.cm)) # erg/s/cm^2

                        else: 

                            units = 1.0

                        value = Results.params[column].value
                        error = Results.params[column].stderr
                        error = error*units if error is not None else np.nan
                        value = value*units

                    else: 

                        value, error = np.nan, np.nan

                    dictionary.update({column: [value, error]})

                temp_Results_df = pd.DataFrame([dictionary])

                Results_df = pd.concat([Results_df, temp_Results_df], ignore_index=True)

            temp_string = temp_string.replace('_Ha', '')
            temp_string = temp_string.replace('model_', '')

            if bootstrap > 1: Results_df.to_csv(f'{pathname}/Bootstrapped_Results_{temp_string}.csv', index=False)

            else: Results_df.to_csv(f'{pathname}/Results_{temp_string}.csv', index=False)

        except Exception:

            pass

    # Bootstrapped statistics

    if bootstrap > 1: 

        Results_bootstrapped_statistics = []

        # Calculates x0 percentiles

        x0_samples = Results_df['x0'].values
        x0_samples_val = np.array([sample[0] for sample in x0_samples if not np.isnan(sample[0])])
        x0_samples_err = np.array([sample[1] for sample in x0_samples if not np.isnan(sample[1])])

        x0_p16, x0_p50, x0_p84  = np.percentile(x0_samples_val, [16, 50, 84])

        x0_mean, x0_std = np.nanmean(x0_samples_val), np.nanstd(x0_samples_val)

        Results_bootstrapped_statistics.append([
            x0_p16, x0_p50, x0_p84, x0_mean, x0_std])

        # Calculates x1 percentiles

        x1_samples = Results_df['x1'].values
        x1_samples_val = np.array([sample[0] for sample in x1_samples if not np.isnan(sample[0])])
        x1_samples_err = np.array([sample[1] for sample in x1_samples if not np.isnan(sample[1])])

        x1_p16, x1_p50, x1_p84  = np.percentile(x1_samples_val, [16, 50, 84])

        x1_mean, x1_std = np.nanmean(x1_samples_val), np.nanstd(x1_samples_val)

        Results_bootstrapped_statistics.append([
            x1_p16, x1_p50, x1_p84, x1_mean, x1_std])

        # Calculates zred percentiles

        zred_samples = Results_df['zred'].values
        zred_samples_val = np.array([sample[0] for sample in zred_samples if not np.isnan(sample[0])])
        zred_samples_err = np.array([sample[1] for sample in zred_samples if not np.isnan(sample[1])])

        zred_p16, zred_p50, zred_p84  = np.percentile(zred_samples_val, [16, 50, 84])

        zred_mean, zred_std = np.nanmean(zred_samples_val), np.nanstd(zred_samples_val)

        Results_bootstrapped_statistics.append([
            zred_p16, zred_p50, zred_p84, zred_mean, zred_std])

        # Calculates eline_sigma percentiles

        eline_sigma_samples = Results_df['eline_sigma'].values
        eline_sigma_samples_val = np.array([sample[0].value for sample in eline_sigma_samples if not np.isnan(sample[0])])
        eline_sigma_samples_err = np.array([sample[1].value for sample in eline_sigma_samples if not np.isnan(sample[1])])

        eline_sigma_p16, eline_sigma_p50, eline_sigma_p84  = np.percentile(eline_sigma_samples_val, [16, 50, 84])

        eline_sigma_mean, eline_sigma_std = np.nanmean(eline_sigma_samples_val), np.nanstd(eline_sigma_samples_val)

        Results_bootstrapped_statistics.append([
            eline_sigma_p16, eline_sigma_p50, eline_sigma_p84, eline_sigma_mean, eline_sigma_std])

        # Calculates flux_O2__Doub percentiles

        flux_O2__Doub_samples = Results_df['flux_O2__Doub'].values
        flux_O2__Doub_samples_val = np.array([sample[0].value for sample in flux_O2__Doub_samples if not np.isnan(sample[0])])
        flux_O2__Doub_samples_err = np.array([sample[1].value for sample in flux_O2__Doub_samples if not np.isnan(sample[1])])

        flux_O2__Doub_p16, flux_O2__Doub_p50, flux_O2__Doub_p84  = np.percentile(flux_O2__Doub_samples_val, [16, 50, 84])

        flux_O2__Doub_mean, flux_O2__Doub_std = np.nanmean(flux_O2__Doub_samples_val), np.nanstd(flux_O2__Doub_samples_val)

        Results_bootstrapped_statistics.append([
            flux_O2__Doub_p16, flux_O2__Doub_p50, flux_O2__Doub_p84, flux_O2__Doub_mean, flux_O2__Doub_std])

        # Calculates flux_Hb__4863 percentiles

        flux_Hb__4863_samples = Results_df['flux_Hb__4863'].values
        flux_Hb__4863_samples_val = np.array([sample[0].value for sample in flux_Hb__4863_samples if not np.isnan(sample[0])])
        flux_Hb__4863_samples_err = np.array([sample[1].value for sample in flux_Hb__4863_samples if not np.isnan(sample[1])])

        flux_Hb__4863_p16, flux_Hb__4863_p50, flux_Hb__4863_p84  = np.percentile(flux_Hb__4863_samples_val, [16, 50, 84])

        flux_Hb__4863_mean, flux_Hb__4863_std = np.nanmean(flux_Hb__4863_samples_val), np.nanstd(flux_Hb__4863_samples_val)

        Results_bootstrapped_statistics.append([
            flux_Hb__4863_p16, flux_Hb__4863_p50, flux_Hb__4863_p84, flux_Hb__4863_mean, flux_Hb__4863_std])

        # Calculates flux_O3__5007 percentiles

        flux_O3__5007_samples = Results_df['flux_O3__5007'].values
        flux_O3__5007_samples_val = np.array([sample[0].value for sample in flux_O3__5007_samples if not np.isnan(sample[0])])
        flux_O3__5007_samples_err = np.array([sample[1].value for sample in flux_O3__5007_samples if not np.isnan(sample[1])])

        flux_O3__5007_p16, flux_O3__5007_p50, flux_O3__5007_p84  = np.percentile(flux_O3__5007_samples_val, [16, 50, 84])

        flux_O3__5007_mean, flux_O3__5007_std = np.nanmean(flux_O3__5007_samples_val), np.nanstd(flux_O3__5007_samples_val)

        Results_bootstrapped_statistics.append([
            flux_O3__5007_p16, flux_O3__5007_p50, flux_O3__5007_p84, flux_O3__5007_mean, flux_O3__5007_std])

        # Calculates flux_He1_5876 percentiles

        flux_He1_5876_samples = Results_df['flux_He1_5876'].values
        flux_He1_5876_samples_val = np.array([sample[0].value for sample in flux_He1_5876_samples if not np.isnan(sample[0])])
        flux_He1_5876_samples_err = np.array([sample[1].value for sample in flux_He1_5876_samples if not np.isnan(sample[1])])

        flux_He1_5876_p16, flux_He1_5876_p50, flux_He1_5876_p84  = np.percentile(flux_He1_5876_samples_val, [16, 50, 84])

        flux_He1_5876_mean, flux_He1_5876_std = np.nanmean(flux_He1_5876_samples_val), np.nanstd(flux_He1_5876_samples_val)

        Results_bootstrapped_statistics.append([
            flux_He1_5876_p16, flux_He1_5876_p50, flux_He1_5876_p84, flux_He1_5876_mean, flux_He1_5876_std])

        # Calculates flux_Ha__6565 percentiles

        flux_Ha__6565_samples = Results_df['flux_Ha__6565'].values
        flux_Ha__6565_samples_val = np.array([sample[0].value for sample in flux_Ha__6565_samples if not np.isnan(sample[0])])
        flux_Ha__6565_samples_err = np.array([sample[1].value for sample in flux_Ha__6565_samples if not np.isnan(sample[1])])

        flux_Ha__6565_p16, flux_Ha__6565_p50, flux_Ha__6565_p84  = np.percentile(flux_Ha__6565_samples_val, [16, 50, 84])

        flux_Ha__6565_mean, flux_Ha__6565_std = np.nanmean(flux_Ha__6565_samples_val), np.nanstd(flux_Ha__6565_samples_val)

        Results_bootstrapped_statistics.append([
            flux_Ha__6565_p16, flux_Ha__6565_p50, flux_Ha__6565_p84, flux_Ha__6565_mean, flux_Ha__6565_std])

        # Calculates flux_S2__Doub percentiles

        if include_S2:

            flux_S2__Doub_samples = Results_df['flux_S2__Doub'].values
            flux_S2__Doub_samples_val = np.array([sample[0].value for sample in flux_S2__Doub_samples if not np.isnan(sample[0])])
            flux_S2__Doub_samples_err = np.array([sample[1].value for sample in flux_S2__Doub_samples if not np.isnan(sample[1])])

            flux_S2__Doub_p16, flux_S2__Doub_p50, flux_S2__Doub_p84  = np.percentile(flux_S2__Doub_samples_val, [16, 50, 84])

            flux_S2__Doub_mean, flux_S2__Doub_std = np.nanmean(flux_S2__Doub_samples_val), np.nanstd(flux_S2__Doub_samples_val)

            Results_bootstrapped_statistics.append([
                flux_S2__Doub_p16, flux_S2__Doub_p50, flux_S2__Doub_p84, flux_S2__Doub_mean, flux_S2__Doub_std])

    # Returns the results of the model fitting

    if bootstrap > 1: return Results_df, Results_bootstrapped_statistics

    else: return Results_df, Results_O2, Results_O3, Results_He1, Results_Ha

###

# https://www.scixplorer.org/abs/2024A%26A...684A..75C/abstract

def gas_phase_oxygen_abundance_function(x, line_ratio, c0=0.0, c1=0.0, c2=0.0, c3=0.0, c4=0.0, c5=0.0):

    """
    Function to optimize for inferring gas-phase oxygen abundances using standard strong-line diagnostics.

    Parameters:
    -----------
    x : float
        Gas-phase oxygen abundance, logarithmic
    line_ratio : float
        Emission line ratio diagnostic, logarithmic
    c0, c1, c2, c3, c4, c5 : floats
        Polynomial coefficients for inferring gas-phase oxygen abundances
    """

    return np.square(c0 + c1*np.power(x, 1) + c2*np.power(x, 2) + c3*np.power(x, 3) + c4*np.power(x, 4) + c5*np.power(x, 5) - line_ratio)

###

# https://www.scixplorer.org/abs/2024A%26A...684A..75C/abstract

def gas_phase_oxygen_abundance_calibration(diagnostic, line_ratios, branch='lower'):

    """
    Function for inferring gas-phase oxygen abundances using standard strong-line diagnostics.

    Parameters:
    -----------
    diagnostic : float
        Emission line ratio diagnostic to be used
    line_ratios : float or list of float
        Emission line ratio diagnostic, logarithmic
    branch : float
        Which branch to assume for the strong-line calibration (either "lower" or "upper")
    """

    assert branch.lower() in ('lower', 'upper'), f'Unknown branch: {branch.lower()} (Must be one of "lower" or "upper")'

    if diagnostic == 'R2':

        if branch.lower() == 'lower': bounds = (-2.0, -0.6)
        elif branch.lower() == 'upper': bounds = (-0.6, +1.0)

        c0, c1, c2, c3, c4, c5 = +0.4326, -1.0751, -5.1141, -5.5321, -2.3009, -0.2850

    elif diagnostic == 'R3':

        if branch.lower() == 'lower': bounds = (-2.0, -0.6)
        elif branch.lower() == 'upper': bounds = (-0.6, +1.0)

        c0, c1, c2, c3, c4, c5 = -0.2768, -3.1422, -2.7300, -0.6003, +0.0000, +0.0000

    elif diagnostic == 'R23':

        if branch.lower() == 'lower': bounds = (-2.0, -0.6)
        elif branch.lower() == 'upper': bounds = (-0.6, +1.0)

        c0, c1, c2, c3, c4, c5 = +0.5145, -1.4633, -1.3891, -0.2847, +0.0000, +0.0000

    elif diagnostic == 'Rhat':

        if branch.lower() == 'lower': bounds = (-2.0, -0.6)
        elif branch.lower() == 'upper': bounds = (-0.6, +1.0)

        c0, c1, c2, c3, c4, c5 = -0.0478, -3.0707, -3.4164, -1.0034, -0.0379, +0.0000

    else:

        raise ValueError(f'Unknown diagnostic: {diagnostic} (Must be one of "R2", "R3", "R23", or "Rhat").')

    if type(line_ratios) is list:

        calibrations = []

        for line_ratio in line_ratios:

            args = (line_ratio, c0, c1, c2, c3, c4, c5)

            try:

                calibrations.append(scipy.optimize.minimize(gas_phase_oxygen_abundance_function, 
                    np.mean(bounds), args=args, bounds=[bounds], method='Powell')['x'][0])

            except Exception:

                calibrations.append(np.nan)

        return calibrations

    else:

        args = (line_ratios, c0, c1, c2, c3, c4, c5)

        try:

            return scipy.optimize.minimize(gas_phase_oxygen_abundance_function, 
                np.mean(bounds), args=args, bounds=[bounds], method='Powell')['x'][0]

        except Exception:

            return np.nan

###

# Determines the V-band dust attenuation and its uncertainty from the Balmer decrement
# pip install git+https://github.com/karllark/dust_attenuation.git
# https://dust-attenuation.readthedocs.io/en/latest/

def _k_(wavelength_microns, attenuation_curve):

    """
    Returns A(\lambda)/A(V-band) from a dust attenuation curve object.

    Parameters:
    -----------
    wavelengths_microns : float
        Observed-frame wavelength in units of microns
    attenuation_curve : object
        Attenuation curve object from the dust_attenuation package

    Returns:
    --------
    float : A(\lambda)/A(V-band)
    """

    return float(attenuation_curve(1.0/wavelength_microns/u.um))

def attenuation_from_balmer_decrement(flux_ha, flux_hb, attenuation_curve, 
    Balmer_decrement_intrinsic=Balmer_decrement):

    """
    Returns the V-band dust attenuation determined by the observed Balmer decrement.

    Parameters:
    -----------
    flux_ha, flux_hb : floats
        Observed line fluxes (any units as long as they are consistent)
    attenuation_curve : object
        Attenuation curve object from the dust_attenuation package
    Balmer_decrement_intrinsic : float
        Intrinsic Balmer decrement from Case B recombination

    Returns:
    --------
    float : V-band dust attenuation in units of magnitudes
    """

    k_Ha = _k_(1e-4*rest_wave_Ha__6565, attenuation_curve)
    k_Hb = _k_(1e-4*rest_wave_Hb__4863, attenuation_curve)

    delta_k = k_Ha - k_Hb

    Balmer_decrement_observed = flux_ha/flux_hb

    return -2.5*np.log10(Balmer_decrement_observed/Balmer_decrement_intrinsic)/delta_k

def attenuation_monte_carlo(flux_ha, error_ha, flux_hb, error_hb, attenuation_curve, 
    Balmer_decrement_intrinsic=Balmer_decrement, N=int(1e+4)):

    """
    Returns the V-band dust attenuation determined by the observed Balmer decrement.
    Uncertainties are determined through Monte Carlo sampling.
    Uncertainties on fluxes are assumed to be Gaussian.

    Parameters:
    -----------
    flux_ha, flux_hb : floats
        Observed line fluxes (any units as long as they are consistent)
    error_ha, error_hb : floats
        Observed line flux errors (any units as long as they are consistent)
    attenuation_curve : object
        Attenuation curve object from the dust_attenuation package
    Balmer_decrement_intrinsic : float
        Intrinsic Balmer decrement from Case B recombination

    Returns:
    --------
    list of floats : V-band dust attenuation percentiles in units of magnitudes
    list of floats : V-band dust attenuation samples from Monte Carlo sampling
    """

    attenuation = attenuation_from_balmer_decrement(flux_ha, flux_hb, 
        attenuation_curve, Balmer_decrement_intrinsic=Balmer_decrement_intrinsic)

    samples_ha = np.random.normal(flux_ha, error_ha, N)
    samples_hb = np.random.normal(flux_hb, error_hb, N)

    samples_attenuation = []

    for sample_ha, sample_hb in zip(samples_ha, samples_hb):

        samples_attenuation.append(attenuation_from_balmer_decrement(sample_ha, sample_hb, 
            attenuation_curve, Balmer_decrement_intrinsic=Balmer_decrement_intrinsic))

    p05, p16, p50, p84, p95 = np.nanpercentile(samples_attenuation, [5, 16, 50, 84, 95])

    return [attenuation, p05, p16, p50, p84, p95], samples_attenuation

###

###

def validate_fluxratio_uncertainties(df, O3_ratio=O3_ratio, Balmer_decrement=Balmer_decrement, N=int(1e+4)):

    """
    Validates the analytic uncertainty estimates for the R3, R23, and Rhat
    strong-line diagnostics by comparing them to Monte Carlo resampling of
    the individual emission line fluxes.

    For each galaxy in df, each emission line is resampled N times from its
    Gaussian flux error distribution. The resulting MC uncertainty is taken
    as the half-width of the 16th-84th percentile interval. Galaxies using
    the Halpha/Balmer_decrement fallback denominator (i.e., where Hbeta is
    undetected) are handled consistently with the analytic index calculation.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing emission line fluxes, flux errors, and pre-computed
        index values and errors. Must contain the following columns: O2_3727_flux,
        O2_3727_flux_err, O3_5007_flux, O3_5007_flux_err, HBaB_4861_flux,
        HBaB_4861_flux_err, Blnd_HBaA_N2_flux, Blnd_HBaA_N2_flux_err,
        R3_val, R3_err, R23_val, R23_err, Rhat_val, Rhat_err, Name.
    O3_ratio : float
        Physical flux ratio [OIII]5007/[OIII]4959 computed from PyNeb emissivities.
    Balmer_decrement : float
        Intrinsic Halpha/Hbeta ratio from Case B recombination computed from PyNeb.
    N : int
        Number of Monte Carlo samples.

    Returns:
    --------
    dict : Dictionary with keys 'R3_mc_err', 'R23_mc_err', 'Rhat_mc_err', each a
           numpy array of MC uncertainties with length len(df).
    """

    # Extract flux and error arrays

    flux_O2 = df['O2_3727_flux'].values
    flux_O3 = df['O3_5007_flux'].values
    flux_Hb = df['HBaB_4861_flux'].values
    flux_Ha = df['Blnd_HBaA_N2_flux'].values

    flux_err_O2 = df['O2_3727_flux_err'].values
    flux_err_O3 = df['O3_5007_flux_err'].values
    flux_err_Hb = df['HBaB_4861_flux_err'].values
    flux_err_Ha = df['Blnd_HBaA_N2_flux_err'].values

    # Monte Carlo samples: shape (N, n_gal)

    samples_O2 = np.random.normal(flux_O2, flux_err_O2, size=(N, len(df)))
    samples_O3 = np.random.normal(flux_O3, flux_err_O3, size=(N, len(df)))
    samples_Hb = np.random.normal(flux_Hb, flux_err_Hb, size=(N, len(df)))
    samples_Ha = np.random.normal(flux_Ha, flux_err_Ha, size=(N, len(df)))

    # Fallback mask C: True for galaxies where Hbeta is undetected (nan or inf
    # from the primary log-ratio computation) and the Halpha/Balmer_decrement
    # denominator must be used instead.

    with np.errstate(divide='ignore', invalid='ignore'):

        C_R2 = ~np.isfinite(np.log10(flux_O2/flux_Hb))
        C_R3 = ~np.isfinite(np.log10(flux_O3/flux_Hb))
        C_R23 = ~np.isfinite(np.log10((flux_O2 + flux_O3*(1.0 + O3_ratio)/O3_ratio)/flux_Hb))

    # R2...

    with np.errstate(divide='ignore', invalid='ignore'):

        MC_R2_primary = np.log10(samples_O2/samples_Hb)
        MC_R2_fallback = np.log10(samples_O2/(samples_Ha/Balmer_decrement))

    MC_R2 = np.where(C_R2[np.newaxis, :], MC_R2_fallback, MC_R2_primary)

    # R3...

    with np.errstate(divide='ignore', invalid='ignore'):

        MC_R3_primary = np.log10(samples_O3/samples_Hb)
        MC_R3_fallback = np.log10(samples_O3/(samples_Ha/Balmer_decrement))

    MC_R3 = np.where(C_R3[np.newaxis, :], MC_R3_fallback, MC_R3_primary)

    # R23...

    with np.errstate(divide='ignore', invalid='ignore'):

        O3_total_samples = samples_O3*(1.0 + O3_ratio)/O3_ratio

        MC_R23_primary = np.log10((samples_O2 + O3_total_samples)/samples_Hb)
        MC_R23_fallback  = np.log10((samples_O2 + O3_total_samples)/(samples_Ha/Balmer_decrement))

    MC_R23 = np.where(C_R23[np.newaxis, :], MC_R23_primary, MC_R23_fallback)

    # Rhat...

    MC_Rhat = +0.47*MC_R2 + 0.88*MC_R3

    # MC uncertainties: half-width of the 16th-84th percentile interval

    MC_R2_err = +0.5*(np.nanpercentile(MC_R2, 84, axis=0) - np.nanpercentile(MC_R2, 16, axis=0))
    MC_R3_err = +0.5*(np.nanpercentile(MC_R3, 84, axis=0) - np.nanpercentile(MC_R3, 16, axis=0))
    MC_R23_err = +0.5*(np.nanpercentile(MC_R23, 84, axis=0) - np.nanpercentile(MC_R23, 16, axis=0))
    MC_Rhat_err = +0.5*(np.nanpercentile(MC_Rhat, 84, axis=0) - np.nanpercentile(MC_Rhat, 16, axis=0))

    # Print table to compare analytic and Monte Carlo sampled uncertainties

    names = df['Name'].values if 'Name' in df.columns else [str(i) for i in df.index]

    Analytic_R2_err = df['R2_err'].values
    Analytic_R3_err = df['R3_err'].values
    Analytic_R23_err = df['R23_err'].values
    Analytic_Rhat_err = df['Rhat_err'].values

    header = (
        f"{'Name':<25}  "
        f"{'Analytic R2':>12}  {'MC R2':>8}  {'Ratio':>6}  "
        f"{'Analytic R3':>12}  {'MC R3':>8}  {'Ratio':>6}  "
        f"{'Analytic R23':>12}  {'MC R23':>8}  {'Ratio':>6}  "
        f"{'Analytic Rhat':>12}  {'MC Rhat':>8}  {'Ratio':>6}  "
    ); print(header); print('-'*len(header))

    for index, name in enumerate(names):

        Analytic_R2, MC_R2 = Analytic_R2_err[index], MC_R2_err[index]
        Analytic_R3, MC_R3 = Analytic_R3_err[index], MC_R3_err[index]
        Analytic_R23, MC_R23 = Analytic_R23_err[index], MC_R23_err[index]
        Analytic_Rhat, MC_Rhat = Analytic_Rhat_err[index], MC_Rhat_err[index]

        print(
            f"{str(name):<25}  "
            f"{Analytic_R2:>12.4f}  {MC_R2:>8.4f}  {Analytic_R2/MC_R2:>6.3f}  "
            f"{Analytic_R3:>12.4f}  {MC_R3:>8.4f}  {Analytic_R3/MC_R3:>6.3f}  "
            f"{Analytic_R23:>12.4f}  {MC_R23:>8.4f}  {Analytic_R23/MC_R23:>6.3f}  "
            f"{Analytic_Rhat:>12.4f}  {MC_Rhat:>8.4f}  {Analytic_Rhat/MC_Rhat:>6.3f}  "
        )

    return {
        'MC_R2_err': MC_R2_err,
        'MC_R3_err': MC_R3_err,
        'MC_R23_err': MC_R23_err,
        'MC_Rhat_err': MC_Rhat_err,
    }

###