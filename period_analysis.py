import File_Management
import algorithms as alg
import numpy as np

File_Management.read_input_file()

time, detrended_flux, background = File_Management.get_data()
# Change values in columns to float values for later processing.
time = [float(data) for data in time]
detrended_flux = [float(data) for data in detrended_flux]
noise = [float(data) for data in background]

nan_idx = np.argwhere(np.isnan(detrended_flux))
time = np.delete(time, nan_idx)
detrended_flux = np.delete(detrended_flux, nan_idx)
alg.calcPeriods(np.asarray(time), np.array(detrended_flux))