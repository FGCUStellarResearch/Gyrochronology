import File_Management
import algorithms as alg
import numpy as np

File_Management.read_input_file()

time, detrended_flux, background = File_Management.get_data()
# Change values in columns to float values for later processing.
time = [float(data) for data in time]
detrended_flux = [float(data) for data in detrended_flux]
noise = [float(data) for data in background]


alg.calcPeriods(np.asarray(time), np.array(detrended_flux))