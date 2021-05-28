import data_process
import File_Management
import algorithms as alg
import tkinter as tk
from tkinter import filedialog, messagebox, Grid, ttk
import tkinter.font as tkFont
from PIL import Image, ImageTk

'''
This code effectively replaces period_analysis.py with a GUI version of the same code with the same functionality.

To-Do List:
    1. The test sinusoid functionality is problematic with this codeset. If the user passes the test sinusoid to any
    algorithm, and then tries to pass a .csv file to an algorithm, the program crashes. However, if the user passes the
    test sinusoid and then passes a .fits file, everything is fine, and the user may even pass a .csv file in after
    this. The issue seems to lie in data_process.read_csv_data when it is being called by File_Management.read_csv.
    That said, if the test sinusoid was only a tool to test code, then this issue is unnecessary to solve. The sinusoid
    also causes a datatype issue where it becomes an np.ndarray instead of a list, and therefore does not have access
    to .clear(), crashing the program in data_process.clear_data(). I made a small edit to my version of data_process
    to solve this.

    2. The GUI is a bit of an eyesore, so that could use some work. Additionally, I am not sure if a background image
    is what we want for the GUI, or if we want something else instead. If we go for an image, it would be smart to go
    for a non-copyrighted image. Note: If your code is not running because of an issue with the image, make sure you
    have the image downloaded, and make sure that you are using the correct path as needed throughout the code.
    
    3. Occasionally blank windows will open if the user runs the program more than once before closing it. I believe
    this is somehow triggered by an if/else statement but will need to look into it more.

Note:
    To fix potential issues that the user could cause to crash the GUI, I made minor edits to my version of
    File_Management.py that are probably worth making to the repo version as well. Also, we may want to add
    PIL as a dependency if we end up using a background image.
'''

# Creates the GUI
win = tk.Tk()
# Sets the GUI initial size to the natural pixel dimensions of the background image.
win.geometry("854x429")
# Sets the initial text for the file selection ComboBox.
file_choice = tk.StringVar(win)
file_choice.set("Select")
# Sets the initial text for the algorithm selection ComboBox.
algorithm_choice = tk.StringVar(win)
algorithm_choice.set("Select")
files = []
# Creates the font for the executeMe button
font = tkFont.Font(family="Lithos Pro", size=12)
# Stores the background image. This is possibly an unnecessary feature for the program and the image may be copyrighted.
photo = ImageTk.PhotoImage(file='1613768_night-sky-png-meteor-stars-night-sky-meteorday.png')


def file_picker():
    """This function stores the name/s of a file selected and stores it/them to the files[] array.
    """
    # Limits file types to .csv and fits. If we want to add excel or other compatibility, change this code.
    filename = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                          filetypes=[("Data Files", "*.csv"), ("Data Files", "*.fits")])
    files.clear()
    files.append(filename)


def data_op(file_num=None, alg_choice=None):
    """ This function takes in a file/s and an algorithm, and passes the given file data to the chosen algorithm.

    Note: each of these parameters are optional in the event that the user does not select a choice from either of their
    respective ComboBoxes, however if either is left as None this function will exit itself.

    Args:
        file_num (String): the file chosen by the user. Either single or multiple files, or a test sinusoid.
        alg_choice (String): the user's chosen algorithm.

    """

    # Maps the algorithm choices to numbers for compatibility with algorithms.py
    alg_dict = {'Time Series': '1', 'Lomb-Scargle': '2', 'Autocorrelation': '3', 'Wavelet': '4', 'GPS': '5', 'All': '6'}

    # Prevents program from crashing in the event that the user doesn't select properly.
    if file_num is None or file_num == "Select" or alg_choice is None or alg_choice == "Select":
        tk.messagebox.showinfo("Error", "Please select both a file/folder and an algorithm")

    elif file_num == "Single File":
        file_picker()

        # Prevents program from crashing in the event that the user closes the file selection window.
        if files[0] == "" or files[0] is None:
            tk.messagebox.showinfo("Error", "Error: No Files Selected")
            return

        else:
            File_Management.read_input_file(files[0])

        time, detrended_flux, background = data_process.get_data()
        time = [float(data) for data in time]
        detrended_flux = [float(data) for data in detrended_flux]
        noise = [float(data) for data in background]

        alg_choice = alg_dict[alg_choice]

        alg.selection(time, detrended_flux, alg_choice)

    elif file_num == "Multiple Files":
        folder = File_Management.open_dir()

        # Prevents program from crashing in the event that the user closes the file selection window.
        if folder is None:
            tk.messagebox.showinfo("Error", "Error: No Folder Selected")
            return

        # Prevents program from crashing in the event that the user chooses a folder containing zero files.
        elif len(folder) == 0:
            tk.messagebox.showinfo("Error", "Error: Folder is Empty")
            return

        # Iterates through the files in the selected folder and passes each one through the chosen algorithm.
        # One potential issue with this is if the user intends to pass files through different algorithms.
        for path in folder:
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
    # elif file_num == "Test Sinusoid":
    #     data_process.create_sin()
    #     time, detrended_flux, background = data_process.get_data()
    #     time = [float(data) for data in time]
    #     detrended_flux = [float(data) for data in detrended_flux]
    #     noise = [float(data) for data in background]
    #
    #     alg_choice = alg_dict[alg_choice]
    #     alg.selection(time, detrended_flux, alg_choice)


def on_enter(event):
    """This function changes the color of the executeMe button when the user hovers over it.
    Args:
        event (tkinter.Event): automatically passed when the user's mouse enters the button's coordinates.
    """

    executeMe.config(background='black', foreground="white")


def on_leave(event):
    """This function reverts the color of the executeMe button when the users stops hovering over it.
    Args:
        event (tkinter.Event): automatically passed when the user's mouse exits the button's coordinates.
    """
    executeMe.config(background='SystemButtonFace', foreground='black')


def resize_image(event):
    """This function resizes the background image when the window size changes.
    Args:
        event (tkinter.Event): automatically passed when the user's resizes the program window.
    """
    global image, resized_image, new_image
    image = Image.open('1613768_night-sky-png-meteor-stars-night-sky-meteorday.png')
    # "unresolved attribute reference" for .width & .height can be ignored. This only displays due to the pydoc comment.
    resized_image = image.resize((event.width, event.height), Image.ANTIALIAS)
    new_image = ImageTk.PhotoImage(resized_image)
    canvas.create_image(0, 0, image=new_image, anchor='nw')


win.title("Gyrochronology GUI")

# Assigns weights of 0 to all items in the grid so that they do not get stretched when the window changes size.
for x in range(10):
    Grid.columnconfigure(win, x, weight=0)

for y in range(10):
    Grid.rowconfigure(win, y, weight=0)

# Creates a canvas on which to display the background image and place other widgets.
canvas = tk.Canvas(win, width=win.winfo_screenwidth(), height=win.winfo_screenheight(), highlightthickness=0)
canvas.create_image(0, 0, image=photo, anchor='nw')
canvas.place(x=0, y=0)

# Fixes a bug in which a shrunken background image appears in the top left corner of the program window.
win.update()

# This text should probably be changed, I was unsure of the proper name for this program.
label1 = tk.Label(win, text="Welcome to the Gyrochronology GUI", justify='center')
label1.grid(row=0, column=1)
label1['bg'] = win['bg']

dropDownFileLabel = tk.Label(win, text='Choose File or Folder: ')
dropDownFileLabel.grid(row=1, column=1, sticky='nw')

dropDownFiler = ttk.Combobox(win, textvariable=file_choice, state='readonly')
dropDownFiler['values'] = ('Single File', 'Multiple Files',
                           # 'Test Sinusoid')
                           )

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

# Creates the executeMe button and executes the data_op function if it is clicked.
executeMe = tk.Button(win, font=font, text='Execute', bd=1, command=lambda: [data_op(dropDownFiler.get(),
                                                                                     dropDown.get())])
# Binds the on_enter and on_leave functions to the executeMe button
executeMe.bind('<Enter>', on_enter)
executeMe.bind('<Leave>', on_leave)
executeMe.grid(row=3, column=1, pady=5)

# Binds the resize_image function to the program.
win.bind('<Configure>', resize_image)

win.mainloop()
