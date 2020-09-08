import csv

#Arrays to hold each column of data of the input file.
time = []
raw_flux = []
detrended_flux = []
background = []
x_pos = []
y_pos = []

# Global for determining correct input when user inputs the file path.
file_found = True


def read_input_file():
    # For testing algorithms input file is: "example_K2_input.csv"
    while True:
        file_path = input("Choose file for period analysis: ")
        open_file(file_path)
        if file_found:
            print("File found, analyzing data...")
            break


def open_file(file_path):
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
        print(f"No file found in path: \"{file_path}\". Please check your file path and try again.")
        file_found = False
        return

# During testing, only three values are needed for period analysis algorithms.
def get_data():
    return (time, detrended_flux, background)