import csv
import re
from astropy.io import fits
import numpy as np
#Arrays to hold each column of data of the input file.
time = []
raw_flux = []
detrended_flux = []
background = []
x_pos = []
y_pos = []

# Global for determining correct input when user inputs the file path.
file_found = False


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



def read_csv(file_path):
    global file_found
    # Reading input file
    try:
        with open(file_path) as input_file:
            read_input = csv.reader(input_file, delimiter = ",")
            # Read each line and append data points to corresponding lists
            for line in read_input:
                time.append(line[0])
                raw_flux.append(line[1])
                detrended_flux.append(line[2])
                background.append(line[3])
                x_pos.append(line[4])
                y_pos.append(line[5])
            file_found = True
    except:
        file_found = False
        return

def read_fits(file_path):
    fits_file = fits.open(file_path)
    lightkurve = fits_file[1].data
    fits_file.close()

    data = np.asarray(lightkurve)

    for idx in range(len(data['TIME'])):
        if data['SAP_QUALITY'][idx] > 0:
            continue
        time.append(data['TIME'][idx])
        detrended_flux.append(data['PDCSAP_FLUX'][idx])
        background.append(data['SAP_BKG'][idx])

    global file_found
    file_found = True


# During testing, only three values are needed for period analysis algorithms.
def get_data():
    return (time, detrended_flux, background)