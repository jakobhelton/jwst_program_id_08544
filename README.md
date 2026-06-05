# JWST Program ID 8544

**Ionizing Photon Production Efficiencies and Chemical Abundances at Cosmic Dawn Revealed by Ultra-Deep Rest-Frame Optical Spectroscopy of JADES-GS-z14-0**

Helton et al. (2026), *The Astrophysical Journal Letters*

[![arXiv](https://img.shields.io/badge/arXiv-2512.19695-b31b1b.svg?style=flat)](https://arxiv.org/abs/2512.19695)
[![DOI](https://img.shields.io/badge/DOI-10.17909%2Fvpjw--b773-blue.svg?style=flat)](https://doi.org/10.17909/vpjw-b773)
[![JWST Pipeline](https://img.shields.io/badge/JWST%20Pipeline-v2.0.0-orange.svg?style=flat)](https://jwst-pipeline.readthedocs.io/en/stable/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat)](https://opensource.org/licenses/Apache-2.0)

---

## Overview

This repository contains the data products, reduction pipelines, analysis scripts, figures, and results associated with ultra-deep rest-frame optical spectroscopy of JADES-GS-z14-0, one of the most distant galaxies currently known at a spectroscopic redshift of $z \approx 14.18$. These observations were obtained by JWST/MIRI's Low Resolution Spectrometer (LRS) as part of JWST Cycle 4 Program #8544 (PI: Jakob M. Helton).

### Instrument

MIRI/LRS is a prism-based spectrograph that covers $\lambda_{\mathrm{obs}} \approx 5\text{-}14\ \mu\mathrm{m}$ at a spectral resolution of $R \approx 40\text{-}160$ (varying with wavelength). In slit spectroscopy mode, the source is placed on a fixed 0.51 × 4.7 arcsec slit and dispersed by the P750L prism+filter assembly onto the MIRI detector. Two dither positions along the slit (nod positions) allow the slit itself to serve as the background reference: alternating nod-pair subtractions remove detector glow, thermal background, and spatially smooth contamination. Compared to slitless mode, slit spectroscopy provides lower background levels and improved spectral purity at the cost of a smaller instantaneous field of view.

Further details on the MIRI/LRS observing mode are available in the [JWST User Documentation](https://jwst-docs.stsci.edu/jwst-mid-infrared-instrument/miri-observing-modes/miri-low-resolution-spectroscopy).

The combined spectrum totals approximately 183,800 seconds (~51 hours) of on-sky integration across three visits (Obs 002, Obs 003, and Obs 004; Obs 001 failed target acquisition). The data were collected on 2025 November 15–18 and 2026 January 1–2 using the FASTR1 readout pattern with 119 groups per integration.

### Data Reduction

Data were reduced using the standard [JWST Calibration Pipeline](https://jwst-pipeline.readthedocs.io/en/stable/) (version 2.0.0) with Calibration Reference Data System (version 13.1.14, pipeline mapping 1536), proceeding through three sequential stages:

- **Stage 1** (`Detector1Pipeline`): Detector-level corrections applied universally across all JWST instruments and modes, including linearity correction, saturation flagging, cosmic-ray jump detection, and ramp fitting to convert raw counts to count-rate images.
- **Stage 2** (`Spec2Pipeline`): Instrument- and mode-specific calibrations for spectroscopic data, including WCS assignment, flat-fielding, photometric calibration, background subtraction, and resampling of each exposure to a rectified 2D spectral frame.
- **Stage 3** (`Spec3Pipeline`): Combination of multiple calibrated exposures from a single association into a final mosaic and 1D extracted spectrum.

The custom reduction pipeline was developed by Jakob M. Helton and **Jane E. Morrison**, with Morrison serving as lead developer. Additional manual post-processing steps were applied at each stage to maximize signal quality for this faint, high-redshift source: custom V2/V3 reference coordinate tweaks to correct pointing offsets, nod-pair background subtraction, sigma-clipping and bad-pixel masking, trace-region masking, and optimal spectral extraction.

---

## Repository Contents

### `data/`

Raw downloads, pipeline association files, calibrated spectra, and supporting data products.

#### Download Scripts

Shell scripts for retrieving raw uncalibrated files from the Mikulski Archive for Space Telescopes (MAST). Each script targets one JWST observation visit.

| File | Description |
|---|---|
| `Download_PID08544_Obs1.sh` | Downloads raw files for Obs 001 (failed target acquisition) |
| `Download_PID08544_Obs2.sh` | Downloads raw files for Obs 002 (UT 2025 November 15–16; 8 exposures) |
| `Download_PID08544_Obs3.sh` | Downloads raw files for Obs 003 (UT 2025 November 17–18; 8 exposures) |
| `Download_PID08544_Obs4.sh` | Downloads raw files for Obs 004 (UT 2026 January 1–2; 8 exposures) |

Raw uncalibrated files are publicly available via [MAST](https://mast.stsci.edu/search/ui/#/jwst) (Program ID: 8544).

#### Pipeline Association Files

Modified Stage 3 association files used to process calibrated exposures through `Spec3Pipeline`. These were customized from the default MAST-generated associations to combine observations across visits.

| File | Description |
|---|---|
| `Stage3_All_association.json` | Association combining all 24 exposures from Obs 002, 003, and 004 |
| `Stage3_Obs002_association.json` | Association for the 8 exposures from Obs 002 alone |
| `Stage3_Obs003_association.json` | Association for the 8 exposures from Obs 003 alone |
| `Stage3_Obs004_association.json` | Association for the 8 exposures from Obs 004 alone |

#### Calibrated Spectra (FITS)

Output data products from Stage 3 of the JWST Calibration Pipeline. See `data/ReadMe.txt` for a complete description of the FITS file structure and column definitions.

| File | Size | Description |
|---|---|---|
| `jw08544_obsAll_t001_miri_p750l_s2d.fits` | ~1.1&nbsp;MB | Combined 2D rectified spectrum<br>All 24 exposures (Obs 002, 003, and 004) |
| `jw08544_obsAll_t001_miri_p750l_x1d.fits` | ~196&nbsp;KB | Combined 1D extracted spectrum<br>All 24 exposures (Obs 002, 003, and 004) |
| `jw08544_obsAll_t001_miri_p750l_0_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 0 (Obs 002) |
| `jw08544_obsAll_t001_miri_p750l_1_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 1 (Obs 002) |
| `jw08544_obsAll_t001_miri_p750l_2_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 2 (Obs 002) |
| `jw08544_obsAll_t001_miri_p750l_3_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 3 (Obs 002) |
| `jw08544_obsAll_t001_miri_p750l_4_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 4 (Obs 002) |
| `jw08544_obsAll_t001_miri_p750l_5_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 5 (Obs 002) |
| `jw08544_obsAll_t001_miri_p750l_6_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 6 (Obs 002) |
| `jw08544_obsAll_t001_miri_p750l_7_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 7 (Obs 002) |
| `jw08544_obsAll_t001_miri_p750l_8_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 8 (Obs 003) |
| `jw08544_obsAll_t001_miri_p750l_9_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 9 (Obs 003) |
| `jw08544_obsAll_t001_miri_p750l_10_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 10 (Obs 003) |
| `jw08544_obsAll_t001_miri_p750l_11_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 11 (Obs 003) |
| `jw08544_obsAll_t001_miri_p750l_12_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 12 (Obs 003) |
| `jw08544_obsAll_t001_miri_p750l_13_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 13 (Obs 003) |
| `jw08544_obsAll_t001_miri_p750l_14_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 14 (Obs 003) |
| `jw08544_obsAll_t001_miri_p750l_15_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 15 (Obs 003) |
| `jw08544_obsAll_t001_miri_p750l_16_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 16 (Obs 004) |
| `jw08544_obsAll_t001_miri_p750l_17_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 17 (Obs 004) |
| `jw08544_obsAll_t001_miri_p750l_18_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 18 (Obs 004) |
| `jw08544_obsAll_t001_miri_p750l_19_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 19 (Obs 004) |
| `jw08544_obsAll_t001_miri_p750l_20_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 20 (Obs 004) |
| `jw08544_obsAll_t001_miri_p750l_21_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 21 (Obs 004) |
| `jw08544_obsAll_t001_miri_p750l_22_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 22 (Obs 004) |
| `jw08544_obsAll_t001_miri_p750l_23_x1d.fits` | ~224&nbsp;KB | Individual 1D extracted spectrum<br>Exposure 23 (Obs 004) |

The 24 individual x1d files (exposures 0–23) allow verification of signal consistency across exposures and visits. They are also used to construct the empirical covariance matrix described below. Note that the flux uncertainties in the combined x1d file underestimate the true per-channel noise by approximately 40–45%; the empirical covariance matrix should be used for any quantitative analysis.

#### Pipeline Reference Files

Calibration reference and supporting data files required by `PID08544_Reduction_Pipeline_helper.py`.

| File | Size | Description |
|---|---|---|
| `jwst_miri_psf_0002.fits` | ~4.8&nbsp;MB | Empirical MIRI/LRS PSF model (CRDS reference; pedigree: INFLIGHT 2022-05-26 – 2024-08-05; author: A. Petric, STScI). Used to model the spatial PSF profile during optimal spectral extraction. |
| `resolving_power.csv` | ~270&nbsp;B | Tabulated spectral resolving power ($R = \lambda / \Delta\lambda$) versus observed-frame wavelength for MIRI/LRS. Two columns: `x` (wavelength, $\mu\mathrm{m}$) and `y` (resolving power $R$). Used to set the instrumental line spread function width during emission line fitting. |

#### Empirical Covariance Matrix

Derived from bootstrap resampling of the 24 individual x1d spectra to characterize correlated noise and noise inflation in the combined spectrum.

| File | Description |
|---|---|
| `empirical_covariance_matrix.csv` | Empirical covariance matrix in CSV format |
| `empirical_covariance_matrix.npy` | Empirical covariance matrix as a NumPy binary array |

#### Documentation and Environment

| File | Description |
|---|---|
| `ReadMe.txt` | Detailed description of the FITS data products, file structure, column definitions, and example Python access code (formatted as a standard journal data-behind-the-figure README) |
| `Conda_Environment_Instructions.txt` | Instructions for creating the conda environment required to run the reduction pipeline and analysis scripts |

---

### `figures/Paper1/`

Publication figures from Helton et al. (2026). Each figure is provided in JPEG, PDF, and PNG formats.

| Figure | Files | Description |
|---|---|---|
| Figure&nbsp;1 | <nobr>`Slit_Locations.{jpg,pdf,png}`</nobr> | On-sky positions of the MIRI/LRS slit for each of the four scheduled visits (Obs 001–004) overlaid on a JWST/NIRCam image of the JADES-GS-z14-0 field. Obs 001 failed target acquisition; Obs 002, 003, and 004 are the three science visits included in the analysis. |
| Figure&nbsp;2 | <nobr>`Full_Spectrum.{jpg,pdf,png}`</nobr> | Final combined MIRI/LRS spectrum of JADES-GS-z14-0 showing both the rectified 2D spectrum (from the s2d file) and the 1D extracted spectrum with $1\sigma$ uncertainty envelope (from the combined x1d file). The spectrum spans ${\approx}5.0\text{-}10.0\ \mu\mathrm{m}$ observed frame (${\approx}0.33\text{-}0.66\ \mu\mathrm{m}$ rest frame at $z = 14.18$). |
| Figure&nbsp;3 | <nobr>`ZoomIn_EmissionLines.{jpg,pdf,png}`</nobr> | Zoom-in views of the spectrum around the key detected emission features: [OII]λλ3726,3729 (marginal), Hβ + [OIII]λλ4959,5007 (${\approx}14\sigma$ combined), and Hα (${\approx}4\sigma$). Best-fit emission line models are overlaid. |
| Figure&nbsp;4 | <nobr>`LHalpha_vs_MUV.{jpg,pdf,png}`</nobr> | Hα luminosity versus absolute UV magnitude ($M_{\mathrm{UV}}$) for JADES-GS-z14-0 compared to a literature compilation of high-redshift galaxies. JADES-GS-z14-0 shows Hα luminosity broadly consistent with other $z > 10$ galaxies of similar UV brightness. |
| Figure&nbsp;5 | <nobr>`xi_ion_vs_zSpec_and_MUV.{jpg,pdf,png}`</nobr> | Ionizing photon production efficiency ($\xi_{\mathrm{ion}}$) as a function of spectroscopic redshift (left) and absolute UV magnitude (right) for JADES-GS-z14-0 compared to the literature. JADES-GS-z14-0 has $\log_{10}(\xi_{\mathrm{ion}}) \approx 25.3 \pm 0.1\ \mathrm{Hz\ erg^{-1}}$, among the highest values measured at any redshift. |
| Figure&nbsp;6 | <nobr>`O32_vs_R3_and_R23.{jpg,pdf,png}`</nobr> | Strong emission-line ratio diagnostics: O32 versus R3 (left) and O32 versus R23 (right) for JADES-GS-z14-0 overlaid on the grid of Cue photoionization models. These diagrams constrain the ionization parameter ($\log_{10} U \gtrsim -2.4$) and oxygen abundance (${12 + \log_{10}(\mathrm{O/H}) \approx 7.5 \pm 0.2}$). |
| Figure&nbsp;7 | <nobr>`logCtoO_vs_logOtoH.{jpg,pdf,png}`</nobr> | Carbon-to-oxygen ratio ($[\mathrm{C/O}]$) versus gas-phase oxygen abundance (${12 + \log_{10}(\mathrm{O/H})}$) for JADES-GS-z14-0 compared to literature measurements in high-redshift galaxies and local H II regions. JADES-GS-z14-0 has $[\mathrm{C/O}] \approx -0.4 \pm 0.2$, consistent with enrichment primarily by massive, short-lived stars with limited carbon contribution from AGB stars. |
| Figure&nbsp;8 | <nobr>`Cue_results_corner.{jpg,pdf,png}`</nobr> | Joint posterior probability distributions from the Cue neural-network photoionization model fitting to the observed emission line fluxes. Constrained parameters include gas-phase metallicity, ionization parameter, hydrogen gas density ($n_{\mathrm{H}} \approx 690 \pm 200\ \mathrm{cm^{-3}}$), and carbon-to-oxygen ratio. |

---

### `results/Cue/`

Output files from the Cue (Li et al. 2024, 2025) neural-network photoionization model fitting.

| File | Description |
|---|---|
| `GSz14_Cue_corner_plot_large.{jpg,pdf,png}` | Large-format version of the Cue posterior corner plot (Figure 8 equivalent with additional parameters shown) |
| `GSz14_Cue.pkl` | Main Cue fitting results: full posterior samples and derived physical properties |
| `GSz14_Cue_ionFlambda.pkl` | Cue ion flux-lambda data used for constructing the model spectrum |
| `GSz14_Cue_lineFluxData.pkl` | Posterior distributions of individual emission line fluxes from Cue |
| `GSz14_Cue_linePlotData.pkl` | Data arrays used to generate the Cue model line profile plots |

---

### `PID08544_Reduction_Pipeline_helper.py`

Custom JWST MIRI/LRS reduction pipeline helper script (developed by Jakob M. Helton and **Jane E. Morrison**). This script implements all three stages of the JWST Calibration Pipeline (version 2.0.0) with additional custom corrections and manual post-processing steps designed to maximize the signal quality of faint, high-redshift sources in MIRI/LRS slit spectroscopy.

Key capabilities include:

- **Stage 1** (`Detector1Pipeline`): Standard ramp-fitting and detector-level calibration
- **Stage 2** (`Spec2Pipeline`): Custom V2/V3 reference coordinate tweaks to correct pointing offsets, nod-pair background subtraction, sigma-clipping and bad-pixel masking, and trace-region masking
- **Stage 3** (`Spec3Pipeline`): Spectral combination and optimal 1D extraction using the modified association files in `data/`

The script requires the `REDUCTIONS_MIRI` environment variable to be set to the root directory of the local reduction tree. PSF model and resolving power table (`jwst_miri_psf_0002.fits` and `resolving_power.csv`) must be copied from `data/` into the `REDUCTIONS_MIRI` directory before running. Usage examples covering all four observations are included in the script's top-level docstring.

---

### `PID08544_Prospector_helper.py`

Prospector SED fitting helper script for modeling the broadband spectral energy distribution and emission-line properties of JADES-GS-z14-0. Built on the Prospector framework (Johnson et al. 2021) using FSPS stellar population models and the dynesty nested sampler.

Key capabilities include:

- Multiple star formation history (SFH) parameterizations: BurstyContinuity, Continuity, Rising, Constant, and DelayedTau
- IGM absorption, Lyman-series damping wing, and ionizing photon escape fraction as free parameters
- Joint fitting of JWST/NIRSpec spectra, MIRI/LRS spectra, broadband photometry, and ALMA continuum constraints
- Derived quantities: emission-line equivalent widths, star formation rates, stellar masses, and mass-weighted ages
- Diagnostic plots: trace plots, corner plots, and star formation history panels

---

## Software Requirements

The conda environment needed to run the reduction pipeline and analysis scripts is described in `data/Conda_Environment_Instructions.txt`. Key dependencies include:

[AstroPy](https://docs.astropy.org) | [corner](https://corner.readthedocs.io) | [Cue](https://github.com/yi-jia-li/cue) | [dynesty](https://dynesty.readthedocs.io) | [LMFIT](https://lmfit.github.io/lmfit-py) | [Matplotlib](https://matplotlib.org) | [NumPy](https://numpy.org) | [pandas](https://pandas.pydata.org) | [photutils](https://photutils.readthedocs.io) | [PyNeb](http://research.iac.es/proyecto/PyNeb) | [SciPy](https://scipy.org) | [seaborn](https://seaborn.pydata.org) | [specutils](https://specutils.readthedocs.io)

---

## Citation

If you use these data or scripts in your research, please cite:

```bibtex
@article{Helton2026,
  author        = {{Helton}, Jakob M. and {Morrison}, Jane E. and {Hainline}, Kevin N. and
                   {D'Eugenio}, Francesco and {Rieke}, George H. and {Alberts}, Stacey and
                   {Carniani}, Stefano and {Leja}, Joel and {Li}, Yijia and
                   {Rinaldi}, Pierluigi and {Scholtz}, Jan and {Stone}, Meredith and
                   {Willmer}, Christopher N.~A. and {Wu}, Zihao and {Baker}, William M. and
                   {Bunker}, Andrew J. and {Charlot}, St{\'e}phane and {Chevallard}, Jacopo and
                   {Cleri}, Nikko J. and {Curti}, Mirko and {Curtis-Lake}, Emma and
                   {Egami}, Eiichi and {Eisenstein}, Daniel J. and {Jakobsen}, Peter and
                   {Ji}, Zhiyuan and {Johnson}, Benjamin D. and {Kumari}, Nimisha and
                   {Lin}, Xiaojing and {Lyu}, Jianwei and {Maiolino}, Roberto and
                   {Maseda}, Michael and {P{\'e}rez-Gonz{\'a}lez}, Pablo G. and
                   {Rieke}, Marcia J. and {Robertson}, Brant and {Saxena}, Aayush and
                   {Sun}, Fengwu and {Tacchella}, Sandro and {{\"U}bler}, Hannah and
                   {Venturi}, Giacomo and {Williams}, Christina C. and {Willott}, Chris and
                   {Witstok}, Joris and {Zhu}, Yongda},
  title         = "{Ionizing Photon Production Efficiencies and Chemical Abundances at
                   Cosmic Dawn Revealed by Ultra-Deep Rest-Frame Optical Spectroscopy
                   of {JADES-GS-z14-0}}",
  journal       = {\apjl},
  year          = {2026},
  eprint        = {2512.19695},
  archivePrefix = {arXiv},
  primaryClass  = {astro-ph.GA},
}
```

MAST data DOI: [10.17909/vpjw-b773](https://doi.org/10.17909/vpjw-b773)

---

## Data Availability

Raw uncalibrated JWST files for Program 8544 are publicly available via [MAST](https://mast.stsci.edu/search/ui/#/jwst) (Program ID: 8544).
