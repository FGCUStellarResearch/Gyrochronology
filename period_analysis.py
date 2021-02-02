import File_Management
import data_process
import algorithms as alg
import numpy as np
import sys

while(True):
        menu_selec = input("Select file option: \n1 - Single file \n2 - Multiple Files \n0 - Exit Program\n\n")

        if(menu_selec == "1"):
            file_path = input("Choose file for period analysis: ")
            File_Management.read_one_file(file_path)

           
            time, detrended_flux, background = data_process.get_data()
          # Change values in columns to float values for later processing.
            time = [float(data) for data in time]
            detrended_flux = [float(data) for data in detrended_flux]
            noise = [float(data) for data in background]


            alg.calcPeriods(np.asarray(time), np.asarray(detrended_flux))

        elif(menu_selec == "2"):
           File_Management.open_dir()
              
           time, detrended_flux, background = data_process.get_data()
          # Change values in columns to float values for later processing.
           time = [float(data) for data in time]
           detrended_flux = [float(data) for data in detrended_flux]
           noise = [float(data) for data in background]


           alg.calcPeriods(np.asarray(time), np.asarray(detrended_flux))

        elif(menu_selec == "0"):
            sys.exit()
        else:
            print("This is not a valid selection.")


#File_Management.open_dir()

# time, detrended_flux, background = data_process.get_data()
# # Change values in columns to float values for later processing.
# time = [float(data) for data in time]
# detrended_flux = [float(data) for data in detrended_flux]
# noise = [float(data) for data in background]


# alg.calcPeriods(np.asarray(time), np.asarray(detrended_flux))