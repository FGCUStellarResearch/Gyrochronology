import csv

#Arrays to hold each column of data of the input file.
time = []
raw_flux = []
detrended_flux = []
background = []
x_pos = []
y_pos = []


def read_input_file():
    # For testing algorithms input file is: "example_K2_input.csv" 
    file_path = input("Choose file for period analysis: ")
    open_file(file_path)

def open_file(file_path):
    # Reading input file
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

# During testing, only three values are needed for period analysis algorithms.
def get_data():
    return (time, detrended_flux, background)