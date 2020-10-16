import numpy as np
import pandas as pd
import scipy as sp
from scipy import signal
from math import nan

time = []
raw_flux = []
detrended_flux = []
background = []
x_pos = []
y_pos = []

def read_fits_data(fits_data):
    # First column is generally time, flux the 8th column, and quality the 10th.
    for idx in range(len(fits_data)):
        #Code to check for gap in TESS observation.
        if fits_data[idx][9] == 8 or fits_data[idx][9] == 136:
            time.append(0)
            raw_flux.append(0)    
        if fits_data[idx][9] > 0:
            continue
        time.append(fits_data[idx][0])
        raw_flux.append(fits_data[idx][7])
        background.append(fits_data['SAP_BKG'][idx])

def clean_tess():
    global time, raw_flux, detrended_flux
    
    #Index of zero values, used to find gap in TESS data.
    nan_idx = np.argwhere(np.asarray(time) == 0)
    # Taking the most frequent spacing value, excluding the values that are zero.
    time_mode = sp.stats.mode(np.diff(np.delete(time, nan_idx)), axis=None)[0]

    # Change each zero value, to appropriate mode-spaced time values.
    for idx in nan_idx:
        time[idx[0]] = time[idx[0]- 1] + time_mode
        raw_flux[idx[0]] = nan


    # Attempting interpolation of flux values by using PANDAS
    flux = pd.Series(raw_flux)
    flux = flux.interpolate(method = 'slinear')
    detrended_flux = flux.tolist()

def clean_k2():
    global time, raw_flux, detrended_flux

    nan_idx = np.argwhere(np.isnan(raw_flux))

    time =  np.delete(time, nan_idx)
    raw_flux = np.delete(raw_flux, nan_idx)

    detrended_flux = signal.detrend(raw_flux)

def read_csv_data(csv_file):
    for line in csv_file:
        time.append(line[0])
        raw_flux.append(line[1])
        detrended_flux.append(line[2])
        background.append(line[3])
        x_pos.append(line[4])
        y_pos.append(line[5])

def get_data():
    return (time, detrended_flux, background)