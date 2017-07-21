import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def writeStringToFile(string, filename):
    with open(filename, "w+") as f:
        f.write(string)

def writeListToFile(stringlist, filename):
    with open(filename, "w+") as f:
        for string in stringlist:
            f.write(string)


def getDataFramesForRunComp(containerlist, runlist, datatype = "fullDetector"):
    dataframes = {}
    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]

    runseries = pd.Series(runlist)

    slices = {}
    for name in layerNames:
        slices[name] = {}
        for group in groups:
            slices[name][group] = {}
    for run in runseries:
        containerDF = containerlist[run].getpdDataFrame(datatype)
        for name in layerNames:
            for group in groups:
                slices[name][group].update({ run : containerDF[group].loc[name]})


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


def makeHTMLfile(containerlist, runlist, foldername):
    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]

    perRunTables, runcomparisonperLayer = makeFullDetectorTables(containerlist, runlist)

    if not os.path.exists(foldername):
        os.makedirs(foldername)

    #HTML file with "Pix/Lay", "Pix/Det", "Clus/Lay" and "Clus/Det" tables for all layer and all processed runs
    blocks = []
    header = "<!DOCTYPE html> \n <html> \n <body> \n"
    blocks.append(header)
    style = "<style> \n table, th, td {\nborder: 1px solid black;\n border-collapse: collapse;\n}\nth, td { padding: 8px; }\n</style>\n"
    blocks.append(style)
    for run in runlist:
        block = "<hr>\n<h2>{0}</h2>\n".format(run)
        for group in groups:
            block = block + "<h3>{0}</h3>\n{1}".format(group, perRunTables[run][group].to_html())
        blocks.append(block+"<br>\n")
    footer = "</body> \n </html> \n"
    blocks.append(footer)
    writeListToFile(blocks, "{0}/perRunTables.html".format(foldername))
    #HTML file per Layer with comparisons for all processed runs for "Pix/Lay", "Pix/Det", "Clus/Lay" and "Clus/Det"
    for layer in layerNames:
        blocks = []
        blocks.append(header)
        blocks.append(style)
        block = "<hr>\n<h2>{0}</h2>\n".format(layer)
        for group in groups:
            block = block + "<hr>\n<h3>{0}</h3>\n{1}".format(group, runcomparisonperLayer[layer][group].to_html())
        blocks.append(block+"<br>\n")
        blocks.append(footer)
        writeListToFile(blocks, "{0}/runComparison{1}.html".format(foldername, layer))
