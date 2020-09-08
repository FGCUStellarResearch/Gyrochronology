import matplotlib.pyplot as plt

def plot_graph(x, y, xlab=None, ylab=None, title=None, plt_text=None, box_x =None, box_y = None):
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    box = dict(boxstyle = 'round', facecolor = 'wheat', alpha = 0.5)
    plt.text(box_x, box_y, plt_text, ha='left', va='center', bbox = box)
    plt.show()
