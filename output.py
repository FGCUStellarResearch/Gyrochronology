import matplotlib.pyplot as plt

def plot_graph(x, y, xlab=None, ylab=None, title=None, plt_text=None, box_x =None, box_y = None):
    """Function to plot all the necessary components of period finding algorithm results.
    Args:
        x (List): X-values to be plotted.
        y (List): Y-values to be plotted
        xlab (String, optional): Label for x-axis. Defaults to None.
        ylab (String, optional): Label for y-axis. Defaults to None.
        title (String, optional): Title of plot. Defaults to None.
        plt_text (String, optional): Peak and uncertainty values. Defaults to None.
        box_x (Float, optional): X-position of plt_text. Defaults to None.
        box_y (Float, optional): Y-position of plt_text. Defaults to None.
    """    
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    box = dict(boxstyle = 'round', facecolor = 'wheat', alpha = 0.5)
    plt.text(box_x, box_y, plt_text, ha='left', va='center', bbox = box)
    plt.show()
   # plt.savefig(filename + '.png')
