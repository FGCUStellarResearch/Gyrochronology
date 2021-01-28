import csv
import glob
import re
import os
import pathlib
import pandas as pd
from astropy.io import fits
import numpy as np
from scipy import signal
import scipy.interpolate
import data_process

# Global for determining correct input when user inputs the file path.
file_found = False


'''
def read_input_file():
    # For testing algorithms input csv is: "example_K2_input.csv" and fits: "ktwo212708252-c17_slc.fits"
    while True:
        file_path = input("Choose file for period analysis: ")
        csv = file_path.endswith(".csv")
        fits = file_path.endswith(".fits")
        if csv:
            read_csv(file_path)
        elif fits:
            read_fits(file_path)
        if file_found:
            print("File found, analyzing data...")
            break
        print(f"No file found in path: \"{file_path}\". Please check your file path and try again.")

'''

def read_csv(file_path):
    global file_found
    # Reading input file
    try:
        with open(file_path) as input_file:
            read_input = csv.reader(input_file, delimiter = ",")
            # Read each line and append data points to corresponding lists
            data_process.read_csv_data(read_input)
           
            file_found = True
    except:
        file_found = False
        return

def read_fits(file_path):
    # Use global values for lists.
    global file_found

    fits_file = fits.open(file_path)
    lightkurve = fits_file[1].data
    fits_file.close()

    data = np.asarray(lightkurve)
    
    # First column is generally time, flux the 8th column, and quality the 10th.
    data_process.read_fits_data(data)
    
    # Remove nan values extracted from fits file.
    if("tess" in file_path):
        data_process.clean_tess()
    elif("ktwo" or "k2" in file_path):
        data_process.clean_k2()

    file_found = True

'''
def multipleFiles():

    directory = 'C:\\Users\\doryc\\Documents\\Gyrochronology\\Fits File'

    for filename in os.listdir(directory):
        
        if filename.endswith(".fits"):
            file_path = os.path.join(directory,filename)
            read_fits(file_path)

''' 
  

