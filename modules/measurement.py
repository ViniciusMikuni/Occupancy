"""
Main module for binging together all the steps needed for the occupancy measurement

K. Schweiger, 2017
"""

import logging
from copy import copy

import modules.classes as classes
import modules.output
import modules.pandasOutput
import modules.htmlOutput

def getValuesPerLayer(n, nModules, collBunches, lumi = 1, isCluster = False,
                      RevFrequ = 11245, ActiveModArea = 10.45, PixperMod = 66560 ):
    """
    Function for calculating mean values per Layer:
    * hit pixel/cluster per module
    * hit pixel/cluster per area [cm^-2]
    * hit pixel/cluster par area rate [cm^-2 s^-1]
    * hit pixel/cluster par area rate normalized to inst. Lumi per bunch corossing
    * occupancy

    Set isCluster to True if used for cluster because occupancy can ne be measured.

    returns dict with keys: perMod, perArea, perAreaSec, Occ, perAreaNorm
    """
    logging.debug("calculateing per layer with {0}, {1}, {2}".format(n, nModules, collBunches))


    perMod = n / float(nModules)
    perArea, perAreaSec = calculateCommonValues(perMod, collBunches, RevFrequ, ActiveModArea, PixperMod)


    perAreaNorm = perArea / (lumi / collBunches)
    perAreaSecNorm = perAreaSec / (lumi / collBunches)

    occupancy = None
    if not isCluster:
        logging.debug("isCluster is set to False: Occupancy calculation")
        occupancy =  perMod / PixperMod

    return {"perMod" : perMod, "Occ" : occupancy,
            "perArea" : perArea, "perAreaSec" : perAreaSec, "perAreaSecNorm" : perAreaSecNorm, "perAreaNorm" : perAreaNorm}

def getValuesPerDet(nperDet, collBunches, lumi = 1, isCluster = False,
                    RevFrequ = 11245, ActiveModArea = 10.45, PixperMod = 66560):
    """
    Function for calculating mean values per Det/Module:
    * hit pixel/cluster per area [cm^-2]
    * hit pixel/cluster par area rate [cm^-2 s^-1]
    * hit pixel/cluster par area rate normalized to inst. Lumi per bunch corossing
    * occupancy

    Set isCluster to True if used for cluster because occupancy can ne be measured.

    returns dict with keys: perMod, perArea, perAreaSec, Occ, perAreaNorm
    """
    logging.debug("calculateing per Det with {0}, {1}".format(nperDet, collBunches))

    perArea, perAreaSec = calculateCommonValues(nperDet, collBunches, RevFrequ, ActiveModArea, PixperMod)

    perAreaNorm = perArea / (lumi / collBunches)
    perAreaSecNorm = perAreaSec / (lumi / collBunches)

    occupancy = None
    if not isCluster:
        logging.debug("isCluster is set to False: Occupancy calculation")
        occupancy =  nperDet / PixperMod

    return {"perMod" : nperDet, "Occ" : occupancy,
            "perArea" : perArea, "perAreaSec" : perAreaSec, "perAreaSecNorm" : perAreaSecNorm, "perAreaNorm" : perAreaNorm}

def calculateCommonValues(nPerModule, collBunches, RevFrequ, ActiveModArea, PixperMod):
    perArea = nPerModule / float(ActiveModArea)
    perAreaSec = perArea * collBunches * RevFrequ

    return perArea, perAreaSec

def occupancyFromConfig(config):
    """
    Calculate occupancy and related values from a config defining files, nBunches,... . See README.md for detailed information.

    Use https://github.com/cms-analysis/DPGAnalysis-SiPixelTools/tree/master/HitAnalyzer/test/PixClusterTest.* to preprocess the data samples.
    """
    from ConfigParser import SafeConfigParser

    logging.info("Processing config {0}".format(config))

    cfg = SafeConfigParser(allow_no_value=True)
    cfg.read( config )

    runstoProcess = cfg.sections()[1::] #Ignore General section
    logging.debug("Sections in config: {0}".format(runstoProcess))
    Resultcontainers = {}
    generaldesc = cfg.get("General","description")
    generaltitle = cfg.get("General","title")
    foldername = cfg.get("General","foldername")
    texexport = cfg.getboolean("General","latexexport")
    csvexport = cfg.getboolean("General","csvexport")
    cfgexport = cfg.getboolean("General","cfgexport")
    invalidruns = []
    for run in runstoProcess:
        logging.info("Processing section {1} from config {0}".format(config, run))
        if cfg.get(run, "file") is not None:
            inputfile = cfg.get(run, "file")
        else:
            inputfile = ""
        collBunches = cfg.getfloat(run, "collidingBunches")
        instLumi =  cfg.getfloat(run, "lumi")
        comment = [cfg.get(run, "comment"),cfg.get(run, "dataset")]
        nFiles = cfg.getint(run, "nFiles")

        container = classes.container(run, inputfile, collBunches, instLumi, comment, nFiles)
        if not container.invalidFile:
            Resultcontainers[run] = copy(container)
        else:
            invalidruns.append(run)
        del container

    for run in invalidruns:
        runstoProcess.remove(run)

    generatedplots = []
    makeplots = False
    if makeplots:
        for group in ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]:
            generatedfiles = modules.pandasOutput.makeRunComparisonPlots(Resultcontainers, runstoProcess, foldername, group)
            generatedplots.append((generatedfiles , group))

    modules.output.makeFiles(generaltitle, generaldesc, Resultcontainers, runstoProcess, foldername, config,
                             makeIndex = True, makeTables = True, makePlotOverview = makeplots, plottuples = generatedplots,
                             exportLaTex = texexport, exportCSV = csvexport, exportCFG = cfgexport)

def occupancyFromFile(inputfile, collBunchesforRun, instLumi, nFiles):
    """
    Calculate occupancy and related values from a preprocesst file containing
    the nescessary histograms

    Use https://github.com/cms-analysis/DPGAnalysis-SiPixelTools/tree/master/HitAnalyzer/test/PixClusterTest.* to preprocess the data samples.
    """
    filename = inputfile.split("/")[-1].split(".")[0]
    logging.info("Processing file: {0}".format(filename))
    logging.debug("File location: {0}".format(inputfile))
    Resultcontainer = classes.container(filename, inputfile, collBunchesforRun, instLumi, nFiles = nFiles)

    modules.htmlOutput.makeComparisonFiles("Occupancy monitoring for file {0}".format(filename.split("/")[-1]), "", {"Processed Run": Resultcontainer},
                                           ["Processed Run"], ".", singlerun = True)
