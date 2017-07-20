"""
Main module for binging together all the steps needed for the occupancy measurement

K. Schweiger, 2017
"""
from ConfigParser import SafeConfigParser
import logging

import modules.classes as classes

def getValuesPerLayer(n, nModules, collBunches, isCluster = False,
                      RevFrequ = 11245, ActiveModArea = 10.45, PixperMod = 66560 ):
    """
    Function for calculating mean values per Layer:
    * hit pixel/cluster per module
    * hit pixel/cluster per area [cm^-2]
    * hit pixel/cluster par area rate [cm^-2 s^-1]
    * occupancy

    Set isCluster to True if used for cluster because occupancy can ne be measured.

    returns dict with keys: PixpMod, PixpArea, PixpAreaSec, Occ
    """

    perMod = n / float(nModules)
    perArea, perAreaSec = calculateCommonValues(perMod, collBunches, RevFrequ, ActiveModArea, PixperMod)

    occupancy = None
    if not isCluster:
        occupancy =  perMod / PixperMod

    return {"perMod" : perMod, "perArea" : perArea, "perAreaSec" : perAreaSec, "Occ" : occupancy}

def getValuesPerDet(nperDet, collBunches, isCluster = False,
                    RevFrequ = 11245, ActiveModArea = 10.45, PixperMod = 66560):
    """
    Function for calculating mean values per Det/Module:
    * hit pixel/cluster per area [cm^-2]
    * hit pixel/cluster par area rate [cm^-2 s^-1]
    * occupancy

    Set isCluster to True if used for cluster because occupancy can ne be measured.

    returns dict with keys: PixpMod, PixpArea, PixpAreaSec, Occ
    """

    perArea, perAreaSec = calculateCommonValues(nperDet, collBunches, RevFrequ, ActiveModArea, PixperMod)

    occupancy = None
    if not isCluster:
        occupancy =  nperDet / PixperMod

    return {"perMod" : nperDet, "perArea" : perArea, "perAreaSec" : perAreaSec, "Occ" : occupancy}

def calculateCommonValues(nPerModule, collBunches, RevFrequ, ActiveModArea, PixperMod):
    perArea = nPerModule / float(ActiveModArea)
    perAreaSec = perArea * collBunches * RevFrequ

    return perArea, perAreaSec

def occupancyFromFile(inputfile, collBunchesforRun):
    """
    Calculate occupency and related values from a preprocesst file containing
    the nescessary histograms

    TODO: Link DPGPixel Github
    """
    filename = inputfile.split("/")[-1].split(".")[0]
    logging.info("Processing file: {0}".format(filename))
    logging.debug("File location: {0}".format(inputfile))
    Resultcontainer = classes.container(filename, inputfile, collBunchesforRun)
    Resultcontainer.printValues()
