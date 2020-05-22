import numpy as np
import astropy as ap
from astropy.timeseries import LombScargle
import matplotlib.pyplot as plt
import csv
import pandas as pd
import os
from scipy.fft import fft

# Period finder, soon to utilize four different algorithms find periods in a data set.
def calcPeriods(time, flux, snr):
    #plotLombScargle(time, detrended_flux)
    DFT(time, flux, snr)

# Plotting the Lomb-Scargle Algorithm.
def plotLombScargle(time, flux):
    # Plotting the raw time and detrended flux from the input file.
    plt.plot(time, flux)
    plt.show()

    # Plotting the period with the Lomb-Scargle method. 
    frequency,power = LombScargle(time, flux).autopower()
    plt.plot(frequency, power)
    plt.title("Lomb-Scargle Periods")
    plt.xlabel("Frequency - Cycles/Day")
    plt.ylabel("Power")
    plt.show()

def DFT(time, flux, snr):
    N = len(flux)

#Arrays to hold each column of data of the input file.
time = []
raw_flux = []
detrended_flux = []
background = []
x_pos = []
y_pos = []


# Reading input file
with open("example_K2_input.csv") as input_file:
    read_input = csv.reader(input_file, delimiter = ",")
    # Read each line and append data points to corresponding lists
    for line in read_input:
        time.append(line[0])
        raw_flux.append(line[1])
        detrended_flux.append(line[2])
        background.append(line[3])
        x_pos.append(line[4])
        y_pos.append(line[5])


# Change values in columns to float values for later processing.
time = [float(data) for data in time]
detrended_flux = [float(data) for data in detrended_flux]
raw_flux = [float(data) for data in raw_flux]
noise = [float(data) for data in background]
# Calculate the signal to noise ratio for data set. 
snr = [signal/noise for signal,noise in zip(detrended_flux, noise)]

calcPeriods(time, detrended_flux, snr)