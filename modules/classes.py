"""
Classes for occupancy measurement

K. Schweiger, 2017
"""
import logging
import ROOT
from copy import copy

from modules.modulecounter import modulecounter
from modules.tests import isHistoinFile
import modules.measurement


class container:
    """
    Container initialized for a run containing all claculations for the occupancy
    and related values.
    """
    def __init__(self, name, inputfile, collBunches):
        logging.debug("Initializing container for {0} with inputfile {1} and colliding bunches {2}".format(name, inputfile, collBunches))
        self.LayerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
        self.zpositions = ["-4", "-3", "-2", "-1", "1", "2", "3", "4"]
        self.name = name
        self.file = ROOT.TFile.Open(inputfile)
        self.collBunches = collBunches

        # Varaiable for full layer
        self.nWorkingModules = modulecounter(self.file)
        #Pixels
        self.hitPix = {}
        self.occupancies = {}
        self.hitPixPerModule = {}
        self.hitPixPerArea = {}
        self.hitPixPerAreaSec = {}

        self.Detoccupancies = {}
        self.hitPixPerDet = {}
        self.hitPixPerDetArea = {}
        self.hitPixPerDetAreaSec = {}
        # Clusters
        self.hitClusters = {}
        self.hitClustersPerModule = {}
        self.hitClustersPerArea = {}
        self.hitClustersPerAreaSec = {}

        self.hitClustersPerDet = {}
        self.hitClustersPerDetArea = {}
        self.hitClustersPerDetAreaSec = {}

        # Set general values
        self.getBaseValuesForallLayer()


    def getBaseValuesForallLayer(self):
        """
        Calculate for each layer:
            * Occupancy (Only for pixels)
            * Pixel/Cluster hit per module
            * Pixel/Cluster hit per cm^2
            * Pixel/Cluster hit per cm^2 per sec
        """
        for ilayer, layer in enumerate(self.LayerNames):
            logging.info("Setting base values for {0}".format(layer))
            ############################################################################################
            # Pixels per Layer
            currentmean = getHistoMean(self.file, "d/hpixPerLay"+str(ilayer+1))
            self.hitPix[layer] = currentmean
            values = modules.measurement.getValuesPerLayer(currentmean, self.nWorkingModules[layer], self.collBunches)
            self.occupancies[layer] = values["Occ"]
            self.hitPixPerModule[layer] = values["perMod"]
            self.hitPixPerArea[layer] = values["perArea"]
            self.hitPixPerAreaSec[layer] = values["perAreaSec"]
            # Pixels per Det
            currentmean = getHistoMean(self.file, "d/hpixPerDet"+str(ilayer+1))
            values = modules.measurement.getValuesPerDet(currentmean, self.collBunches)
            self.Detoccupancies[layer] = values["Occ"]
            self.hitPixPerDet[layer] = values["perMod"]
            self.hitPixPerDetArea[layer] = values["perArea"]
            self.hitPixPerDetAreaSec[layer] = values["perAreaSec"]
            ############################################################################################
            # Clusters per Layer
            currentmean = getHistoMean(self.file, "d/hclusPerLay"+str(ilayer+1))
            values = modules.measurement.getValuesPerLayer(currentmean, self.nWorkingModules[layer],self.collBunches, True)
            self.hitClusters[layer] = currentmean
            self.hitClustersPerModule[layer] = values["perMod"]
            self.hitClustersPerArea[layer] = values["perArea"]
            self.hitClustersPerAreaSec[layer] = values["perAreaSec"]
            # CLusters per Det
            currentmean = getHistoMean(self.file, "d/hclusPerDet"+str(ilayer+1))
            values = modules.measurement.getValuesPerDet(currentmean, self.collBunches, True)
            self.hitClustersPerDet[layer] = values["perMod"] #In this case: The mean given to the function
            self.hitClustersPerDetArea[layer] = values["perArea"]
            self.hitClustersPerDetAreaSec[layer] = values["perAreaSec"]

    def getzDependency(self):
        pass

    def getValuesasDict(self, valuetype):
        retdict = {"Pix/Lay" : None, "Pix/Det" : None, "Clus/Lay" : None, "Clus/Det" : None}
        if valuetype == "fullDetector":
            retdict["Pix/Lay"] = [self.hitPix, self.hitPixPerModule, self.hitPixPerArea,
                                  self.hitPixPerAreaSec, self.occupancies]
            retdict["Pix/Det"] = [None, self.hitPixPerDet, self.hitPixPerDetArea,
                                  self.hitPixPerDetAreaSec, self.Detoccupancies]
            retdict["Clus/Lay"] = [self.hitClusters, self.hitClustersPerModule,
                                   self.hitClustersPerArea , self.hitClustersPerAreaSec]
            retdict["Clus/Det"] = [None, self.hitClustersPerDet,
                                   self.hitClustersPerDetArea, self.hitClustersPerDetAreaSec]
        return retdict
    def getValuesasDetailDict(self, valuetype):
        retdict = {"Pix/Lay" : None, "Pix/Det" : None, "Clus/Lay" : None, "Clus/Det" : None}
        if valuetype == "fullDetector":
            retdict["Pix/Lay"] = {"perMod" : self.hitPixPerModule,
                                  "perArea" : self.hitPixPerArea,
                                  "perAreaSec" : self.hitPixPerAreaSec,
                                  "occupancy" : self.occupancies}
            retdict["Pix/Det"] = {"perMod" : self.hitPixPerDet,
                                  "perArea" : self.hitPixPerDetArea,
                                  "perAreaSec" : self.hitPixPerDetAreaSec,
                                  "occupancy" : self.Detoccupancies}
            retdict["Clus/Lay"] = {"perMod" : self.hitClustersPerModule,
                                   "perArea" : self.hitClustersPerArea,
                                   "perAreaSec" : self.hitClustersPerAreaSec}
            retdict["Clus/Det"] =  {"perMod" : self.hitClustersPerDet,
                                    "perArea" : self.hitClustersPerDetArea,
                                    "perAreaSec" : self.hitClustersPerDetAreaSec}
        return retdict

    def getValuesasDetailDict2(self, valuetype):
        retdict = self.getValuesasDetailDict(valuetype)
        if valuetype == "fullDetector":
            retdict["Pix/Lay"].update({"nhit" : self.hitPix})
            retdict["Pix/Det"].update({"nhit" : None})
            retdict["Clus/Lay"].update({"nhit" : self.hitClusters})
            retdict["Clus/Det"].update({"nhit" : None})
        return retdict

    def getValuesDetailDictperLayer(self, valuetype, layer = "Layer1"):
        retdict = {"Pix/Lay" : None, "Pix/Det" : None, "Clus/Lay" : None, "Clus/Det" : None}
        if valuetype == "fullDetector":
            retdict["Pix/Lay"] = {"perMod" : self.hitPixPerModule[layer],
                                  "nhit" : self.hitPix[layer],
                                  "perArea" : self.hitPixPerArea[layer],
                                  "perAreaSec" : self.hitPixPerAreaSec[layer],
                                  "occupancy" : self.occupancies[layer]}
            retdict["Pix/Det"] = {"perMod" : self.hitPixPerDet[layer],
                                  "perArea" : self.hitPixPerDetArea[layer],
                                  "perAreaSec" : self.hitPixPerDetAreaSec[layer],
                                  "occupancy" : self.Detoccupancies[layer]}
            retdict["Clus/Lay"] = {"perMod" : self.hitClustersPerModule[layer],
                                   "perArea" : self.hitClustersPerArea[layer],
                                   "nhit" : self.hitClusters[layer],
                                   "perAreaSec" : self.hitClustersPerAreaSec[layer]}
            retdict["Clus/Det"] =  {"perMod" : self.hitClustersPerDet[layer],
                                    "perArea" : self.hitClustersPerDetArea[layer],
                                    "perAreaSec" : self.hitClustersPerDetAreaSec[layer]}
        return retdict

    def getpdDataFrame(self, valuetype):
        import pandas as pd
        import numpy as np

        returndict = {}
        groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]
        subgroups = {"Pix/Lay" : ["nhit","perMod", "perArea", "perAreaSec", "occupancy"],
                     "Pix/Det" : ["nhit","perMod", "perArea", "perAreaSec", "occupancy"],
                     "Clus/Lay" : ["nhit","perMod", "perArea", "perAreaSec"],
                     "Clus/Det" : ["nhit","perMod", "perArea", "perAreaSec"]}
        valuedict = self.getValuesasDetailDict2(valuetype)
        if valuetype == "fullDetector":
            layerlist = self.LayerNames
            for group in groups:
                columns = pd.Series(subgroups[group])
                a = pd.DataFrame(valuedict[group], index = layerlist)
                a = a[subgroups[group]] #Sort columns by subgroup order
                a.fillna(value=np.nan, inplace=True)
                returndict[group] = copy(a)
        return returndict

    def printValues(self):
        """
        Print base values for debugging
        """
        for layer in self.LayerNames:
            print "-------- {0} --------".format(layer)
            print "nWorkingModules: {0}".format(self.nWorkingModules[layer])
            print "Pixels per Layer"
            print "  Pixels hit: {0}".format(self.hitPix[layer])
            print "  Occupancy: {0}".format(self.occupancies[layer])
            print "  Pixels hit per Module: {0}".format(self.hitPixPerModule[layer])
            print "  Pixels hit per Area: {0}".format(self.hitPixPerArea[layer])
            print "  Pixels hit per Area per sec: {0}".format(self.hitPixPerAreaSec[layer])
            print "Pixels per Det"
            print "  Occupancy (Det): {0}".format(self.Detoccupancies[layer])
            print "  Pixels hit per Det: {0}".format(self.hitPixPerDet[layer])
            print "  Pixels hit per DetArea: {0}".format(self.hitPixPerDetArea[layer])
            print "  Pixels hit per DetArea per sec: {0}".format(self.hitPixPerDetAreaSec[layer])
            print "Cluster per Layer"
            print "  Clusters hit: {0}".format(self.hitClusters[layer])
            print "  Clusters hit per module: {0}".format(self.hitClustersPerModule[layer])
            print "  Clusters hit per Area: {0}".format(self.hitClustersPerArea[layer])
            print "  Clusters hit per Area per sec: {0}".format(self.hitClustersPerAreaSec[layer])
            print "Clusters per Det"
            print "  Clusters hit per Det: {0}".format(self.hitClustersPerDet[layer])
            print "  Clusters hit per DetArea: {0}".format(self.hitClustersPerDetArea[layer])
            print "  Clusters hit per DetArea per sec: {0}".format(self.hitClustersPerDetAreaSec[layer])

def getHistoMean(inputfile, histoname):
    logging.debug("Getting mean form histogram: {0}".format(histoname))
    if isHistoinFile(inputfile, histoname):
        h = inputfile.Get(histoname)
        mean = h.GetMean()
        logging.debug("Mean of histogram {0} --> {1}".format(histoname, mean))
        if mean == 0:
            logging.waring("Mean of histogram {0} in file {1} is Zero! Please Check.".format(histoname, inputfile))
    else:
        mean = 0
        logging.error("Histogram not in file! Please check.")
    return mean
