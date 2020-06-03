import numpy as np
import astropy as ap
from astropy.timeseries import LombScargle
from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.graphics.tsaplots import plot_acf
import matplotlib.pyplot as plt
import csv
import pandas as pd
import os
from scipy.fftpack import fft
import scaleogram as scg
import pywt
from scipy import signal
from scipy import stats



# Period finder, soon to utilize four different algorithms find periods in a data set.
def calcPeriods(time, flux, snr):
    #plotLombScargle(time, detrended_flux)
    #autoCorr(time, flux)
    wavelets(time,flux)

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

def autoCorr(time, flux):
    # Lag for this data is half the  number of days in K2 observations(40) multiplied by the amount of observations per day - 48 (30 min cadence)
    lag = ((max(time) - min(time))/2) * 48
    plot_acf(flux, lags = lag)
    plt.title('Autocorrelation of K2 flux values')
    plt.xlabel('Lag')
    plt.ylabel('Autocorrelation')
    plt.show()

def wavelets(time, flux):

    #  wavelet = 'cmor1.5-1.0'
    
    #  [wave , period] = pywt.cwt(signal.detrend(flux)/np.mean(flux),stats.mode(np.diff(time)))
    #  awave = abs(wave)

    #  plt.plot(awave/max(awave), period)
     
    #  plt.xticks(visible = False)
    #  plt.yticks(visible = False)
    #  plt.xlabel('Time (d)')
    #  plt.ylabel('Period (d)')
    #  plt.title('Wavelet')
    #  plt.colorbar()
    #  plt.show()
    # # # colormap jet

    scg.set_default_wavelet('cmor2-3.0')

    # time, flux = pywt.data.nino()
    # dt = time[1] - time[0]

    # Taken from http://nicolasfauchereau.github.io/climatecode/posts/wavelet-analysis-in-python/
    #wavelet = 'cmor2-1.5'
    #scales = np.arange(1, 20)
    scales = scg.periods2scales(0.05*np.arange(1, 1000))
    ax = scg.cws(time, flux - np.mean(flux), scales = scales, figsize = (7,2))

    # [cfs, frequencies] = pywt.cwt(flux, scales, wavelet, dt)
    # power = (abs(cfs)) 

    # period = 1. / frequencies
    # levels = [0.0625, 0.125, 0.25, 0.5, 1, 2, 4, 8]
    # f, ax = plt.subplots(figsize=(15, 10))
    # ax.contourf(time, np.log2(period), np.log2(power), np.log2(levels),
    #             extend='both')

    # ax.set_title('%s Wavelet Power Spectrum (%s)' % ('Nino1+2', wavelet))
    # ax.set_ylabel('Period (years)')
    # Yticks = 2 ** np.arange(np.ceil(np.log2(period.min())),
    #                         np.ceil(np.log2(period.max())))
    # ax.set_yticks(np.log2(Yticks))
    # ax.set_yticklabels(Yticks)
    # ax.invert_yaxis()
    # ylim = ax.get_ylim()
    # ax.set_ylim(ylim[0], -1)

    plt.show()
    



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