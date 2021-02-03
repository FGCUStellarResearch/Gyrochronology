import File_Management
import data_process
import algorithms as alg
import numpy as np
import sys

def pass_data():
    alg_choice = input("Select analysis method: \n1 - Time Series \n2 - Lomb-Scargle \n3 - Autocorrelation \n4 - Wavelets \n5 - All\n0 - Exit Program\n")
    time, detrended_flux, background = data_process.get_data()
    # Change values in columns to float values for later processing.
    time = [float(data) for data in time]
    detrended_flux = [float(data) for data in detrended_flux]
    noise = [float(data) for data in background]
    
    alg.selection(time, detrended_flux, alg_choice)


menu = True
while(menu):
        menu_selec = input("Select file option: \n1 - Single file \n2 - Multiple Files \n0 - Exit Program\n\n")

        if(menu_selec == "1"):
            file_path = input("Choose file for period analysis: ")
            File_Management.read_input_file(file_path)
            pass_data()
            menu = False

        elif(menu_selec == "2"):
           files = File_Management.open_dir()
           for path in files:
               File_Management.read_input_file(path)
               pass_data()
           menu = False

        elif(menu_selec == "0"):
            sys.exit()
        else:
            print("This is not a valid selection.")

