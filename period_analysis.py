import File_Management
import data_process
import algorithms as alg
import numpy as np
import sys

'''
Main driver file. Program begins here. File reading type and algorithm selection are done here.

*** Current implementation may be phased out with implementation of GUI. ***
'''

def pass_data(file_num, alg_choice = None):
    """ This function takes the data obtained from the selected menu choices above, and passes them to their respective algorithms.
    
    *** Should be phased out after implementing GUI. ***

    Args:
        file_num (String): The option chosen for number of files selected, either 1, multiple or a test sinusoid is selected. 
        alg_choice (String, optional): Used in the case of creating a test sinusoid. Algorithm is chosen prior to . Defaults to None.
    """    
    if file_num == "1":
        time, detrended_flux, background = data_process.get_data()
        # Change values in columns to float values for later processing.
        time = [float(data) for data in time]
        detrended_flux = [float(data) for data in detrended_flux]
        noise = [float(data) for data in background]
        
        while(True):
            alg_choice = input("Select analysis method: \n1 - Time Series \n2 - Lomb-Scargle \n3 - Autocorrelation \n4 - Morlet Wavelet \n5 - GPS\n6 - All\n0 - Exit Program\n")

            alg.selection(time, detrended_flux, alg_choice)
    else:
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
            pass_data(menu_selec)
            menu = False

        elif(menu_selec == "2"):
           files = File_Management.open_dir()
           alg_choice = input("Select analysis method: \n1 - Time Series \n2 - Lomb-Scargle \n3 - Autocorrelation \n4 - Wavelets \n5 - All\n0 - Exit Program\n")
           for path in files:
               File_Management.read_input_file(path)
               pass_data(menu_selec, alg_choice)
           
        elif(menu_selec == "3"):
            data_process.create_sin()
            alg_choice = input("Select analysis method: \n1 - Time Series \n2 - Lomb-Scargle \n3 - Autocorrelation \n4 - Wavelets \n5 - All\n0 - Exit Program\n")
            time, detrended_flux, background = data_process.get_data()

            alg.selection(time, detrended_flux, alg_choice)
            
        elif(menu_selec == "0"):
            sys.exit()
        else:
            print("This is not a valid selection.")

