import os
from tkinter.constants import ACTIVE, COMMAND, DISABLED

import data_process
import File_Management
import algorithms as alg
import tkinter as tk
from tkinter import filedialog, Grid, ttk
import tkinter.font as tkFont

'''
This code effectively replaces period_analysis.py with a GUI version of the same code with the same functionality.
To-Do List:

    1. Running the algorithms more than once produces a variety of errors. In some cases, the data from the last execution
    will be saved, and the next execution will duplicate the data. In other cases, the algorithm will not run at all a 
    time due to a variety of data type and input errors. I believe these problems could be solved by implementing a universal
    data wipe that runs after each execution. 
 
Note:
    To fix potential issues that the user could cause to crash the GUI, I made minor edits to my version of
    File_Management.py that are probably worth making to the repo version as well.
'''

# Creates the GUI
win = tk.Tk()
# **Changed window size to wrap current GUI elements.
win.geometry("380x300")
# Sets the initial text for the file selection ComboBox.
file_choice = tk.StringVar(win)
file_choice.set("Select")
# Creates an array to store the user's chosen files and algorithms.
files = []
algorithms = []
# Creates the font for the executeMe and chooseFiles buttons.
font = tkFont.Font(family="Lithos Pro", size=12)
# Creates the font for the files names. This can be changed if the text is deemed to be too small or too big.
font2 = tkFont.Font(family="Lithos Pro", size=6)


def files_picker():
    """This function stores the names of files selected and stores them to the files[] array.
    """
    # Limits file types to .csv and fits. If we want to add excel or other compatibility, change this code.
    global files
    filenames = filedialog.askopenfilenames(parent = win, title="Select a File", 
                                            filetypes=[("Data Files", "*.csv"), ("Data Files", "*.fits")])
    canvas.delete('all')
    chosenFiles.grid_remove()
    files.clear()
    files = list(filenames)


def file_selection(file_num):
    """ This function allows the user to choose a file, and stores the chosen file so that the user may pass the file
    data to multiple algorithms without continually selecting the file.
    Args:
         file_num (String): the file chosen by the user. Either single or multiple files, or a test sinusoid.
    """

    # Prevents program from crashing in the event that the user doesn't select properly.
    if file_num == "Select" or file_num is None:
        tk.messagebox.showinfo("Error", "Error: Please Choose a File Option")
        return

    elif file_num == "Browse For File(s)":
        files_picker()

        # Prevents program from crashing in the event that the user closes the file selection window.
        if not files:
            tk.messagebox.showinfo("Error", "Error: No Files Selected")
            return

        # Adds the paths to the selected files to the canvas, and stores them in files[].
        else:
            checkInput()
            canvas.delete('all')
            label_height = 130
            for file in files:
                if not (file.endswith('.csv') or file.endswith('.fits')):
                    continue
                else:
                    chosenFiles.grid()
                    canvas.create_text(10, label_height, text=os.path.relpath(file), font=font2, anchor='nw')
                    label_height += 15


def data_op(file_num=None, algorithms = []):
    """ This function takes in a file/s and an algorithm, and passes the given file data to the chosen algorithm.
    Note: each of these parameters are optional in the event that the user does not select a choice from either of their
    respective ComboBoxes, however if either is left as None this function will exit itself.
    Args:
        file_num (String): the amount of files chosen by the user. Either single or multiple files, or a test sinusoid.
        alg_choice (String): the user's chosen algorithm.
    """

    # Maps the algorithm choices to numbers for compatibility with algorithms.py
    alg_dict = {'Time Series': '1', 'Lomb-Scargle': '2', 'Autocorrelation': '3', 'Wavelets': '4', 'GPS': '5',
                'Faster Wavelets': '6'}

    # Prevents program from crashing in the event that the user doesn't select properly.
    if file_num is None or file_num == "Select" or len(algorithms) == 0:
        tk.messagebox.showinfo("Error", "Please select both a file/folder and an algorithm")

    elif file_num == "Browse For File(s)":

        # Iterates through the files in the selected folder and passes each one through the chosen algorithm.
        # One potential issue with this is if the user intends to pass files through different algorithms.
        for file in files:
            # Prevents program from crashing in the event that the user chooses a folder containing bad file types.
            if not (file.endswith('.csv') or file.endswith('.fits')):
                continue

            File_Management.read_input_file(file)

            time, detrended_flux, background = data_process.get_data()
            time = [float(data) for data in time]
            detrended_flux = [float(data) for data in detrended_flux]
            noise = [float(data) for data in background]

        for algorithm in algorithms:
            alg_choice = alg_dict[algorithm]
            alg.selection(time, detrended_flux, alg_choice)

    # This option is not currently functional when used in sequence with a .csv file.
    elif file_num == "Test Sinusoid":
        chooseFiles.config(state=DISABLED)
        data_process.create_sin()
        time, detrended_flux, background = data_process.get_data()
        time = [float(data) for data in time]
        detrended_flux = [float(data) for data in detrended_flux]
        noise = [float(data) for data in background]

        for algorithm in algorithms:
            alg_choice = alg_dict[algorithm]
            alg.selection(time, detrended_flux, alg_choice)


# checkbox listener for Select All checkbox
def saCheckState():
    # if select all checkbox is selected
    if saState.get() == 1:
        # check all remaining boxes and add algorithms to list
        tsState.set(1)
        algorithms.append('Time Series')
        lsState.set(1)
        algorithms.append('Lomb-Scargle')
        acState.set(1)
        algorithms.append('Autocorrelation')
        fwState.set(1)
        algorithms.append('Faster Wavelets')
        print(algorithms)

    # else if select all checkbox is not selected   
    else:
        # uncheck all remaining boxes and clear list
        tsState.set(0)
        lsState.set(0)
        acState.set(0)
        fwState.set(0)
        del algorithms[:]
        print(algorithms)
    checkInput()


# checkbox listener for Time Series algorithm
def tsCheckState():
    # if checkbox is enabled, add algorithm
    if tsState.get() == 1:
        # add to beginning of list
        algorithms.insert(0, 'Time Series')
    # if checkbox is disabled, remove algorithm
    else:
        # checks if algorithm is already present before removing it, to prevent program from crashing
        if 'Time Series' in algorithms:
            algorithms.remove('Time Series')
    checkInput()
    print(algorithms)


# checkbox listener for Lomb-Scargle algorithm
def lsCheckState():
    # if checkbox is enabled, add algorithm
    if lsState.get() == 1:
        algorithms.append('Lomb-Scargle')
    # if checkbox is disabled, remove algorithm
    else:
        # checks if algorithm is already present before removing it, to prevent program from crashing
        if 'Lomb-Scargle' in algorithms:
            algorithms.remove('Lomb-Scargle')
    checkInput()
    print(algorithms)


# checkbox listener for Autocorrelation algorithm
def acCheckState():
    # if checkbox is enabled, add algorithm
    if acState.get() == 1:
        algorithms.append('Autocorrelation')
    # if checkbox is disabled, remove algorithm
    else:
        # checks if algorithm is already present before removing it, to prevent program from crashing
        if 'Autocorrelation' in algorithms:
            algorithms.remove('Autocorrelation')
    checkInput()
    print(algorithms)


# checkbox listener for Wavelets algorithm
def wCheckState():
    # if checkbox is enabled, add algorithm
    if wState.get() == 1:
        algorithms.append('Wavelets')
    # if checkbox is disabled, remove algorithm
    else:
        # checks if algorithm is already present before removing it, to prevent program from crashing
        if 'Wavelets' in algorithms:
            algorithms.remove('Wavelets')
    checkInput()
    print(algorithms)


# checkbox listener for Wavelets algorithm
def gpsCheckState():
    # if checkbox is enabled, add algorithm
    if gpsState.get() == 1:
        algorithms.append('GPS')
    # if checkbox is disabled, remove algorithm
    else:
        # checks if algorithm is already present before removing it, to prevent program from crashing
        if 'GPS' in algorithms:
            algorithms.remove('GPS')
    checkInput()
    print(algorithms)


# checkbox listener for Faster Wavelets algorithm
def fwCheckState():
    # if checkbox is enabled, add algorithm
    if fwState.get() == 1:
        algorithms.append('Faster Wavelets')
    # if checkbox is disabled, remove algorithm
    else:
        # checks if algorithm is already present before removing it, to prevent program from crashing
        if 'Faster Wavelets' in algorithms:
            algorithms.remove('Faster Wavelets')
    checkInput()
    print(algorithms)

def checkInput():
    if dropDownFiler.get() == "Browse For File(s)":
        # Prevents user from clicking execute button if there are no files or algorithms selected
        if file_choice is None or file_choice.get() == "Select" or len(files) == 0 or len(algorithms) == 0:
            executeMe.config(state='disabled') 
        else:
            executeMe.config(state='normal')
    else:
        # Prevents user from clicking execute button if there are no files or algorithms selected
        if file_choice is None or file_choice.get() == "Select" or len(algorithms) == 0:
            executeMe.config(state='disabled') 
        else:
            executeMe.config(state='normal')

def exec_on_enter(event):
    """This function changes the color of the executeMe button when the user hovers over it.
    Args:
        event (tkinter.Event): automatically passed when the user's mouse enters the button's coordinates.
    """

    if dropDownFiler.get() == "Browse For File(s)":
        # Prevents user from clicking execute button if there are no files or algorithms selected
        if not(file_choice is None or file_choice.get() == "Select" or len(files) == 0 or len(algorithms) == 0):
            executeMe.config(background='black', foreground="white") 
    else:
        # Prevents user from clicking execute button if there are no files or algorithms selected
        if not(file_choice is None or file_choice.get() == "Select" or len(algorithms) == 0):
            executeMe.config(background='black', foreground="white") 


def exec_on_leave(event):
    """This function reverts the color of the executeMe button when the users stops hovering over it.
    Args:
        event (tkinter.Event): automatically passed when the user's mouse exits the button's coordinates.
    """
    executeMe.config(background='lightgray', foreground='black')


def choose_on_enter(event):
    """This function changes the color of the chooseFiles button when the user hovers over it.
    Args:
        event (tkinter.Event): automatically passed when the user's mouse enters the button's coordinates.
    """
    if dropDownFiler.get() == "Browse For File(s)":
        chooseFiles.config(background='black', foreground="white")
    

def choose_on_leave(event):
    """This function reverts the color of the chooseFiles button when the users stops hovering over it.
    Args:
        event (tkinter.Event): automatically passed when the user's mouse exits the button's coordinates.
    """
    chooseFiles.config(background='lightgray', foreground='black')

# Gives a title to the GUI window
win.title("Period Analysis")

# Creates a canvas on which to display the file paths.
canvas = tk.Canvas(win)
canvas.place(x=0, y=0)

# Assigns weights of 0 to all items in the grid so that they do not get stretched when the window changes size.
for x in range(5):
    Grid.columnconfigure(win, x, weight=0)

for y in range(5):
    Grid.rowconfigure(win, y, weight=0)

# This text should probably be changed, I was unsure of the proper name for this program.
label1 = tk.Label(win, text="Welcome to the Period Analysis GUI.", justify='center')
label1.grid(row=0, column=1, sticky="")

# Label for file selection dropdown
dropDownFileLabel = tk.Label(win, text='Data Source:')
dropDownFileLabel.grid(row=1, column=1, sticky='nw')

dropDownFiler = ttk.Combobox(win, textvariable=file_choice, state='readonly')
dropDownFiler['values'] = ('Browse For File(s)','Test Sinusoid')

dropDownFiler.bind("<<ComboboxSelected>>", lambda f: win.focus())
dropDownFiler.grid(row=2, column=1, sticky='nw')

# Label for checkboxes used in algorithm selection
checkBoxLabel = tk.Label(win, text='Algorithm:')
checkBoxLabel.grid(row=1, column=2, sticky='nw')

# Declare states for checkboxes
saState = tk.IntVar()
tsState = tk.IntVar()
lsState = tk.IntVar()
acState = tk.IntVar()
wState = tk.IntVar()
gpsState = tk.IntVar()
fwState = tk.IntVar()

# Checkboxes for selection of algorithm(s)
saCheckBox = tk.Checkbutton(win, text='Select All', variable=saState, onvalue=1, offvalue=0, command=saCheckState)
saCheckBox.grid(row=2, column=2, sticky='w')
tsCheckBox = tk.Checkbutton(win, text='Time Series', variable=tsState, onvalue=1, offvalue=0, command=tsCheckState)
tsCheckBox.grid(row=3, column=2, sticky='w')
lsCheckButton = tk.Checkbutton(win, text='Lomb-Scargle', variable=lsState, onvalue=1, offvalue=0, command=lsCheckState)
lsCheckButton.grid(row=4, column=2, sticky='w')
acCheckButton = tk.Checkbutton(win, text='Autocorrelation', variable=acState, onvalue=1, offvalue=0, command=acCheckState)
acCheckButton.grid(row=5, column=2, sticky='w')
fwCheckButton = tk.Checkbutton(win, text='Faster Wavelets', variable=fwState, onvalue=1, offvalue=0, command=fwCheckState)
fwCheckButton.grid(row=6, column=2, sticky='w')

# Choose File/s
chooseFiles = tk.Button(win, font=font, text='Choose File/s', bd=1, background='lightgray', foreground='black',
                        command=lambda: [file_selection(dropDownFiler.get())])

# Binds the on_enter and on_leave functions to the chooseFiles button
chooseFiles.bind('<Enter>', choose_on_enter)
chooseFiles.bind('<Leave>', choose_on_leave)
chooseFiles.grid(sticky='w', row=3, column=1, pady=5)
chooseFiles.config(state=DISABLED) 

# Creates the executeMe button and executes the data_op function if it is clicked.
executeMe = tk.Button(win, font=font, text='Execute', bd=1, background='lightgray', state='disabled', foreground='black', command=lambda: [data_op(dropDownFiler.get(),
                                                                                     algorithms)])
# Binds the on_enter and on_leave functions to the executeMe button
executeMe.bind('<Enter>', exec_on_enter)
executeMe.bind('<Leave>', exec_on_leave)
executeMe.grid(row=9, column=2, sticky="w")

chosenFiles = tk.Label(win, text='Selected Files:')
chosenFiles.grid(row=4, column=1, sticky='nw')
chosenFiles.grid_remove()

# event listener for file input type dropdown
def fileInputChanged(*args):
    files.clear()
    canvas.delete('all')

    chosenFiles.grid_remove()
    checkInput()
    
    # Prevents user from clicking browse files button when there is no 
    # file input type selected or a test file has been selected
    if dropDownFiler.get() == "Browse For File(s)":
        chooseFiles.config(state='normal')
    else:
        chooseFiles.config(state='disabled') 
    win.focus();

file_choice.trace("w", fileInputChanged)

win.mainloop()
