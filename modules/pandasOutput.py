import pandas as pd
import numpy as np

import os
import logging
from copy import copy

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

    slices = {}
    for name in layerNames:
        slices[name] = {}
        for group in groups:
            slices[name][group] = {}
    for run in runlist:
        containerDF = containerlist[run].getpdDataFrame(datatype)
        for name in layerNames:
            for group in groups:
                generalinfo = pd.Series([containerlist[run].nWorkingModules[name],
                                         containerlist[run].collBunches,
                                         containerlist[run].instLumi],
                                        index = ["nModules", "nBunches", "instLumi"])
                slices[name][group].update({ run : generalinfo.append(containerDF[group].loc[name])})

    for name in layerNames:
        dataframes[name] = {}
        for group in groups:
            dataframes[name][group] = pd.DataFrame(slices[name][group]).transpose()

    return dataframes

def makeFullDetectorTables(containerlist, runlist, singlerun = False):
    logging.info("Getting pandas DF for full detector")
    groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]

    runtables = {}
    for run in runlist:
        runtables[run] = {}
        data = containerlist[run].getpdDataFrame("fullDetector")
        for group in groups:
            runtables[run][group] = data[group]
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
    # if not singler:
    return runtables, runcomparisonperLayer

def makeInnerOuterLadderDetectorTables(containerlist, runlist, singlerun = False):
    logging.info("Getting pandas DF for inner and outer ladder detector parts")
    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    groups = ["Pix/Lay"]

    runtables, runcomparisonperLayer = {}, {}
    for run in runlist:
        runtables[run] = {}
        datadict = containerlist[run].getpdDataFrame("partialDetectorInnerOuterLadders")
        for group in groups:
            runtables[run][group] = {}
            data = datadict[group]
            for layer in layerNames:
                layerdata = data.loc[layer]
                layerseries = {}
                for ladder in ["inner", "outer"]:
                    positiondata = layerdata[ladder]
                    series = pd.Series([containerlist[run].nWorkingModulesInOut[layer][ladder]], index = ["nModules"])
                    series = series.append(positiondata)
                    layerseries[ladder] = series
                currentDF = pd.DataFrame(layerseries)
                runtables[run][group][layer] = currentDF.transpose()
    if not singlerun:
        # RunComparison tables -> For inner/outer ladder -> for each layer -> for each group -> for each run on row
        # ----> runcomparisonperLayer[ladder][layer][group]
        slices = {}
        for group in groups:
            slices[group] = {}
            for ladder in ["inner", "outer"]:
                slices[group][ladder] = {}
                for layer in layerNames:
                    slices[group][ladder][layer] = {}

        for run in runlist:
            datadict = containerlist[run].getpdDataFrame("partialDetectorInnerOuterLadders")
            for group in groups:
                for ladder in ["inner", "outer"]:
                    for layer in layerNames:
                        layerdataforLadderLayer = datadict[group].transpose().loc[ladder].transpose().loc[layer]

                        generalinfo = pd.Series([containerlist[run].nWorkingModulesInOut[layer][ladder],
                                                 containerlist[run].collBunches,
                                                 containerlist[run].instLumi],
                                                index = ["nModules", "nBunches", "instLumi"])
                        slices[group][ladder][layer][run] = generalinfo.append(layerdataforLadderLayer)

        runcomparisonperLayer = {}
        for group in groups:
            runcomparisonperLayer[group] = {}
            for ladder in ["inner", "outer"]:
                runcomparisonperLayer[group][ladder] = {}
                for layer in layerNames:
                    runcomparisonperLayer[group][ladder][layer] = pd.DataFrame(slices[group][ladder][layer]).transpose()
    else:
        runcomparisonperLayer = None
        
    return runtables, runcomparisonperLayer

def makeRunComparisonPlots(containerlist, runlist, foldername, group):
    if group not in ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]:
        logging.error("Group *{0}* is not supported".format(group))
        generatedplots = None
    else:
        generatedplots = []

        runcompperlayer = makeFullDetectorTables(containerlist, runlist)[1]
        perRunTablesZDependent = makeZdepDetectorTables(containerlist, runlist)[0]
        rumcompladders = modules.pandasOutput.makeInnerOuterLadderDetectorTables(containerlist, runlist)[1]
        prefix = "RunComp"
        generatedplots.append(modules.plotting.makeDiYAxisplot(runcompperlayer["Layer1"][group]["instLumi"],
                                                               r"average inst. Lumi [cm$^{-2}$s$^{-1}$]",
                                                               runcompperlayer["Layer1"][group]["nBunches"],
                                                               "Number of colliding bunches",
                                                               "{0}LumiVsnBunches_allLayers".format(prefix),
                                                               "", foldername))
        if group.startswith("Pix"):
            generatedplots.append(modules.plotting.makecomparionPlot([runcompperlayer["Layer1"][group]["occupancy"],
                                                                      runcompperlayer["Layer2"][group]["occupancy"],
                                                                      runcompperlayer["Layer3"][group]["occupancy"],
                                                                      runcompperlayer["Layer4"][group]["occupancy"]],
                                                                     ["Layer1","Layer2","Layer3","Layer4"],
                                                                     "{0}_{1}_Occupancy_allLayers".format(prefix, group.replace("/","per")),
                                                                     foldername = foldername, yTitle = r"Occupancy"))
        generatedplots.append(modules.plotting.makecomparionPlot([runcompperlayer["Layer1"][group]["perAreaNorm"],
                                                                  runcompperlayer["Layer2"][group]["perAreaNorm"],
                                                                  runcompperlayer["Layer3"][group]["perAreaNorm"],
                                                                  runcompperlayer["Layer4"][group]["perAreaNorm"]],
                                                                 ["Layer1","Layer2","Layer3","Layer4"],
                                                                 "{0}_{1}_perAreaNorm_allLayers".format(prefix, group.replace("/","per")),
                                                                 foldername = foldername, yTitle = r"Hits per module area norm. to inst. luminosity per bunch"))
        generatedplots.append(modules.plotting.makecomparionPlot([runcompperlayer["Layer1"][group]["perAreaSec"],
                                                                  runcompperlayer["Layer2"][group]["perAreaSec"],
                                                                  runcompperlayer["Layer3"][group]["perAreaSec"],
                                                                  runcompperlayer["Layer4"][group]["perAreaSec"]],
                                                                 ["Layer1","Layer2","Layer3","Layer4"],
                                                                 "{0}_{1}_perAreaSec_allLayers".format(prefix, group.replace("/","per")),
                                                                 foldername = foldername, yTitle = r"hit rate per active module area [cm$^{-2}$s$^{-1}$]"))
        generatedplots.append(modules.plotting.makecomparionPlot([runcompperlayer["Layer1"][group]["perArea"],
                                                                  runcompperlayer["Layer2"][group]["perArea"],
                                                                  runcompperlayer["Layer3"][group]["perArea"],
                                                                  runcompperlayer["Layer4"][group]["perArea"]],
                                                                 ["Layer1","Layer2","Layer3","Layer4"],
                                                                 "{0}_{1}_density_allLayers".format(prefix, group.replace("/","per")),
                                                                 foldername = foldername, yTitle = r"Hits per module area [cm$^{-2}$]"))
        #Run comparisons
        for layer in ["Layer1", "Layer2", "Layer3", "Layer4"]:
            normrate = runcompperlayer[layer][group]["perAreaNorm"]
            lumiperbx = runcompperlayer[layer][group]["instLumi"]/runcompperlayer["Layer1"][group]["nBunches"]

            generatedplots.append(modules.plotting.makeDiYAxisplot(normrate, 'perAreaNorm', lumiperbx, r'LumiperBX [cm$^{-2}$s$^{-1}$]',
                                                                   "{0}_{2}_perAreaNorm{1}".format(prefix, layer, group.replace("/","per")),
                                                                   layer, foldername))
            doplots = False
            if group == "Pix/Lay":
                doplots = True
                othergroup = "Pix/Det"
            elif group == "Clus/Lay":
                doplots = True
                othergroup = "Clus/Det"
            if doplots:
                if group == "Pix/Lay":
                    generatedplots.append(modules.plotting.makeDiYAxisplot(runcompperlayer[layer][group]["occupancy"], r"Occupancy",
                                                                           lumiperbx, r'Inst. luminosity per coolliding bunch [cm$^{-2}$s$^{-1}$]',
                                                                           "{0}_{2}_Occupancy{1}".format(prefix, layer, group.replace("/","per")),
                                                                           layer, foldername))
                    generatedplots.append(modules.plotting.makecomparionPlot([runcompperlayer[layer][group]["occupancy"],
                                                                              runcompperlayer[layer][othergroup]["occupancy"]],
                                                                             [r"Calculated from layer", r"Calculated from dets"],
                                                                             "{0}_{2}_LayerVsDet_Occupancy{1}".format(prefix, layer, group.replace("/","per")),
                                                                             plottitle = layer, foldername = foldername,
                                                                             yTitle = r"Occupancy"))
                generatedplots.append(modules.plotting.makecomparionPlot([runcompperlayer[layer][group]["perAreaSec"],runcompperlayer[layer][othergroup]["perAreaSec"]],
                                                                         [r"Calculated from layer", r"Calculated from dets"],
                                                                         "{0}_{2}_LayerVsDet_rate{1}".format(prefix, layer, group.replace("/","per")),
                                                                         plottitle = layer, foldername = foldername,
                                                                         yTitle = r"hit rate per active module area [cm$^{-2}$s$^{-1}$]"))
                generatedplots.append(modules.plotting.makecomparionPlot([runcompperlayer[layer][group]["perAreaNorm"],runcompperlayer[layer][othergroup]["perAreaNorm"]],
                                                                         [r"Calculated from layer", r"Calculated from dets"],
                                                                         "{0}_{2}_LayerVsDet_areaNorm{1}".format(prefix, layer, group.replace("/","per")),
                                                                         plottitle = layer, foldername = foldername,
                                                                         yTitle = r"Hits per module area norm. to inst. luminosity per bunch"))
        # Inner/Outer ladder dependency
        if group == "Pix/Lay":
            for layer in ["Layer1", "Layer2", "Layer3", "Layer4"]:
                generatedplots.append(modules.plotting.makecomparionPlot([rumcompladders["Pix/Lay"]["inner"][layer]["occupancy"],
                                                                          rumcompladders["Pix/Lay"]["outer"][layer]["occupancy"],
                                                                          runcompperlayer[layer]["Pix/Lay"]["occupancy"]],
                                                                         [r"Inner Ladder", r"Outer Ladder",r"Full layer"],
                                                                         "InnerVsOuterRunComp_{0}_occupancy".format(layer), plottitle = layer,
                                                                         foldername = foldername, yTitle = r"Occupancy"))
                generatedplots.append(modules.plotting.makecomparionPlot([rumcompladders["Pix/Lay"]["inner"][layer]["perAreaSec"],
                                                                          rumcompladders["Pix/Lay"]["outer"][layer]["perAreaSec"],
                                                                          runcompperlayer[layer]["Pix/Lay"]["perAreaSec"]],
                                                                         [r"Inner Ladder", r"Outer Ladder",r"Full layer"],
                                                                         "InnerVsOuterRunComp_{0}_perAreaSec".format(layer), plottitle = layer,
                                                                         foldername = foldername, yTitle = r"hit rate per active module area [cm$^{-2}$s$^{-1}$]"))
                generatedplots.append(modules.plotting.makecomparionPlot([rumcompladders["Pix/Lay"]["inner"][layer]["perAreaNorm"],
                                                                          rumcompladders["Pix/Lay"]["outer"][layer]["perAreaNorm"],
                                                                          runcompperlayer[layer]["Pix/Lay"]["perAreaNorm"]],
                                                                         [r"Inner Ladder", r"Outer Ladder",r"Full layer"],
                                                                         "InnerVsOuterRunComp_{0}_perAreaNorm".format(layer), plottitle = layer,
                                                                         foldername = foldername, yTitle = r"Hits per module area norm. to inst. luminosity per bunch"))
                generatedplots.append(modules.plotting.makecomparionPlot([rumcompladders["Pix/Lay"]["inner"][layer]["nhit"],
                                                                          rumcompladders["Pix/Lay"]["outer"][layer]["nhit"],
                                                                          runcompperlayer[layer]["Pix/Lay"]["nhit"]],
                                                                         [r"Inner Ladder", r"Outer Ladder",r"Full layer"],
                                                                         "InnerVsOuterRunComp_{0}_nhit".format(layer), plottitle = layer,
                                                                         foldername = foldername, yTitle = r"Number of pixels hit"))

        # Z dependency
        if group == 'Pix/Lay':
            for values in zip(["occupancy", 'perAreaSec', 'perAreaNorm'],
                              [r"Occupancy",r"hit rate per active module area [cm$^{-2}$s$^{-1}$]",r"Hits per module area norm. to inst. luminosity per bunch"]):
                runcompperLayer = {"Layer1" : {}, "Layer2" : {}, "Layer3" : {}, "Layer4" : {}}
                for run in runlist:
                    plotdict = {}
                    for layer in ["Layer1", "Layer2", "Layer3", "Layer4"]:
                        plotdict[layer] = perRunTablesZDependent[run]['Pix/Lay'][layer][values[0]]
                        runcompperLayer[layer][run] = perRunTablesZDependent[run]['Pix/Lay'][layer][values[0]]
                    generatedplots.append(modules.plotting.plotDataFrame(pd.DataFrame(plotdict), "Zdep_{0}_{1}".format(run,values[0]), "Z position", values[1], foldername = foldername, plottitle = run))
                #for layer in ["Layer1", "Layer2", "Layer3", "Layer4"]:
                #    generatedplots.append(modules.plotting.plotDataFrame(pd.DataFrame(runcompperLayer[layer]), "ZdepRunComp_{0}_{1}".format(layer, values[0]),
                #                                                         "Z position", values[1], foldername = foldername, plottitle = layer))

    return generatedplots
