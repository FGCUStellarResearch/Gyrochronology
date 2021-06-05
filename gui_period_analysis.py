import data_process
import File_Management
import algorithms as alg
import tkinter as tk
from tkinter import filedialog, messagebox, Grid, ttk
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
win.geometry("380x200")
# Sets the initial text for the file selection ComboBox.
file_choice = tk.StringVar(win)
file_choice.set("Select")
# Sets the initial text for the algorithm selection ComboBox.
algorithm_choice = tk.StringVar(win)
algorithm_choice.set("Select")
# Creates an array to store the user's chosen files.
files = []
# Creates the font for the executeMe and chooseFiles buttons.
font = tkFont.Font(family="Lithos Pro", size=12)
# Creates the font for the files names. This can be changed if the text is deemed to be too small or too big.
font2 = tkFont.Font(family="Lithos Pro", size=6)


def file_picker():
    """This function stores the name/s of a file selected and stores it/them to the files[] array.
    """
    # Limits file types to .csv and fits. If we want to add excel or other compatibility, change this code.
    filename = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                          filetypes=[("Data Files", "*.csv"), ("Data Files", "*.fits")])
    files.clear()
    canvas.delete('all')
    files.append(filename)


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

    elif file_num == "Single File":
        file_picker()

        # Prevents program from crashing in the event that the user closes the file selection window.
        if files[0] == "" or files[0] is None:
            tk.messagebox.showinfo("Error", "Error: No Files Selected")
            return

        else:
            canvas.create_text(10, 125, text=files[0], font=font2, anchor='nw')

    if file_num == "Multiple Files":
        folder = File_Management.open_dir()

        # Prevents program from crashing in the event that the user closes the file selection window.
        if folder is None:
            tk.messagebox.showinfo("Error", "Error: No Folder Selected")
            return

        # Prevents program from crashing in the event that the user chooses a folder containing zero files.
        elif len(folder) == 0:
            tk.messagebox.showinfo("Error", "Error: Folder is Empty")
            return

        # Adds the paths to the selected files to the canvas, and stores them in files[].
        else:
            canvas.delete('all')
            label_height = 125
            for x in range(0, len(folder)):
                if not (folder[x].endswith('.csv') or folder[x].endswith('.fits')):
                    continue
                else:
                    files.append(folder[x])
                    canvas.create_text(10, label_height, text=folder[x], font=font2, anchor='nw')
                    label_height += 15


def data_op(file_num=None, alg_choice=None):
    """ This function takes in a file/s and an algorithm, and passes the given file data to the chosen algorithm.
    Note: each of these parameters are optional in the event that the user does not select a choice from either of their
    respective ComboBoxes, however if either is left as None this function will exit itself.
    Args:
        file_num (String): the amount of files chosen by the user. Either single or multiple files, or a test sinusoid.
        alg_choice (String): the user's chosen algorithm.
    """

    # Maps the algorithm choices to numbers for compatibility with algorithms.py
    alg_dict = {'Time Series': '1', 'Lomb-Scargle': '2', 'Autocorrelation': '3', 'Wavelets': '4', 'GPS': '5',
                'All': '6'}

    # Prevents program from crashing in the event that the user doesn't select properly.
    if file_num is None or file_num == "Select" or alg_choice is None or alg_choice == "Select":
        tk.messagebox.showinfo("Error", "Please select both a file/folder and an algorithm")

    elif file_num == "Single File":
        
        # Prevents program from crashing in the event that the user closes the file selection window.
        if not files:
            tk.messagebox.showinfo("Error", "Error: No Files Selected")
            return
        
        # Also prevents program from crashing in the event that the user closes the file selection window.
        elif files[0] == "" or files[0] is None:
            tk.messagebox.showinfo("Error", "Error: No Files Selected")
            return

        else:
            print(files[0])
            File_Management.read_input_file(files[0])

        time, detrended_flux, background = data_process.get_data()
        time = [float(data) for data in time]
        detrended_flux = [float(data) for data in detrended_flux]
        noise = [float(data) for data in background]

        alg_choice = alg_dict[alg_choice]

        alg.selection(time, detrended_flux, alg_choice)

    elif file_num == "Multiple Files":

        # Iterates through the files in the selected folder and passes each one through the chosen algorithm.
        # One potential issue with this is if the user intends to pass files through different algorithms.
        for path in files:
            # Prevents program from crashing in the event that the user chooses a folder containing bad file types.
            if not (path.endswith('.csv') or path.endswith('.fits')):
                continue

            File_Management.read_input_file(path)

            time, detrended_flux, background = data_process.get_data()
            time = [float(data) for data in time]
            detrended_flux = [float(data) for data in detrended_flux]
            noise = [float(data) for data in background]

            alg_new = alg_dict[alg_choice]
            alg.selection(time, detrended_flux, alg_new)

    # This option is not currently functional when used in sequence with a .csv file.
    elif file_num == "Test Sinusoid":
        data_process.create_sin()
        time, detrended_flux, background = data_process.get_data()
        time = [float(data) for data in time]
        detrended_flux = [float(data) for data in detrended_flux]
        noise = [float(data) for data in background]

        alg_choice = alg_dict[alg_choice]
        alg.selection(time, detrended_flux, alg_choice)


def exec_on_enter(event):
    """This function changes the color of the executeMe button when the user hovers over it.
    Args:
        event (tkinter.Event): automatically passed when the user's mouse enters the button's coordinates.
    """

    executeMe.config(background='black', foreground="white")


def exec_on_leave(event):
    """This function reverts the color of the executeMe button when the users stops hovering over it.
    Args:
        event (tkinter.Event): automatically passed when the user's mouse exits the button's coordinates.
    """
    executeMe.config(background='SystemButtonFace', foreground='black')


def choose_on_enter(event):
    """This function changes the color of the chooseFiles button when the user hovers over it.
    Args:
        event (tkinter.Event): automatically passed when the user's mouse enters the button's coordinates.
    """

    chooseFiles.config(background='black', foreground="white")


def choose_on_leave(event):
    """This function reverts the color of the chooseFiles button when the users stops hovering over it.
    Args:
        event (tkinter.Event): automatically passed when the user's mouse exits the button's coordinates.
    """
    chooseFiles.config(background='SystemButtonFace', foreground='black')


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
label1 = tk.Label(win, text="Welcome to the Gyrochronology GUI", justify='center')
label1.grid(row=0, column=1, sticky="")

dropDownFileLabel = tk.Label(win, text='Choose File or Folder: ')
dropDownFileLabel.grid(row=1, column=1, sticky='nw')

dropDownFiler = ttk.Combobox(win, textvariable=file_choice, state='readonly')
dropDownFiler['values'] = ('Single File', 'Multiple Files',
                           'Test Sinusoid')

# Prevents the selected option from staying highlighted
dropDownFiler.bind("<<ComboboxSelected>>", lambda f: win.focus())
dropDownFiler.grid(row=1, column=2, sticky='nw')

dropDownLabel = tk.Label(win, text='Choose Algorithm:')
dropDownLabel.grid(row=2, column=1, sticky='nw')

dropDown = ttk.Combobox(win, textvariable=algorithm_choice, state='readonly')
dropDown['values'] = ('Time Series', 'Lomb-Scargle', 'Autocorrelation', 'Wavelets', 'GPS', 'All')

# Prevents the selected option from staying highlighted
dropDown.bind("<<ComboboxSelected>>", lambda f: win.focus())
dropDown.grid(row=2, column=2, sticky='nw')

# Choose File/s
chooseFiles = tk.Button(win, font=font, text='Choose File/s', bd=1,
                        command=lambda: [file_selection(dropDownFiler.get())])

# Binds the on_enter and on_leave functions to the chooseFiles button
chooseFiles.bind('<Enter>', choose_on_enter)
chooseFiles.bind('<Leave>', choose_on_leave)
chooseFiles.grid(row=3, column=1, pady=5)

# Creates the executeMe button and executes the data_op function if it is clicked.
executeMe = tk.Button(win, font=font, text='Execute', bd=1, command=lambda: [data_op(dropDownFiler.get(),
                                                                                     dropDown.get())])
# Binds the on_enter and on_leave functions to the executeMe button
executeMe.bind('<Enter>', exec_on_enter)
executeMe.bind('<Leave>', exec_on_leave)
executeMe.grid(row=3, column=2, pady=5)

chosenFiles = tk.Label(win, text='Selected Files:')
chosenFiles.grid(row=4, column=1, sticky='nw')

win.mainloop()
