import sys
import numpy as np
import astropy as ap
import File_Management
import data_process
import output
from astropy.timeseries import LombScargle
import matplotlib.pyplot as plt
import pandas as pd
import scaleogram as scg
import pywt
from wavelets import WaveletAnalysis
from wavelets import Paul
from scipy import signal
from scipy import stats
from scipy import fftpack
import scipy.interpolate
import scipy.cluster
from scipy.signal import find_peaks
from astropy.convolution import convolve, Box1DKernel


def selection(time, detrended_flux, algorithm):

    #algorithm = input("Select analysis method: \n1 - Time Series \n2 - Lomb-Scargle \n3 - Autocorrelation \n4 - Wavelets \n5 - All\n0 - Exit Program\n")
    if(algorithm == "1"):
        output.plot_graph(time, detrended_flux)
    elif(algorithm == "2"):
        plotLombScargle(time, detrended_flux)
    elif(algorithm == "3"):
        autoCorr(time, detrended_flux)
    elif(algorithm == "4"):        
        wavelets(time, detrended_flux)
    elif(algorithm == "5"):
        output.plot_graph(time, detrended_flux)
        plotLombScargle(time, detrended_flux)
        autoCorr(time, detrended_flux)
        wavelets(time, detrended_flux)
    elif(algorithm == "0"):
        sys.exit()
    else:
        print("This is not a valid selection.")
    data_process.clear_data()


def calcPeriods(time, detrended_flux):
    selection(time, detrended_flux)
    paul_wav(time, detrended_flux)
    
  
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
    period = np.max(power)

    # Values used when creating interpolated values in uncertainty function. 
    interp_coeff = [0.5, 2]
    peak_index = np.where(power == period)[0][0]
    print(period)
    
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
    
    num_lags = np.floor(len(time)/2)
    flux = -1 + flux/np.median(flux)

    a = plt.acorr(flux, maxlags=int(num_lags), usevlines = False)

    # Split results of autocorrelation function into two values.
    lags = a[0]
    acf = a[1]
    # Only look at positive values.
    acf = acf[lags > 0]
    lags = lags[lags > 0]
    
    # Change lags to time units.
    del_t = np.median(np.diff(time))
    lags = lags * del_t
    print(del_t)
    # Smooth acf curve. 
    kernel_size = np.floor(0.5/np.mean(np.diff(time)))
    print(kernel_size)
    smooth_acf = convolve(acf, Box1DKernel(kernel_size))
    # Find peaks that are in the positive range.
    pks, _ = scipy.signal.find_peaks(smooth_acf, distance = kernel_size)
    
    potential_periods = lags[pks]
    # The first peak (after the smoothing window) will be our period for this data. 
    potential_periods = potential_periods[acf[pks] > 0]
    # Find potential periods after one day lag. 
    period = potential_periods[potential_periods > 1]

    # Get the indices of each potential period.
    # The np.where function returns array values, so indexing at 0, 0 is needed to get the actual indices.
    index = [np.where(lags == i)[0][0] for i in period]
    
    # Find the max period according to the smooth_acf values.
    max_per = np.max(smooth_acf[index])

    # Index of the max period
    period = np.where(smooth_acf == max_per)

    # Noise level of acf plot.
    acf_noise = np.std(np.diff(acf))


    total_time = np.max(time) - np.min(time)
    # Values used when creating interpolated values in uncertainty function. 
    interp_coeff = [0.65, 1.30]
    peak_index = period[0][0]

    # Call uncertainty function
    plt_text = find_uncertainty(lags , acf, total_time, acf_noise, peak_index, interp_coeff)

    # Hold max and min values for plot window
    max_x = np.max(lags)
    min_x = np.min(lags)
    max_y = np.max(acf)
    min_y = np.min(acf)

    plt.xlim(min_x * 1.25, max_x * 1.25)
    plt.ylim(min_y * 1.25, max_y * 1.25)
    
    # Temporary box coordinates, will have to be changed***
    output.plot_graph(lags, acf, "Lags", "ACF", "AutoCorrelation", plt_text, max_x * .90, max_per * 1.1)
 
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

    ax2 = scg.cws(time, flux, scales=scales, coikw={'alpha':0.5, 'hatch':'/' })
    plt.show()
    
    # Same code in scaleogram package, used to visualize 1-D version of the data. 
    coeff, scales_freq = scg.fastcwt(flux, scales, 'cmor2-2.0', dt)

    # Sum all of the x values pertaining to each period value.
    period_sum = []
    for idx, arr in enumerate(coeff):
        period_sum.append(np.sum(np.abs(arr)))
    
    # Period values from the fastcwt function.
    transformed_time = 1./scales_freq

    output.plot_graph(transformed_time, period_sum, "Period", "Sum per Period", "Wavelet Transformation - 1-D")

# Using Aaron O'Leary's wavelet package to compute the paul wavelet.
def paul_wav(time, flux):
    dt = time[1] - time[0]
    # Package implementation
    wa = WaveletAnalysis(data = flux, time = time, wavelet=Paul(), dt=dt)
    power = wa.wavelet_power
    scales = wa.scales
    periods = wa.fourier_periods
    frequencies = wa.fourier_frequencies

    t = wa.time
    
    GPS(time, frequencies, periods,  np.sum(power, axis=1))
    #Attempting to plot period values on a 1-D grid.
    plt.plot(scales , np.sum(power, axis=1))
    plt.show()

    # Plotting wavelet results on 2D map.
    fig, ax = plt.subplots()
    T, S = np.meshgrid(t, scales)

    ax.contourf(T, S, power, 100)
    ax.set_yscale('log')
    plt.show()

def GPS(time, frequency, period, power_sum):
    scale_factor = 0.19
    scale_factor_low = 0.14
    scale_factor_hi = 0.22

    print(len(power_sum))
    # Temporary lists to hold log-adjusted scale.
    temp2 = []
    temp3 = []

    for i in range(1, len(period)):
        temp2.append(np.log(power_sum[i]) - np.log(power_sum[i-1])) 
        temp3.append(np.log(frequency[i]) - np.log(frequency[i-1]))
    
    gps_vals = 1-np.divide(temp2, temp3)
    period_vals = np.divide(period[1:], scale_factor)
    plt.plot(period_vals,gps_vals)
    plt.show()

    tot_len_ts = np.max(time) - np.min(time)
    aa = np.max(gps_vals[period_vals<0.5*tot_len_ts])
    print(aa)
    