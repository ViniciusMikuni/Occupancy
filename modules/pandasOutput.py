import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import logging

def writeStringToFile(string, filename):
    logging.debug("Writing string to file: {0}".format(filename))
    with open(filename, "w+") as f:
        f.write(string)

def writeListToFile(stringlist, filename):
    logging.debug("Writing list of strings to file: {0}".format(filename))
    with open(filename, "w+") as f:
        for string in stringlist:
            f.write(string)


def getDataFramesForRunComp(containerlist, runlist, datatype = "fullDetector"):
    dataframes = {}
    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]

    #runseries = pd.Series(runlist)

    slices = {}
    for name in layerNames:
        slices[name] = {}
        for group in groups:
            slices[name][group] = {}
    for run in runlist:
        #print run
        containerDF = containerlist[run].getpdDataFrame(datatype)
        for name in layerNames:
            for group in groups:
                generalinfo = pd.Series([containerlist[run].nWorkingModules[name], containerlist[run].collBunches],
                                  index = ["nModules", "nBunches"])
                slices[name][group].update({ run : generalinfo.append(containerDF[group].loc[name])})
                #print "slice[{0}][{1}] = \n{2}".format(name,group,slices[name][group][run])

    for name in layerNames:
        #print "-----------"+name+"-----------"
        dataframes[name] = {}
        for group in groups:
            #print "++++++++"+group+"++++++++"
            dataframes[name][group] = pd.DataFrame(slices[name][group]).transpose()
            #print dataframes[name][group]


    return dataframes
    #writeStringToFile(b.to_html(), "test.html")

def makeFullDetectorTables(containerlist, runlist, foldername = None):
    logging.info("Getting pandas DF for full detector")
    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]

    runtables = {}
    if foldername is not None:
        if not os.path.exists(foldername):
            os.makedirs(foldername)
    for run in runlist:
        runtables[run] = {}
        data = containerlist[run].getpdDataFrame("fullDetector")
        for group in groups:
            runtables[run][group] = data[group]
            #writeStringToFile(data[group].to_html(), "{0}/filldet_{1}_{2}.html".format(foldername, run.replace(" ","-"), group.replace("/","per")))
    runcomparisonperLayer = getDataFramesForRunComp(containerlist, runlist, "fullDetector")

    return runtables, runcomparisonperLayer


def makeHTMLfile(title, generaldescription, containerlist, runlist, foldername):
    logging.info("Processing runs and generate HTML files")
    from ConfigParser import SafeConfigParser
    styleconfig = SafeConfigParser()
    logging.debug("Loading style config")
    styleconfig.read("configs/style.cfg")

    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]

    perRunTables, runcomparisonperLayer = makeFullDetectorTables(containerlist, runlist)

    if not os.path.exists(foldername):
        logging.info("Creating folder: {0}".format(foldername))
        os.makedirs(foldername)

    logging.info("Generating HTML files")
    #HTML file with "Pix/Lay", "Pix/Det", "Clus/Lay" and "Clus/Det" tables for all layer and all processed run
    header = "<!DOCTYPE html> \n <html> \n <body> \n"
    style = "<style> \n table, th, td {{\nborder: {0} solid black;\n border-collapse: collapse;\n}}\nth, td {{ padding: {1}; }}\n</style>\n".format(styleconfig.get("Tables","bordersize"),styleconfig.get("Tables","padding"))
    title = "<h1>{0}</h1>{1}\n".format(title, generaldescription)
    blocks = []
    blocks.append(header)
    blocks.append(style)
    blocks.append(title)
    for run in runlist:
        block = "<hr>\n<h2>{0}</h2>\n{1}<br>\nDataset: {2}<br>\n".format(run, containerlist[run].comments[0], containerlist[run].comments[1])
        block = block + "Working modules (from hpDetMap):<br>"
        for layer in layerNames:
            block = block + "{0}: {1} modules<br>".format(layer, containerlist[run].nWorkingModules[layer])
        for group in groups:
            block = block + "<h3>{0}</h3>\n{1}".format(styleconfig.get("Renaming",group), perRunTables[run][group].to_html())
        blocks.append(block+"<br>\n")
    footer = "</body> \n </html> \n"
    blocks.append(footer)
    writeListToFile(blocks, "{0}/perRunTables.html".format(foldername))
    #HTML file per Layer with comparisons for all processed runs for "Pix/Lay", "Pix/Det", "Clus/Lay" and "Clus/Det"
    for layer in layerNames:
        blocks = []
        blocks.append(header)
        blocks.append(style)
        blocks.append(title)
        block = "<hr><h2>Run comparion for {0}</h2>\n".format(layer)
        for group in groups:
            block = block + "<hr>\n<h3>{0}</h3>\n{1}".format(styleconfig.get("Renaming",group), runcomparisonperLayer[layer][group].to_html())
        blocks.append(block+"<br>\n")
        blocks.append(footer)
        writeListToFile(blocks, "{0}/runComparison{1}.html".format(foldername, layer))
