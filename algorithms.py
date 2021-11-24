import sys
import numpy as np
import astropy as ap
import data_process
import output
from astropy.timeseries import LombScargle
import matplotlib.pyplot as plt
import pandas as pd
import scaleogram as scg
import pywt
from wavelets import *
from scipy import signal
from scipy import stats
from scipy import fftpack
import scipy.interpolate
import scipy.cluster
from scipy.signal import find_peaks
from astropy.convolution import convolve, Box1DKernel

'''
Implementation of the period finding algorithms.

- Lomb-Scargle Periodogram
- Autocorrelation Function
- Morlet Wavelet
- Gradient of the Power Spectrum (using Paul Wavelet)

To-Do:
    - Verify uncertainty implementation and accuracy.
    - Fix windowing on output graphs. Properly show the peak, as well as uncertainty window.
    - Continue testing on different fits files.
'''
def selection(time, detrended_flux, algorithm, plot_count, total_plots):
    """Read menu selection, and call respective algorithm.

    Args:
        time (List): Time values taken from processed data file.
        detrended_flux (List): Flux values taken from processed data file.
        algorithm (String): Menu selection number for chosen algorithm.
    """
    if(algorithm == "1"):
        plotTimeSeries(time, detrended_flux, plot_count)
    elif(algorithm == "2"):
        plotLombScargle(time, detrended_flux, plot_count)
    elif(algorithm == "3"):
        plotAutoCorrelation(time, detrended_flux, plot_count)
    elif(algorithm == "4"):        
        plotWavelets(time, detrended_flux, plot_count)
    elif(algorithm == "5"):
        plotPaulWavelet(time, np.asarray(detrended_flux), plot_count)
    elif (algorithm == "6"):
        plotFasterWavelets(time, detrended_flux, plot_count)
    elif(algorithm == "0"):
        sys.exit()
    else:
        print("This is not a valid selection.")
    print(total_plots)
    if(plot_count == total_plots):
        plt.show()
    data_process.clear_data()


def plotTimeSeries(time, detrended_flux, plot_count):
    print(plot_count)
    plt.figure(plot_count)
    plt.plot(time, detrended_flux)
    plt.xlabel('Time (d)')
    plt.ylabel('Relative Amplitude (mag)')
    plt.title('Time Series')


def plotLombScargle(time, flux, plot_count):
    """Finding the period of the selected data with astropy's Lombscargle package.
    *** Interpolation coefficients and truncated arrays are hardcoded, may need to be altered. ***

    Args:
        time (List): Time values from processed data file.
        flux (List): Flux values from processed data file. 
    """    
    tot_time = np.max(time) - np.min(time)
    # Plotting the period with the Lomb-Scargle method. 
    frequency,power = LombScargle(time, flux).autopower()
    # Estimate of noise based on the std of power values.
    noise = np.std(np.diff(power))
    
    # Truncate arrays to only view the first peak of the periodogram.
    frequency = frequency[:int(len(frequency) * .25)]
    power = power[:int(len(power) * .25)]
    
    period = np.max(power)

    # Values used when creating interpolated values in uncertainty function. 
    interp_coeff = [0.5, 2]
    peak_index = np.where(power == period)[0][0]
    
    # Finds lower and upper uncertainties. Values are saved and placed on the plot.
    plt_text = find_uncertainty(frequency, power, tot_time, noise, peak_index, interp_coeff)

    # Temporary box coordinates, will have to be changed***
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.figure(plot_count)
    plt.plot(frequency, power)
    plt.xlabel("Frequency - Cycles/Day")
    plt.ylabel("Power")
    plt.title("Lomb-Scargle Periods")
    plt.text(.2, max(power), plt_text, verticalalignment='top', bbox=props)

    
def find_uncertainty(frequency, power, tot_time, noise, period_idx, coeffs):
    """Method to find uncertainty for the autocorrelation function and Lomb-Scargle Periodogram. 
    Starting from the peak, we move 1 noise level down to the left and right of the peak.
    How far the value moves along the x-axis after this noise "adjustment" corresponds to the uncertainty.

    Args:
        frequency (List): x-value of periodogram data. Lags in autocorrelation, Frequency in LS.
        power (List): y-value of periodogram data. ACF for autocorrelation, Power in LS.
        tot_time (Float): The total length of the data.
        noise (Float): Standard deviation of the difference between values along the y-axis.
        period_idx (Integer): Index of the peak period.
        coeffs (List): Values used to interpolate the periodogram data. Interpolation needed to
                       move along the peak.

    Returns:
        [String]: String containing the peak value, and the uncertainty window.
                  Used to display in plotted graph.
    """
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

    # Values that are less than one noise level below the peak.
    lower_vals = np.where(lower_pow < power[period_idx] - noise)
    upper_vals = new_peak + np.argmax(upper_pow < power[period_idx] - noise)

    # Check to see if either arrays are empty. If they are, replace with the maximum frequency value.
    if(lower_vals[0].size == 0):
        f_min = int(np.max(new_freq))
    else:
        f_min =  np.max(lower_vals)
    if(upper_vals.size == 0):
        f_max = int(np.max(new_freq))
    else:
        f_max = new_peak + np.argmax(upper_pow < power[period_idx] - noise)


    min_period = 1/new_freq[f_max]
    max_period = 1/new_freq[f_min]
    upp_err = max_period - 1/max_freq
    low_err = (1/max_freq) - min_period
    ls_upp_err = np.fmax(1/tot_time, upp_err)
    ls_low_err = np.fmax(1/tot_time, low_err)

    # Use max to differentiate between autocorrelation lag value, or lombscargle freqency value.
    plt_text = 'Period = {:.5f}\nUncertainty\n+ {:.5f}\n- {:.5f}'.format(max(1/max_freq, max_freq), ls_upp_err, ls_low_err)
    return plt_text


def find_wavelet_uncertainty(frequency, power, tot_time, noise, period_idx, coeffs):
    """Performs same function as above however this fixes an issue with the second to last line
    that would find and report the incorrect maximum value.

    Args:
        frequency (List): x-value of periodogram data.
        power (List): y-value of periodogram data.
        tot_time (Float): The total length of the data.
        noise (Float): Standard deviation of the difference between values along the y-axis.
        period_idx (Integer): Index of the peak period.
        coeffs (List): Values used to interpolate the periodogram data. Interpolation needed to
                       move along the peak.

    Returns:
        [String]: String containing the peak value, and the uncertainty window.
                  Used to display in plotted graph.
    """

    # Finding the index with the most frequent period.
    max_freq = frequency[period_idx]
    # Create new frequency list with interpolated power values to find the first value more than one noise level below.
    freq_low = coeffs[0] * max_freq
    freq_high = coeffs[1] * max_freq
    freq_step = (freq_high - freq_low) / 100
    new_freq = np.arange(freq_low, freq_high, freq_step)

    # Create object to interpolate power values from created frequency values.
    pchip_obj = scipy.interpolate.PchipInterpolator(frequency, power)
    new_power = pchip_obj(new_freq)

    # Index of the maximum power value inside new_power
    new_peak = np.where(new_power == np.max(new_power))[0][0]
    # Split frequencies into upper and lower ranges to identify higher and lower uncertainties.
    upper_pow = new_power[new_peak:]
    lower_pow = new_power[1:new_peak]

    # Values that are less than one noise level below the peak.
    lower_vals = np.where(lower_pow < power[period_idx] - noise)
    upper_vals = new_peak + np.argmax(upper_pow < power[period_idx] - noise)

    # Check to see if either arrays are empty. If they are, replace with the maximum frequency value.
    if (lower_vals[0].size == 0):
        f_min = int(np.max(new_freq))
    else:
        f_min = np.max(lower_vals)
    if (upper_vals.size == 0):
        f_max = int(np.max(new_freq))
    else:
        f_max = new_peak + np.argmax(upper_pow < power[period_idx] - noise)

    min_period = 1 / new_freq[f_max]
    max_period = 1 / new_freq[f_min]
    upp_err = max_period - 1 / max_freq
    low_err = (1 / max_freq) - min_period
    ls_upp_err = np.fmax(1 / tot_time, upp_err)
    ls_low_err = np.fmax(1 / tot_time, low_err)
    # Use max to differentiate between autocorrelation lag value, or lombscargle freqency value.
    plt_text = 'Period = {:.5f}\nUncertainty\n+ {:.5f}\n- {:.5f}'.format(max_freq, ls_upp_err,
                                                                         ls_low_err)
    return plt_text


def find_gps_uncertainty(frequency, power, tot_time, noise, max_freq, coeffs):
    """Method to find uncertainty for the autocorrelation function and Lomb-Scargle Periodogram.
    Starting from the peak, we move 1 noise level down to the left and right of the peak.
    How far the value moves along the x-axis after this noise "adjustment" corresponds to the uncertainty.

    Args:
        frequency (List): x-value of periodogram data. Lags in autocorrelation, Frequency in LS.
        power (List): y-value of periodogram data. ACF for autocorrelation, Power in LS.
        tot_time (Float): The total length of the data.
        noise (Float): Standard deviation of the difference between values along the y-axis.
        max_freq (Float): Rotational period found by the GPS() function.
        coeffs (List): Values used to interpolate the periodogram data. Interpolation needed to
                       move along the peak.

    Returns:
        [String]: String containing the peak value, and the uncertainty window.
                  Used to display in plotted graph.
    """

    # Create new frequency list with interpolated power values to find the first value more than one noise level below.
    freq_low = coeffs[0] * max_freq
    freq_high = coeffs[1] * max_freq
    freq_step = (freq_high - freq_low) / 100
    new_freq = np.arange(freq_low, freq_high, freq_step)

    # Create object to interpolate power values from created frequency values.
    pchip_obj = scipy.interpolate.PchipInterpolator(frequency, power)
    new_power = pchip_obj(new_freq)

    # Index of the maximum power value inside new_power
    new_peak = np.where(new_power == np.max(new_power))[0][0]
    # Split frequencies into upper and lower ranges to identify higher and lower uncertainties.
    upper_pow = new_power[new_peak:]
    lower_pow = new_power[1:new_peak]

    # Values that are less than one noise level below the peak.
    lower_vals = np.where(lower_pow < max_freq - noise)
    upper_vals = new_peak + np.argmax(upper_pow < max_freq - noise)

    # Check to see if either arrays are empty. If they are, replace with the maximum frequency value.
    if (lower_vals[0].size == 0):
        f_min = int(np.max(new_freq))
    else:
        f_min = np.max(lower_vals)
    if (upper_vals.size == 0):
        f_max = int(np.max(new_freq))
    else:
        f_max = new_peak + np.argmax(upper_pow < max_freq - noise)

    min_period = 1 / new_freq[f_max]
    max_period = 1 / new_freq[f_min]
    upp_err = max_period - 1 / max_freq
    low_err = (1 / max_freq) - min_period
    ls_upp_err = np.fmax(1 / tot_time, upp_err)
    ls_low_err = np.fmax(1 / tot_time, low_err)
    # Use max to differentiate between autocorrelation lag value, or lombscargle freqency value.
    plt_text = 'Period = {:.5f}\nUncertainty\n+ {:.5f}\n- {:.5f}'.format(max_freq, ls_upp_err,
                                                                         ls_low_err)
    return plt_text


def plotAutoCorrelation(time, flux, plot_count):
    """Using autocorrelation function from MatPlotLib to find period.

    Args:
        time (List): Time values from processed data file.
        flux (List): Flux values from processed data file.
    """    
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
    # Smooth acf curve. 
    kernel_size = np.floor(0.5/np.mean(np.diff(time)))
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
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.figure(plot_count)
    plt.plot(lags, acf)
    plt.xlabel("Lags")
    plt.ylabel("ACF")
    plt.title("AutoCorrelation")
    plt.text(max_x * .90, max_per * 1.1, plt_text, verticalalignment='top', bbox=props)
    

def plotWavelets(time, flux, plot_count):
    """Using morlet wavelet from scaleogram package to determine period. 
        Values are plotted on a 2-D contour map, and then transformed into
        a 1-D plot.

    Args:
        time (List): Time values from processed data file.
        flux (List): Flux values from processed data file.
    """    
    flux = flux/np.median(flux)-1
    flux = flux/np.std(np.diff(flux))
    
    # Convert time to np array for scaleogram.
    time = np.asarray(time)
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

    plt.figure(plot_count)
    plt.plot(transformed_time, period_sum)
    plt.xlabel("Period")
    plt.ylabel("Sum per Period")
    plt.title("Wavelet Transformation - 1-D")

def plotPaulWavelet(time, flux, plot_count):
    """Using Aaron O'Leary's wavelet package to compute the paul wavelet.
       Paul wavelet is used in computing the Gradient of the Power Spectrum.

    Args:
        time (List): Time values from processed data file.
        flux (List): Flux values from processed data file.
    """    
    dt = time[1] - time[0]
    # Package implementation
    wa = WaveletAnalysis(data = flux, time = time, wavelet=Paul(), dt=dt)
    power = wa.wavelet_power
    scales = wa.scales
    periods = wa.fourier_periods
    frequencies = wa.fourier_frequencies

    t = wa.time
    
    plotGPS(time, frequencies, periods,  np.sum(power, axis=1))
    #Attempting to plot period values on a 1-D grid.
    plt.plot(scales , np.sum(power, axis=1))
    plt.show()

    # Plotting wavelet results on 2D map.
    fig, ax = plt.subplots()
    T, S = np.meshgrid(t, scales)

    ax.contourf(T, S, power, 100)
    ax.set_yscale('log')
    plt.show()

def plotGPS(time, frequency, period, power_sum, plot_count):
    """ Using the Paul wavelet to find the Gradient of the Power Spectrum.
        Current problem: given our calculation of period using the alpha value, 
        the period we find is not the peak of the graph. The period is printed to
        the console, but the period shown on the graph is incorrect.
       
    Args:
        time (List): Time values from processed data file.
        frequency (List): Frequency values found from the Paul wavelet function.
        period (List): Periods found in the Paul wavelet function.
        power_sum (List): Sum of power values.
    """    
    # scale_factor = 0.19
    scale_factor_low = 0.14
    scale_factor_hi = 0.22

    tot_time = np.max(time) - np.min(time)
    
    # Temporary lists to hold log-adjusted scale.
    temp2 = []
    temp3 = []

    for i in range(1, len(period)):
        temp2.append(np.log(power_sum[i]) - np.log(power_sum[i-1])) 
        temp3.append(np.log(frequency[i]) - np.log(frequency[i-1]))
    
    gps_vals = 1-np.divide(temp2, temp3)
    
    # Set scale factor (AKA alpha value)
    scale_factor = np.polyval([-0.0017, 0.0258, -0.1362, 0.4218], period[np.argmax(gps_vals)])
    
    # Sets a minimum value for scale_factor of 0.14
    if scale_factor < 0.17:
        scale_factor = 0.17

    print("PGPS: " + str(period[np.argmax(gps_vals)]))
    print("Scale Factor: " + str(scale_factor))
    print("Rotational Period: " + str(period[np.argmax(gps_vals)] / scale_factor))
    
    period_vals = np.divide(period[1:], scale_factor)
    plt.plot(period_vals,gps_vals)
    
    box = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    # plt.text(5, 5, "Rotational Period: " + str(period[np.argmax(gps_vals)] / scale_factor), bbox=box)

    noise=np.std(np.diff(gps_vals))
    interp_coeff = [0.5,2]
    
    # Add peak and uncertainty onto the plot.
    plt_text = find_gps_uncertainty(period_vals, gps_vals, tot_time, noise, np.argmax(gps_vals), interp_coeff)
    plt.text(10, 2, plt_text, bbox=box)
    
    plt.show()

    # tot_len_ts = np.max(time) - np.min(time)
    # aa = np.max(gps_vals[period_vals<0.5*tot_len_ts])
    # print(aa)
    
    
def plotFasterWavelets(time, flux, plot_count):
    """Using Aaron O'Leary's wavelet package to compute the Morlet wavelet.

    Args:
        time (List): Time values from processed data file.
        flux (List): Flux values from processed data file.
    """
    flux = flux / np.median(flux) - 1
    flux = flux / np.std(np.diff(flux))

    tot_time = np.max(time) - np.min(time)

    # Convert time to np array for scaleogram.
    time = np.asarray(time)

    dt = time[1] - time[0]
    # Package implementation
    wa = WaveletAnalysis(data=flux, time=time, wavelet=Morlet(), dt=dt)
    power = wa.wavelet_power
    scales = wa.scales
    periods = wa.fourier_periods
    frequencies = wa.fourier_frequencies

    t = wa.time

    plt.figure(plot_count)
    plt.plot(scales, np.sum(power, axis=1))
    box = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    # idx = unif2D(power.astype(float), size=7, mode='constant').argmax()

    holder = 0
    holder_sum = 0
    power_sum = []
    
    ''' Collapse power values into a single value
        Possibly worth taking the mean instead of the sum.
    '''
    for i in range(0, len(scales)):
        power_sum.append(power[i].sum())
        if power[i].sum() > holder_sum:
            holder_sum = power[i].sum()
            holder = i

    # plt.text(5, 5, "Rotational Period: " + str(scales[holder]), bbox=box)
    noise = np.std(np.diff(power_sum))
    
    # This coefficient can be tweaked. I'm not really certain what it does. - Jake
    interp_coeff = [0.5, 2]
    # power = power.flatten()

    # Finds lower and upper uncertainties. Values are saved and placed on the plot.
    plt_text = find_uncertainty(scales, power_sum, tot_time, noise, holder, interp_coeff)
    plt.text(5,5,plt_text, bbox=box)
    plt.show()

    # Plotting wavelet results on 2D map.
    fig, ax = plt.subplots()
    T, S = np.meshgrid(t, scales)

    ax.contourf(T, S, power, 100)
    # ax.set_yscale('log')
    plt.xlabel('Time')
    plt.ylabel('Frequency')
    plt.title('Faster Wavelets')
    plt.show()
    
