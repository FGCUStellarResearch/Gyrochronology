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
#from scipy.linalg import dft
#from udf import *



# Period finder, soon to utilize four different algorithms find periods in a data set.
def calcPeriods(time, flux, snr):
    #plotLombScargle(time, detrended_flux)
    autoCorr(time, detrended_flux)
    #wavelets(time,flux)
    #dft(time,flux)

# Plotting the Lomb-Scargle Algorithm.
def plotLombScargle(time, flux):

    tot_time = np.max(time) - np.min(time)

    # Plotting the period with the Lomb-Scargle method. 
    frequency,power = LombScargle(time, flux).autopower()

    # Estimate of noise based on the std of power values.
    noise = np.std(np.diff(power))

    # Truncate arrays to only view the first peak of the periodogram.
    frequency = frequency[:int(len(frequency) * .0025)]
    power = power[:int(len(power) * .0025)]

    find_uncertainty(frequency, power, tot_time, noise)

    plt.plot(frequency, power)
    plt.title("Lomb-Scargle Periods")
    plt.xlabel("Frequency - Cycles/Day")
    plt.ylabel("Power")
    plt.show()

def find_uncertainty(frequency, power, tot_time, noise):

    # Index with max power.
    peak_index = np.where(power == np.max(power))[0][0]
    max_freq = frequency[peak_index]
    print(peak_index)

    # Create new frequency list with interpolated power values to find the first value more than one noise level below.
    freq_low = .5 * max_freq
    freq_high = 2 * max_freq
    freq_step = (freq_high - freq_low)/100
    new_freq = np.arange(freq_low, freq_high, freq_step)

    # Create object to interpolate power values from created frequency values.
    pchip_obj = scipy.interpolate.PchipInterpolator(frequency, power)
    new_power = pchip_obj(new_freq)

    # Index of the maximum power value inside new_power
    new_peak = np.where(new_power == np.max(new_power))[0][0]
    
    # Split frequencies into upper and lower ranges to identify higher and lower uncertainties.
    upper_pow = new_power[new_peak:]
    lower_pow = new_power[1:new_peak]

    # Index of frequency values lower than the difference of peak - noise. 
    f_max = new_peak + np.argmax(upper_pow < power[peak_index] - noise)
    f_min = np.max(np.where(lower_pow < power[peak_index]-noise))
    print(f_min)

    min_period = 1/new_freq[f_max]
    max_period = 1/new_freq[f_min]
    upp_err = max_period - 1/max_freq
    low_err = (1/max_freq) - min_period
    ls_upp_err = np.fmax(1/tot_time, upp_err)
    ls_low_err = np.fmax(1/tot_time, low_err)

    print(max_period)

    print('period =', 1/max_freq, "+", ls_upp_err, "-", ls_low_err)   



def autoCorr(time, flux):
    # Lag for this data is half the  number of days in K2 observations(40) multiplied by the amount of observations per day - 48 (30 min cadence)
    #lag = ((max(time) - min(time))/2) * 48

    flux = -1 + flux/np.median(flux)

    a = plt.acorr(flux, maxlags = 2000)

    # Split results of autocorrelation function into two values.
    lags = a[0]
    acf = a[1]
    # Only look at positive values.
    acf = acf[lags > 0]
    lags = lags[lags > 0]

    # Change lags to time units.
    del_t = np.median(np.diff(time))
    lags = lags * del_t

    # Smooth acf curve. 
    kernel_size = 31
    smooth_acf = convolve(acf, Box1DKernel(kernel_size))

    # Find positive peak locations
    pks = scipy.signal.find_peaks(smooth_acf, distance = 30)
    potential_periods = lags[pks]
    
    potential_periods = potential_periods[acf[pks] > 0]
    period = potential_periods[potential_periods > kernel_size * del_t]
    period = period[0]

    # Noise level of acf plot.
    acf_noise = np.std(np.diff(acf))

    total_time = np.max(time) - np.min(time)
    find_uncertainty_corr(lags, acf, total_time, acf_noise, period)
    
    #lags = lags[:int(len(lags) * .35)]
    #acf = acf[:int(len(acf) * .35)]

    plt.plot(lags,acf)
    plt.xlabel("Lags")
    plt.ylabel("Acf")
    plt.xlim(6, 12)
    plt.show()
    
def find_uncertainty_corr(lags, acf, total_time, acf_noise, real_peak):

    # Find peak index, which is the second peak, the one *after* the first values that are smoothing the curve. 
    peak_index = np.where(lags == real_peak)[0][0]
    max_lags = lags[peak_index]
    print("peak_index")
    print(peak_index)
   
    # 
    lags_low = .5 * max_lags
    lags_high = 2 * max_lags
    lags_step = (lags_high - lags_low)/100
    new_lags = np.arange(lags_low, lags_high, lags_step) 

    # 
    pchip_obj = scipy.interpolate.PchipInterpolator(lags, acf)
    new_acf = pchip_obj(new_lags)
    
    # 
    new_peak = np.where(new_acf < np.max(new_acf))[0][0]
    print("new_peak")
    print(new_peak)
    
    # 
    upper_acf = new_acf[new_peak:]
    lower_acf = new_acf[new_peak: 1]
    # print("lower_acf")
    # print(lower_acf)

    #  
    f_max = new_peak + np.argmax(upper_acf < acf[peak_index] - acf_noise)
    f_min = new_peak + np.where(lower_acf < acf[peak_index] - acf_noise)
    print("ACF[peak_index]")
    print(acf[peak_index])
    print(f_min)

    min_period = 1/new_lags[f_max]
    max_period = 1/new_lags[f_min]
    upp_err = max_period - 1/max_lags
    low_err = (1/max_lags) - min_period
    ls_upp_err = np.fmax(1/total_time, upp_err)
    ls_low_err = np.fmax(1/total_time, low_err)

    print(1/max_lags)

    print('period =', 1/max_lags, "+", ls_upp_err, "-", ls_low_err)   
    

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

# def dft(time, flux):

    #     time = np.arange(0,100,0.1)
    #     flux = np.sin(2*time)

    #     delf = 1/(max(time)-min(time))
    #     fout = np.arange(0,500*delf,delf)
    #     XX = udft(time,flux,fout)

    #     delf = 1/(max(time)-min(time))
    #     fout = np.arange(0,500*delf,0.1*delf)
    #     XX = udft(time,flux,fout)
    #     amp = (2/len(time))*abs(XX)

    #     max_freq = fout[np.argmax(amp[fout<1])]
    #     print(max_freq)
    #     print(1/max_freq)

    #     plt.plot(fout,amp)
    #     plt.xlim(0,0.5)
    #     plt.ylim(0,0.003)
    #     plt.show()
   


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



