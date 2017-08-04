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

    returns dict with keys: PixpMod, PixpArea, PixpAreaSec, Occ
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

    returns dict with keys: PixpMod, PixpArea, PixpAreaSec, Occ
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

        container = classes.container(run, inputfile, collBunches, instLumi, comment)
        if not container.invalidFile:
            Resultcontainers[run] = copy(container)
        else:
            invalidruns.append(run)
        del container
        #modules.output.makeTabel(Resultcontainers[run], outputname = "out"+run.replace(" ",""))
        #print Resultcontainers
    for run in invalidruns:
        runstoProcess.remove(run)
    #modules.pandasOutput.getDataFrames(Resultcontainers, runstoProcess)
    modules.pandasOutput.makeInnerOuterLadderDetectorTables(Resultcontainers, runstoProcess)
    #modules.pandasOutput.makeFullDetectorTables(Resultcontainers, runstoProcess, "testing")
    #modules.htmlOutput.makeComparisonFiles(generaltitle, generaldesc, Resultcontainers, runstoProcess, foldername)
    generatedplots = []
    for group in ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]:
        generatedfiles = modules.pandasOutput.makeRunComparisonPlots(Resultcontainers, runstoProcess, foldername, group)
        generatedplots.append((generatedfiles , group))
        #modules.htmlOutput.makePlotOverviewFile(generaltitle, generaldesc, generatedfiles, runstoProcess, foldername, group)
    #modules.htmlOutput.makeLandingPage(generaltitle, generatedfiles, runstoProcess, foldername)
    #modules.htmlOutput.makeFiles(generaltitle, generaldesc, Resultcontainers, runstoProcess, foldername,
    #                             makeIndex = True, makeTables = True, makePlotOverview = True,
    #                             plottuples = generatedplots)
    modules.output.makeFiles(generaltitle, generaldesc, Resultcontainers, runstoProcess, foldername, config,
                             makeIndex = True, makeTables = True, makePlotOverview = True,plottuples = generatedplots,
                             exportLaTex = texexport, exportCSV = csvexport)
        #modules.output.makeRunComparisonTable(Resultcontainers)

def occupancyFromFile(inputfile, collBunchesforRun, instLumi):
    """
    Calculate occupency and related values from a preprocesst file containing
    the nescessary histograms

    TODO: Link DPGPixel Github
    """
    filename = inputfile.split("/")[-1].split(".")[0]
    logging.info("Processing file: {0}".format(filename))
    logging.debug("File location: {0}".format(inputfile))
    Resultcontainer = classes.container(filename, inputfile, collBunchesforRun, instLumi)
    Resultcontainer.printValues()
    #print modules.output.formatContainerFullPixelDetector(Resultcontainer)
    modules.output.makeTabel(Resultcontainer)
