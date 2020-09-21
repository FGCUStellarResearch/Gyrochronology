import numpy as np
from scipy import signal

time = []
raw_flux = []
detrended_flux = []
background = []
x_pos = []
y_pos = []

def read_fits_data(fits_data):
    # First column is generally time, flux the 8th column, and quality the 10th.
    for idx in range(len(fits_data)):
        if fits_data[idx][9] > 0:
            continue
        time.append(fits_data[idx][0])
        raw_flux.append(fits_data[idx][7])
        background.append(fits_data['SAP_BKG'][idx])

def clean_fits():
    global time, raw_flux, detrended_flux

    # Remove nan values extracted from fits file.
    nan_idx = np.argwhere(np.isnan(raw_flux))
    time = np.delete(time, nan_idx)
    raw_flux = np.delete(raw_flux, nan_idx)

    # Detrend flux values for period analysis.
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