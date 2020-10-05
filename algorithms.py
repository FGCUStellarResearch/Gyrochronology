import numpy as np
import astropy as ap
import File_Management
import output
from astropy.timeseries import LombScargle
import matplotlib.pyplot as plt
import pandas as pd
import scaleogram as scg
import pywt
from scipy import signal
from scipy import stats
from scipy import fftpack
import scipy.interpolate
import scipy.cluster
from scipy.signal import find_peaks
from astropy.convolution import convolve, Box1DKernel

# Period finder, soon to utilize four different algorithms find periods in a data set.
def calcPeriods(time, detrended_flux):
    output.plot_graph(time, detrended_flux)
    plotLombScargle(time, detrended_flux)
    autoCorr(time, detrended_flux)
    #wavelets(time,detrended_flux)

# Plotting the Lomb-Scargle Algorithm.
def plotLombScargle(time, flux):
    tot_time = np.max(time) - np.min(time)
    # Plotting the period with the Lomb-Scargle method. 
    frequency,power = LombScargle(time, signal.detrend(flux)).autopower()
    # Estimate of noise based on the std of power values.
    noise = np.std(np.diff(power))

    # Truncate arrays to only view the first peak of the periodogram.
    frequency = frequency[:int(len(frequency) * .0025)]
    power = power[:int(len(power) * .0025)]
    period = np.max(power)

    # Values used when creating interpolated values in uncertainty function. 
    interp_coeff = [0.5, 2]
    peak_index = np.where(power == period)[0][0]

    
    # Finds lower and upper uncertainties. Values are saved and placed on the plot.
    plt_text = find_uncertainty(frequency, power, tot_time, noise, peak_index, interp_coeff)

    # Temporary box coordinates, will have to be changed***
    output.plot_graph(frequency, power, "Frequency - Cycles/Day", "Power", "Lomb-Scargle Periods", plt_text, .2, max(power))
    
# Function for finding uncertainty in either Lomb-Scargle or Autocorrelation functions.
def find_uncertainty(frequency, power, tot_time, noise, period_idx, coeffs):

    
    # Finding the index with the most frequent period.
    max_freq = frequency[period_idx]
    # Create new frequency list with interpolated power values to find the first value more than one noise level below.
    freq_low = coeffs[0] * max_freq
    freq_high = coeffs[1] * max_freq
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
    f_max = new_peak + np.argmax(upper_pow < power[period_idx] - noise)
    f_min = np.max(np.where(lower_pow < power[period_idx]-noise))

    min_period = 1/new_freq[f_max]
    max_period = 1/new_freq[f_min]
    upp_err = max_period - 1/max_freq
    low_err = (1/max_freq) - min_period
    ls_upp_err = np.fmax(1/tot_time, upp_err)
    ls_low_err = np.fmax(1/tot_time, low_err)

    # Use max to differentiate between autocorrelation lag value, or lombscargle freqency value.
    plt_text = 'Period = {:.5f}\nUncertainty\n+ {:.5f}\n- {:.5f}'.format(max(1/max_freq, max_freq), ls_upp_err, ls_low_err)
    return plt_text

# Running autocorrelation on data set.
def autoCorr(time, flux):
    # Lag for this data is half the  number of days in K2 observations(40) multiplied by the amount of observations per day - 48 (30 min cadence)
    #lag = ((max(time) - min(time))/2) * 48
    
    flux = -1 + flux/np.median(flux)

    a = plt.acorr(flux, maxlags = 2000, usevlines = False)

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

    kernel_size = 31
    smooth_acf = convolve(acf, Box1DKernel(kernel_size))

    # Find peaks that are in the positive range.
    pks, _ = scipy.signal.find_peaks(smooth_acf, distance = 30)
    
    plt.plot(lags, acf)
    plt.show()
    potential_periods = lags[pks]
    print(potential_periods)
    # The first peak (after the smoothing window) will be our period for this data. 
    potential_periods = potential_periods[acf[pks] > 0]
    period = potential_periods[potential_periods > kernel_size * del_t]
    print(period)
    period = period[0]
    # Noise level of acf plot.
    acf_noise = np.std(np.diff(acf))


    total_time = np.max(time) - np.min(time)
    # Values used when creating interpolated values in uncertainty function. 
    interp_coeff = [0.65, 1.30]
    peak_index = np.argwhere(lags == period)[0][0]
    print(peak_index)
    plt_text = find_uncertainty(lags , acf, total_time, acf_noise, peak_index, interp_coeff)

    plt.plot(lags,acf)
    plt.xlim(0, 50)
    plt.ylim(0,1)

    # Temporary box coordinates, will have to be changed***
    output.plot_graph(lags, acf, "Lags", "ACF", "AutoCorrelation", plt_text, 11, .822)
 
def wavelets(time, flux):
    flux = flux/np.median(flux)-1
    flux = flux/np.std(np.diff(flux))
    
    # Convert time to np array for scaleogram.
    time = np.asarray(time)
    print(len(time))
    # Spacing in time values for computing transform
    dt = time[1] -time[0]
    scales = scg.periods2scales(np.arange(1, len(time)))
    scg.set_default_wavelet('cmor2-2.0')
    wavelet = scg.get_default_wavelet

    #ax2 = scg.cws(time, flux, scales=scales, coikw={'alpha':0.5, 'hatch':'/' })
    #plt.show()
    
    # Same code in scaleogram package, used to visualize 1-D version of the data. 
    coeff, scales_freq = scg.fastcwt(flux, scales, 'cmor2-2.0', dt)

    # Sum all of the x values pertaining to each period value.
    period_sum = []
    for idx, arr in enumerate(coeff):
        period_sum.append(np.sum(np.abs(arr)))
    
    # Period values from the fastcwt function.
    transformed_time = 1./scales_freq

    output.plot_graph(transformed_time, period_sum, "Period", "Sum per Period", "Wavelet Transformation - 1-D")
