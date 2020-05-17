import numpy as np
import astropy as ap
import matplotlib.pyplot as plt
import csv
import pandas as pd


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

plt.plot(time, detrended_flux)
plt.show()