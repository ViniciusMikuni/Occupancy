"""
Base module for outputs

K. Schweiger, 2017
"""
import logging
import os

import pandas as pd

from collections import OrderedDict

import modules.htmlOutput
import modules.pandasOutput


def makeFiles(titlestring, generaldescription, containerlist, runlist, foldername,
              makeIndex = True, makeTables = True, makePlotOverview = True, plottuples = None,
              exportLaTex = False, exportCSV = False):
    logging.info("Starting file export")
    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]
    ###############################################################
    # Getting dataframes
    fullperRunDF, fullRunCompDF = modules.pandasOutput.makeFullDetectorTables(containerlist, runlist)
    ZperRunDF, ZRunCompDF = modules.pandasOutput.makeZdepDetectorTables(containerlist, runlist)

    #Getting Tables
    logging.debug("Getting perRun tables for full detector")
    fullPerRunDFs = modules.output.makePerRunDFs(fullperRunDF, runlist, groups)
    logging.debug("Getting RunComp tables for full detector")
    fullRunCompDFs = modules.output.makeRunCompDFs(fullRunCompDF, layerNames, groups)
    logging.debug("Getting perRun tables for z partial detector")
    zPerRunDFs = modules.output.makePerRunDFs(ZperRunDF, runlist, ["Pix/Lay"], layerNames)

    # Style config
    from ConfigParser import SafeConfigParser
    styleconfig = SafeConfigParser()
    logging.debug("Loading style config")
    styleconfig.read("configs/style.cfg")
    ###############################################################

    if makeIndex or makeTables or makePlotOverview:
        modules.htmlOutput.makeFiles(titlestring, generaldescription, containerlist, runlist, foldername,
                                     makeIndex, makeTables, makePlotOverview, plottuples, fullperRunDF, fullRunCompDF, ZperRunDF, ZRunCompDF)

    if exportLaTex or exportCSV:
        defaultprecision = pd.get_option('precision')
        if exportLaTex:
            pd.set_option('precision',styleconfig.getint("Tables","latexprecision"))
            logging.info("LaTex export initialized")
            if not os.path.exists("{0}/{1}".format(foldername, "tex")):
                logging.info("Creating folder: {0}".format("{0}/{1}".format(foldername, "tex")))
                os.makedirs("{0}/{1}".format(foldername, "tex"))
            for key in fullPerRunDFs:
                modules.pandasOutput.writeStringToFile(fullPerRunDFs[key].to_latex(), "{0}/tex/fullPerRun_{1}.tex".format(foldername, key.replace("/","per")))
            for key in fullRunCompDFs:
                modules.pandasOutput.writeStringToFile(fullRunCompDFs[key].to_latex(), "{0}/tex/fullRunComp_{1}.tex".format(foldername, key.replace("/","per")))
            for key in zPerRunDFs:
                modules.pandasOutput.writeStringToFile(zPerRunDFs[key].to_latex(), "{0}/tex/zPerRun_{1}.tex".format(foldername, key.replace("/","per")))
            pd.set_option('precision',defaultprecision)
        if exportCSV:
            logging.info("CSV export initialized")
            if not os.path.exists("{0}/{1}".format(foldername, "csv")):
                logging.info("Creating folder: {0}".format("{0}/{1}".format(foldername, "csv")))
                os.makedirs("{0}/{1}".format(foldername, "csv"))
            for key in fullPerRunDFs:
                modules.pandasOutput.writeStringToFile(fullPerRunDFs[key].to_csv(sep=";"), "{0}/csv/fullPerRun_{1}.csv".format(foldername, key.replace("/","per")))
            for key in fullRunCompDFs:
                modules.pandasOutput.writeStringToFile(fullRunCompDFs[key].to_csv(sep=";"), "{0}/csv/fullRunComp_{1}.csv".format(foldername, key.replace("/","per")))
            for key in zPerRunDFs:
                modules.pandasOutput.writeStringToFile(zPerRunDFs[key].to_csv(sep=";"), "{0}/csv/zPerRun_{1}.csv".format(foldername, key.replace("/","per")))

def makePerRunDFs(inputdf, runs, groups, layers = None):
    retDFs = OrderedDict([])
    for run in runs:
        for group in groups:
            if layers is None:
                retDFs.update({"{0}_{1}".format(run,group) : inputdf[run][group]})
            else:
                for layer in layers:
                    retDFs.update({"{0}_{1}_{2}".format(run,group,layer) : inputdf[run][group][layer]})
    return retDFs

def makeRunCompDFs(inputdf, layers, groups):
    retDFs = OrderedDict([])
    for layer in layers:
        for group in groups:
            retDFs.update({"{0}_{1}".format(layer,group) : inputdf[layer][group]})
    return retDFs
