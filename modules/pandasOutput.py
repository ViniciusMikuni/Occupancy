import pandas as pd
import numpy as np

import os
import logging

import modules.plotting

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
                currentDF = currentDF[containerlist[run].zpositions] #Sort z-positions
                runtables[run][group][layer] = currentDF.transpose()
    #TODO: Implement run comparison per z position
    return runtables, runcomparisonperLayer



def makeRunComparisonPlots(containerlist, runlist, foldername):

    generatedplots = []

    runcompperlayer = makeFullDetectorTables(containerlist, runlist)[1]
    perRunTablesZDependent = makeZdepDetectorTables(containerlist, runlist)[0]
    prefix = "RunComp_"
    generatedplots.append(modules.plotting.makeDiYAxisplot(runcompperlayer["Layer1"]['Pix/Lay']["instLumi"], r"average inst. Lumi [cm$^{-2}$s$^{-1}$]",
                                                           runcompperlayer["Layer1"]['Pix/Lay']["nBunches"], "Number of colliding bunches",
                                                           "{0}LumiVsnBunches_allLayers".format(prefix), "", foldername))
    generatedplots.append(modules.plotting.makecomparionPlot([runcompperlayer["Layer1"]['Pix/Lay']["occupancy"],
                                                              runcompperlayer["Layer2"]['Pix/Lay']["occupancy"],
                                                              runcompperlayer["Layer3"]['Pix/Lay']["occupancy"],
                                                              runcompperlayer["Layer4"]['Pix/Lay']["occupancy"]],
                                                             ["Layer1","Layer2","Layer3","Layer4"], "{0}Occupancy_allLayers".format(prefix),
                                                             foldername = foldername, yTitle = r"Occupancy"))
    generatedplots.append(modules.plotting.makecomparionPlot([runcompperlayer["Layer1"]['Pix/Lay']["perAreaNorm"],
                                                              runcompperlayer["Layer2"]['Pix/Lay']["perAreaNorm"],
                                                              runcompperlayer["Layer3"]['Pix/Lay']["perAreaNorm"],
                                                              runcompperlayer["Layer4"]['Pix/Lay']["perAreaNorm"]],
                                                             ["Layer1","Layer2","Layer3","Layer4"], "{0}perAreaNorm_allLayers".format(prefix),
                                                             foldername = foldername, yTitle = r"perAreaNorm"))
    generatedplots.append(modules.plotting.makecomparionPlot([runcompperlayer["Layer1"]['Pix/Lay']["perAreaSec"],
                                                              runcompperlayer["Layer2"]['Pix/Lay']["perAreaSec"],
                                                              runcompperlayer["Layer3"]['Pix/Lay']["perAreaSec"],
                                                              runcompperlayer["Layer4"]['Pix/Lay']["perAreaSec"]],
                                                             ["Layer1","Layer2","Layer3","Layer4"], "{0}perAreaSec_allLayers".format(prefix),
                                                             foldername = foldername, yTitle = r"hits"))
    generatedplots.append(modules.plotting.makecomparionPlot([runcompperlayer["Layer1"]['Pix/Lay']["perArea"],
                                                              runcompperlayer["Layer2"]['Pix/Lay']["perArea"],
                                                              runcompperlayer["Layer3"]['Pix/Lay']["perArea"],
                                                              runcompperlayer["Layer4"]['Pix/Lay']["perArea"]],
                                                             ["Layer1","Layer2","Layer3","Layer4"], "{0}density_allLayers".format(prefix),
                                                             foldername = foldername, yTitle = r"hit density [cm$^{-2}$]"))
    #Run comparisons

    for layer in ["Layer1", "Layer2", "Layer3", "Layer4"]:
        normrate = runcompperlayer[layer]['Pix/Lay']["perAreaNorm"]
        lumiperbx = runcompperlayer[layer]['Pix/Lay']["instLumi"]/runcompperlayer["Layer1"]['Pix/Lay']["nBunches"]

        generatedplots.append(modules.plotting.makeDiYAxisplot(normrate, 'perAreaNorm', lumiperbx, r'LumiperBX [cm$^{-2}$s$^{-1}$]',
                                                               "{0}perAreaNorm{1}".format(prefix, layer), layer, foldername))

        generatedplots.append(modules.plotting.makeDiYAxisplot(runcompperlayer[layer]['Pix/Lay']["occupancy"], r"Occupancy",
                                                               lumiperbx, r'LumiperBX [cm$^{-2}$s$^{-1}$]',
                                                               "{0}Occupancy{1}".format(prefix, layer), layer, foldername))
        generatedplots.append(modules.plotting.makecomparionPlot([runcompperlayer[layer]['Pix/Lay']["occupancy"],runcompperlayer[layer]['Pix/Det']["occupancy"]],
                                                                 [r"Calculated from layer", r"Calculated from dets"],
                                                                 "{0}LayerVsDet_Occupancy{1}".format(prefix, layer),plottitle = layer, foldername = foldername, yTitle = r"Occupancy"))
        generatedplots.append(modules.plotting.makecomparionPlot([runcompperlayer[layer]['Pix/Lay']["perAreaSec"],runcompperlayer[layer]['Pix/Det']["perAreaSec"]],
                                                                 [r"Calculated from layer", r"Calculated from dets"],
                                                                 "{0}LayerVsDet_rate{1}".format(prefix, layer), plottitle = layer, foldername = foldername, yTitle = r"rate [cm$^{-2}$s$^{-1}$]"))
    # Z depdentcy
    for values in zip(["occupancy", 'perAreaSec'],[r"Occupancy",r"rate [cm$^{-2}$s$^{-1}$]"]):
        for run in runlist:
            plotdict = {}
            for layer in ["Layer1", "Layer2", "Layer3", "Layer4"]:
                plotdict[layer] = perRunTablesZDependent[run]['Pix/Lay'][layer][values[0]]
            generatedplots.append(modules.plotting.plotDataFrame(pd.DataFrame(plotdict), "Zdep_{0}_{1}".format(run.split(" ")[1],values[0]), "Z position", values[1], foldername = foldername, plottitle = run))

    return generatedplots
