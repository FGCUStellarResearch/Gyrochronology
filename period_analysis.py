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
from scipy import fftpack
from nfft import nfft
import scipy.interpolate
from scipy.signal import find_peaks
from astropy.convolution import convolve, Box1DKernel



# Period finder, soon to utilize four different algorithms find periods in a data set.
def calcPeriods(time, flux, snr):
    plotLombScargle(time, detrended_flux)
    #autoCorr(time, flux)
    #wavelets(time,flux)
    #dft(time,flux)

# Plotting the Lomb-Scargle Algorithm.
def plotLombScargle(time, flux):
    # Plotting the raw time and detrended flux from the input file.
    # plt.plot(time, flux)
    # plt.show()


    tot_time = np.max(time) - np.min(time)

    # Plotting the period with the Lomb-Scargle method. 
    frequency,power = LombScargle(time, flux).autopower()

    # Estimate of noise based on the std of power values.
    noise = np.std(np.diff(power))
    print(noise)

    # Truncate arrays to only view the first peak of the periodogram.
    frequency = frequency[:int(len(frequency) * .0025)]
    power = power[:int(len(power) * .0025)]

    # Index with max power.
    peak_index = np.where(power == np.max(power))[0][0]

    # Create new frequency list with interpolated power values to find the first value more than one noise level below.
    min_freq = .5 * frequency[peak_index]
    max_freq = 2 * frequency[peak_index]
    freq_step = (max_freq - min_freq)/100
    new_freq = np.arange(min_freq, max_freq, freq_step)

    # Create object to interpolate power values from created frequency values.
    pchip_obj = scipy.interpolate.PchipInterpolator(frequency, power)
    new_power = pchip_obj(new_freq)

    # Index of the maximum power value inside new_power
    new_peak = np.where(new_power == np.max(new_power))[0][0]
    
    # Split frequencies into upper and lower ranges to identify different errors when moving to a higher frequency and a lower frequency. 
    upper_pow = new_power[new_peak:]
    upper_freq = new_freq[new_peak:]
    lower_pow = new_power[:new_peak]
    lower_freq = new_freq[:new_peak]

    # Index of frequency values lower than the difference of peak - noise. 
    f_max = new_peak + np.argmax(upper_pow < power[peak_index] - noise)
    f_min = np.max(np.where(lower_pow < power[new_peak]-noise))
    print(f_max)
    print(f_min)
    max_freq = new_freq[new_peak]

    min_period = 1/new_freq[f_max]
    max_period = 1/new_freq[f_max]
    upp_err = max_period - 1/max_freq
    low_err = (1/max_freq) - min_period
    ls_upp_err = np.fmax(1/tot_time, upp_err)
    ls_low_err = np.fmax(1/tot_time, low_err)

    print('period =', 1/max_freq, "+", ls_upp_err, "-", ls_low_err)

    plt.plot(new_freq, new_power)
    plt.title("Lomb-Scargle Periods")
    plt.xlabel("Frequency - Cycles/Day")
    plt.ylabel("Power")
    plt.show()


def autoCorr(time, flux):
    # Lag for this data is half the  number of days in K2 observations(40) multiplied by the amount of observations per day - 48 (30 min cadence)
    lag = ((max(time) - min(time))/2) * 48

    #noisy_signal = np.std(np.diff(lag))

    
    noisy_signal = np.array(flux)

    smooth_signal = convolve(noisy_signal, Box1DKernel(31))
    # #scipy.signal.find_peaks(x, height = None, threshold = None, distance = None, prominence = None, width = None, wlen= None, rel_height = 0.5, plateau_size = None)

    locs, _ = scipy.signal.find_peaks(smooth_signal, distance = 100)
    pks = smooth_signal[locs]

    #plot_acf(flux, lags = lag)
    #plot_acf(smooth_signal, lags = lag)
    
    plot_acf(pks)
    plt.title('Autocorrelation of K2 flux values')
    plt.xlabel('Lag')
    plt.ylabel('Autocorrelation')
    plt.show()

#def wavelets(time, flux):

    #  wavelet = 'cmor1.5-1.0'
    
    #  wave , period = pywt.dwt(signal.detrend(flux)/np.mean(flux),stats.mode(np.diff(time)))
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

    #scg.set_default_wavelet('cmor2-3.0')

    # time, flux = pywt.data.nino()
    # dt = time[1] - time[0]

    # Taken from http://nicolasfauchereau.github.io/climatecode/posts/wavelet-analysis-in-python/
    #wavelet = 'cmor2-1.5'
    #scales = np.arange(1, 20)
    # scales = scg.periods2scales(0.05*np.arange(1, 1000))
    # ax = scg.cws(time, flux - np.mean(flux), scales = scales, figsize = (7,2))

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

def dft(time, flux):
    # fhat = fftpack.fft(flux)
    # N = len(fhat)
    # '''
    # plt.plot([*range(0,N, 1)],fhat)
    # plt.title('Fast Fourier Transform')
    # plt.xlabel('Frequency')
    # plt.ylabel('Density')
    # plt.show()
    # '''

    NFFT = 1024
    f = fftpack.fft(time, NFFT)
    nVals = np.arange(start = 0, stop = NFFT)
    plt.plot(nVals, f)
    plt.show()
   


    
   

# Function found online. Used to find uncertainty.
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]
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

calcPeriods(time, detrended_flux, noise)
