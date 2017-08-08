from ConfigParser import SafeConfigParser

import matplotlib.pyplot as plt
from matplotlib import rc, rcParams
import os
import logging

# activate latex text rendering
rc('text', usetex=True)
plt.style.use('seaborn') #This can lead to a crash. To review all available styles use `print plt.style.available`.
SMALL_SIZE = 13
MEDIUM_SIZE = 14
BIGGER_SIZE = 16

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

styleconfig = SafeConfigParser()
logging.debug("Loading style config")
styleconfig.read("configs/style.cfg")

dpi = styleconfig.getint("Plotting","dpi")
logging.debug("Setting DPI to {0}".format(dpi))
savepdf = styleconfig.getboolean("Plotting","savepdf")
logging.debug("Setting pdf output to: {0}".format(savepdf))

def makefolder(foldername):
    if foldername is not None:
        if not os.path.exists(foldername):
            logging.info("Creating folder: {0}".format(foldername))
            os.makedirs(foldername)
        if not os.path.exists(foldername+"/plots"):
            logging.info("Creating folder: {0}/plots".format(foldername))
            os.makedirs(foldername+"/plots")
        path = foldername+"/plots/"
    else:
        if not os.path.exists("plots"):
            logging.info("Creating folder: plots")
            os.makedirs("plots")
        path = "plots/"
    return path

def get_colors():
    return plt.rcParams['axes.prop_cycle'].by_key()['color']

def makeDiYAxisplot(df1, df1yTitle, df2, df2yTitle, filename = None, plottitle = "", foldername = None, isRunComp = True):
    """
    This functions makes plots with two curves that share a x-axis but have different y-axes for pandas series.

    returns: file name with path.
    """
    fig, base = plt.subplots(dpi=dpi)
    if isRunComp:
        fig.subplots_adjust(bottom = 0.16, right = 0.88, left = 0.11, top = 0.92)
    else:
        fig.subplots_adjust(bottom = 0.1, right = 0.88, left = 0.11, top = 0.92)
    second = base.twinx()

    base.text(0.125, 1.015, r"{\huge\textbf{CMS}} {\textit{Preliminary}}", transform=base.transAxes)

    color1 = get_colors()[0]
    color2 = get_colors()[2]

    df1.plot(ax = base, color = color1)
    df2.plot(ax = second, color = color2)

    base.set_title(plottitle)
    base.set_ylabel(df1yTitle)
    base.get_yaxis().get_major_formatter().set_powerlimits((-3, 5))
    second.set_ylabel(df2yTitle)
    second.get_yaxis().get_major_formatter().set_powerlimits((-3, 5))

    base.yaxis.label.set_color(color1)
    second.yaxis.label.set_color(color2)
    base.tick_params(axis='y', colors=color1)
    second.tick_params(axis='y', colors=color2)
    if isRunComp:
        base.set_xticks(range(len(df1.index.values.tolist())))
        base.set_xticklabels(["{0}".format(item) for item in df1.index.values.tolist()], rotation=45)

    path = makefolder(foldername)
    if filename is None:
        filename = "plot_{0}_{1}".format(df1yTitle, df2yTitle)
    logging.info("Saving file: {0}".format(path+filename+".png"))
    plt.savefig(path+filename+".png")
    if savepdf:
        logging.info("Saving file: {0}".format(path+filename+".pdf"))
        plt.savefig(path+filename+".pdf")
    plt.close(fig)

    return path+filename+".png"

def makecomparionPlot(dfs, titles, filename, colors = ["Default"], plottitle = "", foldername = None, yTitle = None, isRunComp = True):
    """
    This functions makes plots of pandas series that share x and y-axis.

    Arguments: * dfs, titles are required to be lists with equal lengths. If colors are passed, thay also need to be
                 a list of the same lengths. If no color list is passed, the default colors of the matplotlib style
                 (see L8) are used. Because the number of different colors depends on the style, it is expanded to be
                 at least as long as the list of curves. This can result in multiple curves with the same
                 color.

    returns: file name with path.
    """
    if not (isinstance(dfs, list) and isinstance(titles, list) and isinstance(colors, list)):
        logging.error("Error while processing plot {0}".format(filename))
        logging.error('Arguments dfs, titles and colors need to be of type list')
        return
    else:
        if not (len(set(map(len, [dfs, titles, colors]))) <= 1 or (len(dfs) == len(titles) and colors[0] == "Default")):
            logging.error("Error while processing plot {0}".format(filename))
            logging.error("dfs, titles and colors have different lengths")
            return
    if colors[0] == "Default":
        colors = get_colors()
        if len(dfs) > len(colors):
            colors = colors * (len(dfs)%len(colors) + 1)
            logging.warning("Default color palette has {0} colors -> More DF passed. Some lines will have the same color!".format(len(colors)))

    fig, base = plt.subplots(dpi=dpi)
    if isRunComp:
        fig.subplots_adjust(bottom = 0.16, right = 0.88, left = 0.11, top = 0.92)
    else:
        fig.subplots_adjust(bottom = 0.1, right = 0.88, left = 0.11, top = 0.92)

    base.text(0.125, 1.015, r"{\huge\textbf{CMS}} {\textit{Preliminary}}", transform=base.transAxes)

    for dftuple in zip(dfs, titles, colors):
        dftuple[0].plot(ax = base, color = dftuple[2], label = dftuple[1])

    if isRunComp:
        base.set_xticks(range(len(dfs[0].index.values.tolist())))
        base.set_xticklabels(["{0}".format(item) for item in dfs[0].index.values.tolist()], rotation=45)

    base.get_yaxis().get_major_formatter().set_powerlimits((-3, 5))

    if yTitle is not None:
        base.set_ylabel(yTitle)

    base.set_title(plottitle)

    plt.legend()
    path = makefolder(foldername)
    logging.info("Saving file: {0}".format(path+filename+".png"))
    plt.savefig(path+filename+".png")
    if savepdf:
        logging.info("Saving file: {0}".format(path+filename+".pdf"))
        plt.savefig(path+filename+".pdf")
    plt.close(fig)

    return path+filename+".png"

def plotDataFrame(df, filename, xtitle, ytitle, legendlabels = None, plottitle = "", foldername = None, isRunComp = False):
    """
    This functions makes plots of a pandas dataframe

    returns: file name with path.
    """
    fig, base = plt.subplots(dpi=dpi)
    if isRunComp:
        fig.subplots_adjust(bottom = 0.16, right = 0.88, left = 0.11, top = 0.92)
    else:
        fig.subplots_adjust(bottom = 0.1, right = 0.88, left = 0.11, top = 0.92)

    base.text(0.125, 1.015, r"{\huge\textbf{CMS}} {\textit{Preliminary}}", transform=base.transAxes)

    base.set_ylabel(ytitle)
    base.set_xlabel(xtitle)
    base.set_title(plottitle)
    base.get_yaxis().get_major_formatter().set_powerlimits((-3, 5))

    df.plot(ax = base)

    path = makefolder(foldername)
    logging.info("Saving file: {0}".format(path+filename+".png"))
    plt.savefig(path+filename+".png")
    if savepdf:
        logging.info("Saving file: {0}".format(path+filename+".pdf"))
        plt.savefig(path+filename+".pdf")
    plt.close(fig)

    return path+filename+".png"
