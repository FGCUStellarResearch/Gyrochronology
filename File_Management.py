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
from tkinter import filedialog
from tkinter import *

# Global for determining correct input when user inputs the file path.
file_found = False


#Pass in file from chosen directory.
def read_input_file(data_file):
    """Determine file type and process data accordingly.

    Args:
        data_file (String): Path of file.
    """    
    while True:
        #file_path = input("Choose file for period analysis: ")
        csv = data_file.endswith(".csv")
        fits = data_file.endswith(".fits")
        if csv:
            read_csv(data_file)
        elif fits:
            read_fits(data_file)
        if file_found:
            print("File found, analyzing data...")
            break
        print(f"No file found in path: \"{data_file}\". Please check your file path and try again.")
        break

def read_fits(file_path):
    """Open fits file and grab all of the data columns. 
       Determine if TESS or K2 data.

    Args:
        file_path (String): Path of file.
    """    
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

def read_csv(file_path):
    """Process csv data, using comma delimiter.

    Args:
        file_path (String): Path of data file.
    """    
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

def open_dir():
    """Used when analyzing multiple different files.
       User chooses directory and then fits files are selected.

    Returns:
        List: List of Fits files found in chosen directory.
    """    
    root = Tk()
    root.filename = filedialog.askdirectory()
    
    if root.filename is None or root.filename == "":
        return
    
    files = []
    for entry in os.listdir(root.filename):
        path = root.filename + "/" + entry
        files.append(path)
    root.destroy()
    return files
  

