==========================================================================
README | Data Behind the Figure — Final MIRI/LRS Spectra of JADES-GS-z14-0
JWST Program ID 8544 (PI: Jakob M. Helton)
Helton et al. (2026), Figure 2
==========================================================================

------
TARGET
------

Name: JADES-GS-z14-0
RA: +53.082937 degrees (J2000)
Dec: -27.855633 degrees (J2000)
Spectroscopic Redshift: z ~ 14.18

------------
OBSERVATIONS
------------

Instrument and Observing Mode: JWST/MIRI's Low Resolution Spectrometer (LRS)
Wavelength Coverage: ~ 5.0–14.0 microns (observed frame)
Disperser/Filter: P750L

Observing Strategy: Slit spectroscopy adopting the FASTR1 readout pattern with 
    119 groups per integration, 23 integrations per exposure, 4 exposures per 
    dither, 2 dithers along slit nod per visit, and 3 visits in total;
    the 3 visits are from JWST Program 8544 (Obs 002, 003, and 004)
Effective Exposure Time: 183,752 seconds (~ 51.0 hours)
Observation Dates: 2025 November 15 — 2026 January 2

--------------
DATA REDUCTION
--------------

Reduced using the standard JWST Calibration Pipeline (version 2.0.0) with 
Calibration Reference Data System (version 13.1.14) pipeline mapping (1536).
The three visits were combined into a single spectral association ("obsAll") and
processed through the standard Spec3Pipeline. Custom corrections and manual
post-processing steps were added to improve the final data quality.

-------------------------
FILES INCLUDED (26 total)
-------------------------

jw08544_obsAll_t001_miri_p750l_s2d.fits         (~ 1.1 MB)
    Combined rectified 2D spectrum from all 24 exposures.

jw08544_obsAll_t001_miri_p750l_x1d.fits         (~ 196 KB)
    Combined 1D extracted spectrum from all 24 exposures.

jw08544_obsAll_t001_miri_p750l_{0–7}_x1d.fits   (~ 224 KB each; 8 files)
    Individual 1D spectra for each of the 8 exposures from Obs 002
    (UT 2025 November 15–16).

jw08544_obsAll_t001_miri_p750l_{8–15}_x1d.fits  (~ 224 KB each; 8 files)
    Individual 1D spectra for each of the 8 exposures from Obs 003
    (UT 2025 November 17-18).

jw08544_obsAll_t001_miri_p750l_{16–23}_x1d.fits (~ 224 KB each; 8 files)
    Individual 1D spectra for each of the 8 exposures from Obs 004
    (UT 2026 January 1–2).

-------------------
FITS FILE STRUCTURE
-------------------

s2d file:

  HDU 0  PRIMARY     Observation metadata
  HDU 1  SCI         Rectified 2D science image [398 x 65 pixels]; MJy/sr
                       Axis 1 ( 65 pixels): cross-dispersion
                       Axis 2 (398 pixels): dispersion
  HDU 2  ERR         1-sigma uncertainty [398 x 65 pixels]; MJy/sr
  HDU 3  WAVELENGTH  Wavelength solution [398 x 65 pixels]; microns
  HDU 4  WHT         Coverage map (contributing exposures per pixel)
  HDU 5  CON         Context array (bitmask showing contributing frames)
  HDU 6  VAR_POISSON Poisson variance image  [398 x 65 pixels]; (MJy/sr)^2
  HDU 7  VAR_RNOISE  Read noise variance image [398 x 65 pixels]; (MJy/sr)^2
  HDU 8  VAR_FLAT    Flat-field variance image [398 x 65 pixels]; (MJy/sr)^2
  HDU 9  HDRTAB      Binary table, 24 rows — full header metadata per input exposure

x1d files (combined and individual):

  HDU 0  PRIMARY     Observation metadata
  HDU 1  EXTRACT1D   Binary table, 381 rows (combined) / 380 rows (individual)

    Column           Units       Description
    WAVELENGTH       microns     Observed-frame wavelength
    FLUX             Jy          Flux density
    FLUX_ERROR       Jy          1-sigma flux density uncertainty
    FLUX_VAR_POISSON Jy^2        Poisson variance component
    FLUX_VAR_RNOISE  Jy^2        Read noise variance component
    FLUX_VAR_FLAT    Jy^2        Flat-field variance component
    SURF_BRIGHT      MJy/sr      Surface brightness
    SB_ERROR         MJy/sr      1-sigma surface brightness uncertainty
    SB_VAR_POISSON   (MJy/sr)^2  Poisson variance component
    SB_VAR_RNOISE    (MJy/sr)^2  Read noise variance component
    SB_VAR_FLAT      (MJy/sr)^2  Flat-field variance component
    DQ               —           Data quality flag (0 = good)
    BACKGROUND       MJy/sr      Background estimate
    BKGD_ERROR       MJy/sr      1-sigma background uncertainty
    BKGD_VAR_POISSON (MJy/sr)^2  Background Poisson variance
    BKGD_VAR_RNOISE  (MJy/sr)^2  Background read noise variance
    BKGD_VAR_FLAT    (MJy/sr)^2  Background flat-field variance
    NPIXELS          —           Pixels summed in cross-dispersion direction

-----------------------
RELATIONSHIP TO FIGURE
-----------------------

Figure 2 shows the combined MIRI/LRS spectrum of JADES-GS-z14-0 at z ~ 14.18.

  - The spectral trace uses WAVELENGTH and FLUX from
    jw08544_obsAll_t001_miri_p750l_x1d.fits (HDU 1, EXTRACT1D).
  - The shaded 1-sigma envelope uses FLUX_ERROR from the same file.
  - The 2D spectral panel uses HDU 1 (SCI) of the s2d file with wavelength 
    from HDU 3 (WAVELENGTH).
  - The 24 individual x1d files allow readers to verify the signal
    consistency across exposures and visits. These are also used
    to derive the noise inflation term described in the paper.

--------
SOFTWARE
--------

These files conform to the standard JWST Calibration Pipeline output using FITS format.

Recommended software: astropy (https://docs.astropy.org), numpy (https://numpy.org).

Example Python access:

  import numpy as np

  from astropy.io import fits

  # Read the combined 2D spectrum

  with fits.open('jw08544_obsAll_t001_miri_p750l_s2d.fits') as hdul_s2d:

      wave_data_s2d = np.flip(hdul_s2d['WAVELENGTH'].data, axis=0).T
      err_data = np.flip(hdul_s2d['ERR'].data, axis=0).T
      sci_data = np.flip(hdul_s2d['SCI'].data, axis=0).T

      PIXAR_A2 = hdul_s2d[1].header['PIXAR_A2']

  # Read the combined 1D spectrum

  with fits.open('jw08544_obsAll_t001_miri_p750l_x1d.fits') as hdul_x1d:

      data_x1d = hdul_x1d['EXTRACT1D'].data

      column_names = data_x1d.columns.names

      wave_data = data_x1d.field(np.where(np.array(column_names) == 'WAVELENGTH')[0][0])[::-1]
      flux_data = data_x1d.field(np.where(np.array(column_names) == 'FLUX')[0][0])[::-1]
      flux_error_data = data_x1d[np.array(column_names)[np.char.find(column_names, 'ERROR') != -1][0]][::-1]

  # Read all 24 individual 1D spectra

  individual_x1d_files = [f'jw08544_obsAll_t001_miri_p750l_{i}_x1d.fits' for i in range(24)]

  array_flux_data = []

  for filename in individual_x1d_files:

      with fits.open(filename) as hdul_x1d:

          temp_data = hdul_x1d['EXTRACT1D'].data

          temp_columns = temp_data.columns.names

          temp_flux = temp_data.field(np.where(np.array(temp_columns) == 'FLUX')[0][0])

          array_flux_data.append(np.flip(temp_flux))

-----------------
DATA AVAILABILITY
-----------------

Raw uncalibrated files for JWST Program 8544 are publicly available via MAST:
  https://mast.stsci.edu/search/ui/#/jwst (Program ID: 8544)
