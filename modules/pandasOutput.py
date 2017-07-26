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
                generalinfo = pd.Series([containerlist[run].nWorkingModules[name],
                                         containerlist[run].collBunches,
                                         containerlist[run].instLumi],
                                        index = ["nModules", "nBunches", "instLumi"])
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

def makeFullDetectorTables(containerlist, runlist, singlerun = False):
    logging.info("Getting pandas DF for full detector")
    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]

    runtables = {}
    for run in runlist:
        runtables[run] = {}
        data = containerlist[run].getpdDataFrame("fullDetector")
        for group in groups:
            runtables[run][group] = data[group]
            #writeStringToFile(data[group].to_html(), "{0}/filldet_{1}_{2}.html".format(foldername, run.replace(" ","-"), group.replace("/","per")))
    if not singlerun:
        runcomparisonperLayer = getDataFramesForRunComp(containerlist, runlist, "fullDetector")
    else:
        runcomparisonperLayer = None

    return runtables, runcomparisonperLayer

def makeZdepDetectorTables(containerlist, runlist, singlerun = False):
    logging.info("Getting pandas DF for z-dependent detector parts")
    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    groups = ["Pix/Lay"] # necessary for current implementation of z-dependency
    #groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]

    runtables, runcomparisonperLayer = {}, None
    for run in runlist:
        runtables[run] = {}
        datadict = containerlist[run].getpdDataFrame("partialDetectorZ")
        for group in groups:
            runtables[run][group] = {}
            data = datadict[group]
            for layer in layerNames:
                layerdata = data.loc[layer]
                layerseries = {}
                for z in containerlist[run].zpositions:
                    positiondata = layerdata[z]
                    series = pd.Series([containerlist[run].nWorkingModulesZ[layer][z]], index = ["nModules"])
                    series = series.append(positiondata)
                    layerseries[z] = series
                currentDF = pd.DataFrame(layerseries)
                currentDF = currentDF[containerlist[run].zpositions]
                runtables[run][group][layer] = currentDF.transpose()
    #TODO: Implement run comparison per z position
    return runtables, runcomparisonperLayer


def makeHTMLfile(titlestring, generaldescription, containerlist, runlist, foldername, singlerun = False):
    logging.info("Processing runs and generate HTML files")
    from ConfigParser import SafeConfigParser
    styleconfig = SafeConfigParser()
    logging.debug("Loading style config")
    styleconfig.read("configs/style.cfg")

    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]

    perRunTables, runcomparisonperLayer = makeFullDetectorTables(containerlist, runlist, singlerun)

    if not os.path.exists(foldername):
        logging.info("Creating folder: {0}".format(foldername))
        os.makedirs(foldername)

    logging.info("Generating HTML files")
    #HTML file with "Pix/Lay", "Pix/Det", "Clus/Lay" and "Clus/Det" tables for all layer and all processed run
    header = "<!DOCTYPE html> \n <html> \n <body> \n"
    style = "<style> \n table, th, td {{\nborder: {0} solid black;\n border-collapse: collapse;\n}}\nth, td {{ padding: {1}; }}\n</style>\n".format(styleconfig.get("Tables","bordersize"),styleconfig.get("Tables","padding"))
    title = "<h1>{0}</h1>{1}\n".format(titlestring, generaldescription)
    blocks = []
    blocks.append(header)
    blocks.append(style)
    blocks.append(title)
    for run in runlist:
        block = "<hr>\n<h2>{0}</h2>\n{1} with average inst. luminosity: {2} cm^-2 s^-1<br>\nDataset: {3}<br>\n".format(run, containerlist[run].comments[0], containerlist[run].instLumi, containerlist[run].comments[1])
        block = block + "Working modules (from hpDetMap):<br>"
        for layer in layerNames:
            block = block + "{0}: {1} modules<br>".format(layer, containerlist[run].nWorkingModules[layer])
        for group in groups:
            block = block + "<h3>{0} ({1})</h3>\n<b>{2}</b>".format(styleconfig.get("Renaming", group), group, perRunTables[run][group].to_html())
        blocks.append(block+"<br>\n")
    footer = "</body> \n </html> \n"
    blocks.append(footer)
    writeListToFile(blocks, "{0}/perRunTables.html".format(foldername))
    #HTML file per Layer with comparisons for all processed runs for "Pix/Lay", "Pix/Det", "Clus/Lay" and "Clus/Det"
    if runcomparisonperLayer is not None:
        for layer in layerNames:
            blocks = []
            blocks.append(header)
            blocks.append(style)
            blocks.append(title)
            block = "<h2>Run comparion for {0}</h2>\n".format(layer)
            for group in groups:
                block = block + "<hr>\n<h3>{0} ({1})</h3>\n{2}".format(styleconfig.get("Renaming", group), group, runcomparisonperLayer[layer][group].to_html())
            blocks.append(block+"<br>\n")
            blocks.append(footer)
            writeListToFile(blocks, "{0}/runComparison{1}.html".format(foldername, layer))
    #HTML file per group with z-dependent values per layer
    #for group in groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]:
    perRunTables = makeZdepDetectorTables(containerlist, runlist, singlerun)[0]
    for group in ["Pix/Lay"]:
        blocks = []
        blocks.append(header)
        blocks.append(style)
        blocks.append("<h1>{0} - z-dependency</h1>{1}\n<br><b>{2} ({3})</b>".format(titlestring, generaldescription, styleconfig.get("Renaming", group), group))
        for run in runlist:
            block = "<hr>\n<h2>{0}</h2>\n{1} with average inst. luminosity: {2} cm^-2 s^-1<br>\nDataset: {3}<br>\n".format(run, containerlist[run].comments[0], containerlist[run].instLumi, containerlist[run].comments[1])
            for layer in layerNames:
                block = block + "<h3>{0}</h3>\n{1}".format(layer, perRunTables[run][group][layer].to_html())
            blocks.append(block+"<br>\n")
            blocks.append(footer)
            writeListToFile(blocks, "{0}/zDependency{1}.html".format(foldername, group.replace("/","per")))
