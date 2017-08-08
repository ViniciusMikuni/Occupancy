"""
Classes for occupancy measurement

K. Schweiger, 2017
"""
import logging
import ROOT
from copy import copy
import os.path


from modules.modulecounter import modulecounter
from modules.tests import isHistoinFile
import modules.measurement
import modules.zdep
import modules.ladder

class container:
    """
    Container initialized for a run containing all claculations for the occupancy
    and related values.
    """
    def __init__(self, name, inputfile, collBunches, instLumi, comments = ["",""], nFiles = 1):
        logging.debug("Initializing container for {0} with inputfile {1} and colliding bunches {2}".format(name, inputfile, collBunches))
        self.LayerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
        self.zpositions = ["-4", "-3", "-2", "-1", "1", "2", "3", "4"]
        self.instLumi = instLumi * 1e30
        self.comments = comments
        self.name = name
        self.nFiles = nFiles
        self.invalidFile = False
        if not os.path.exists(inputfile.replace("~",os.path.expanduser("~"))):
            logging.error("File {0} does not exist. Run will be ignored".format(inputfile))
            self.invalidFile = True
        else:
            self.file = ROOT.TFile.Open(inputfile)
        self.collBunches = collBunches

        # Varaiable for full layer
        if not self.invalidFile:
            self.nWorkingModules = modulecounter(self.file)
        #Pixels
        self.hitPix = {}
        self.occupancies = {}
        self.hitPixPerModule = {}
        self.hitPixPerArea = {}
        self.hitPixPerAreaSec = {}
        self.hitPixPerAreaNorm = {}
        self.hitPixPerAreaSecNorm = {}

        self.Detoccupancies = {}
        self.hitPixPerDet = {}
        self.hitPixPerDetArea = {}
        self.hitPixPerDetAreaSec = {}
        self.hitPixPerDetAreaNorm = {}
        self.hitPixPerDetAreaSecNorm = {}
        # Clusters
        self.hitClusters = {}
        self.hitClustersPerModule = {}
        self.hitClustersPerArea = {}
        self.hitClustersPerAreaSec = {}
        self.hitClustersPerAreaNorm = {}
        self.hitClustersPerAreaSecNorm = {}

        self.hitClustersPerDet = {}
        self.hitClustersPerDetArea = {}
        self.hitClustersPerDetAreaSec = {}
        self.hitClustersPerDetAreaNorm = {}
        self.hitClustersPerDetAreaSecNorm = {}

        # Set general values
        if not self.invalidFile:
            self.setBaseValuesForallLayer()

        #Variables for z-dependency
        self.nWorkingModulesZ = {}
        #Pixels
        self.hitPixZ = {}
        self.occupanciesZ = {}
        self.hitPixPerModuleZ = {}
        self.hitPixPerAreaZ = {}
        self.hitPixPerAreaSecZ = {}
        self.hitPixPerAreaNormZ = {}
        self.hitPixPerAreaSecNormZ = {}

        # Set z-dependent values
        if not self.invalidFile:
            self.setzDependency()

        #Variable for inner/outer ladder dependency
        self.nWorkingModulesInOut = {}
        #Pixels
        self.hitPixInOut = {}
        self.occupanciesInOut = {}
        self.hitPixPerModuleInOut = {}
        self.hitPixPerAreaInOut = {}
        self.hitPixPerAreaSecInOut = {}
        self.hitPixPerAreaNormInOut = {}
        self.hitPixPerAreaSecNormInOut = {}

        # Set inner/outer ladder dependency values
        if not self.invalidFile:
            self.setInnerOuterLadderDependency()

        #TODO Implement: variables will have to be ordered differently because not all layer have the same
        #     number of ladder positions. Maybe fill with NaN or something. Will be added later.
        """
        #Variable for ladder dependency
        self.nWorkingModulesLadder = {}
        #Pixels
        self.hitPixLadder = {}
        self.occupanciesLadder = {}
        self.hitPixPerModuleLadder = {}
        self.hitPixPerAreaLadder = {}
        self.hitPixPerAreaSecLadder = {}
        self.hitPixPerAreaNormLadder = {}
        self.hitPixPerAreaSecNormLadder = {}

        # Set inner/outer ladder dependency values
        if not self.invalidFile:
            self.setLadderDependency()
        """

    def setBaseValuesForallLayer(self):
        """
        Calculate for each layer:
            * Occupancy (Only for pixels)
            * Pixel/Cluster hit per module
            * Pixel/Cluster hit per cm^2
            * Pixel/Cluster hit per cm^2 per sec
        """
        logging.info("Setting base values")
        for ilayer, layer in enumerate(self.LayerNames):
            logging.debug("Setting base values for {0}".format(layer))
            ############################################################################################
            # Pixels per Layer
            currentmean = getHistoMean(self.file, "d/hpixPerLay"+str(ilayer+1))
            self.hitPix[layer] = currentmean
            values = modules.measurement.getValuesPerLayer(currentmean, self.nWorkingModules[layer], self.collBunches, self.instLumi)
            self.occupancies[layer] = values["Occ"]
            self.hitPixPerModule[layer] = values["perMod"]
            self.hitPixPerArea[layer] = values["perArea"]
            self.hitPixPerAreaSec[layer] = values["perAreaSec"]
            self.hitPixPerAreaNorm[layer] = values["perAreaNorm"]
            self.hitPixPerAreaSecNorm[layer] = values["perAreaSecNorm"]
            # Pixels per Det
            currentmean = getHistoMean(self.file, "d/hpixPerDet"+str(ilayer+1))
            values = modules.measurement.getValuesPerDet(currentmean, self.collBunches, self.instLumi)
            self.Detoccupancies[layer] = values["Occ"]
            self.hitPixPerDet[layer] = values["perMod"]
            self.hitPixPerDetArea[layer] = values["perArea"]
            self.hitPixPerDetAreaSec[layer] = values["perAreaSec"]
            self.hitPixPerDetAreaNorm[layer] = values["perAreaNorm"]
            self.hitPixPerDetAreaSecNorm[layer] = values["perAreaSecNorm"]
            ############################################################################################
            # Clusters per Layer
            currentmean = getHistoMean(self.file, "d/hclusPerLay"+str(ilayer+1))
            values = modules.measurement.getValuesPerLayer(currentmean, self.nWorkingModules[layer],self.collBunches, self.instLumi,  True)
            self.hitClusters[layer] = currentmean
            self.hitClustersPerModule[layer] = values["perMod"]
            self.hitClustersPerArea[layer] = values["perArea"]
            self.hitClustersPerAreaSec[layer] = values["perAreaSec"]
            self.hitClustersPerAreaNorm[layer] = values["perAreaNorm"]
            self.hitClustersPerAreaSecNorm[layer] = values["perAreaSecNorm"]
            # CLusters per Det
            currentmean = getHistoMean(self.file, "d/hclusPerDet"+str(ilayer+1))
            values = modules.measurement.getValuesPerDet(currentmean, self.collBunches, self.instLumi, True)
            self.hitClustersPerDet[layer] = values["perMod"] #In this case: The mean given to the function
            self.hitClustersPerDetArea[layer] = values["perArea"]
            self.hitClustersPerDetAreaSec[layer] = values["perAreaSec"]
            self.hitClustersPerDetAreaNorm[layer] = values["perAreaNorm"]
            self.hitClustersPerDetAreaSecNorm[layer] = values["perAreaSecNorm"]

    def setzDependency(self):
        logging.info("Setting z-dependent values")
        nhitpixelsperZ, nworkingModulesperZ = modules.zdep.npixZdependency(self.file)
        self.nWorkingModulesZ = nworkingModulesperZ

        for pos in self.zpositions:
            self.hitPixZ[pos] = {}
            self.occupanciesZ[pos] = {}
            self.hitPixPerModuleZ[pos] = {}
            self.hitPixPerAreaZ[pos] = {}
            self.hitPixPerAreaSecZ[pos] = {}
            self.hitPixPerAreaNormZ[pos] = {}
            self.hitPixPerAreaSecNormZ[pos] = {}
            for layer in self.LayerNames:
                logging.debug("{0} - position {1}".format(layer, pos))
                values = modules.measurement.getValuesPerLayer(nhitpixelsperZ[layer][pos], nworkingModulesperZ[layer][pos], self.collBunches, self.instLumi)
                self.hitPixZ[pos][layer] = nhitpixelsperZ[layer][pos]
                self.occupanciesZ[pos][layer] = values["Occ"]
                self.hitPixPerModuleZ[pos][layer] = values["perMod"]
                self.hitPixPerAreaZ[pos][layer] = values["perArea"]
                self.hitPixPerAreaSecZ[pos][layer] = values["perAreaSec"]
                self.hitPixPerAreaNormZ[pos][layer]= values["perAreaNorm"]
                self.hitPixPerAreaSecNormZ[pos][layer]= values["perAreaSecNorm"]

        """
        Inverse structure. Maybe needed later at some point
        for layer in self.LayerNames:
            logging.debug("z-dependent values for {0}".format(layer))
            self.hitPixZ[layer] = {}
            self.occupanciesZ[layer] = {}
            self.hitPixPerModuleZ[layer] = {}
            self.hitPixPerAreaZ[layer] = {}
            self.hitPixPerAreaSecZ[layer] = {}
            self.hitPixPerAreaSecNormZ[layer] = {}
            for pos in self.zpositions:
                logging.debug("{0} - position {1}".format(layer, pos))
                values = modules.measurement.getValuesPerLayer(nhitpixelsperZ[layer][pos], nworkingModulesperZ[layer][pos], self.collBunches)
                self.hitPixZ[layer][pos] = nhitpixelsperZ[layer][pos]
                self.occupanciesZ[layer][pos] = values["Occ"]
                self.hitPixPerModuleZ[layer][pos] = values["perMod"]
                self.hitPixPerAreaZ[layer][pos] = values["perArea"]
                self.hitPixPerAreaSecZ[layer][pos] = values["perAreaSec"]
                self.hitPixPerAreaSecNormZ[layer][pos] = values["perAreaSecNorm"]
        """

    def setInnerOuterLadderDependency(self):
        logging.info("Setting innner/outer ladder dependent values")
        HitPixInOut = modules.ladder.getPixelHitsInOutladderModules(self.file, self.nFiles)
        self.nWorkingModulesInOut = modules.ladder.getworkingInOutladderModules(self.file)

        for ladder in ["inner","outer"]:
            self.hitPixInOut[ladder] = {}
            self.occupanciesInOut[ladder] = {}
            self.hitPixPerModuleInOut[ladder] = {}
            self.hitPixPerAreaInOut[ladder] = {}
            self.hitPixPerAreaSecInOut[ladder] = {}
            self.hitPixPerAreaNormInOut[ladder] = {}
            self.hitPixPerAreaSecNormInOut[ladder] = {}
            for layer in self.LayerNames:
                logging.debug("{0} - {1} ladder".format(layer, ladder))
                values = modules.measurement.getValuesPerLayer(HitPixInOut[layer][ladder], self.nWorkingModulesInOut[layer][ladder], self.collBunches, self.instLumi)
                self.hitPixInOut[ladder][layer] = HitPixInOut[layer][ladder]
                self.occupanciesInOut[ladder][layer] = values["Occ"]
                self.hitPixPerModuleInOut[ladder][layer] = values["perMod"]
                self.hitPixPerAreaInOut[ladder][layer] = values["perArea"]
                self.hitPixPerAreaSecInOut[ladder][layer] = values["perAreaSec"]
                self.hitPixPerAreaNormInOut[ladder][layer] = values["perAreaNorm"]
                self.hitPixPerAreaSecNormInOut[ladder][layer] = values["perAreaNorm"]

    def setLadderDependency(self):
        logging.info("Setting ladder dependent values")
        HitPixLadder = modules.ladder.getPixelHitsladderModules(self.file, self.nFiles)
        self.nWorkingModulesLadder = modules.ladder.getworkingladderModules(self.file)

        for layer in self.LayerNames:
            innerpositions = modules.ladder.getLadderidList(layer, "inner")
            outerpositions = modules.ladder.getLadderidList(layer, "outer")
            self.ladderpositions = innerpositions + outerpositions

        #TODO: Implement: See comment in init


    def getValuesasDict(self, valuetype):
        retdict = {"Pix/Lay" : None, "Pix/Det" : None, "Clus/Lay" : None, "Clus/Det" : None}
        if valuetype == "fullDetector":
            retdict["Pix/Lay"] = [self.hitPix, self.hitPixPerModule, self.hitPixPerArea,
                                  self.hitPixPerAreaSec,self.hitPixPerAreaNorm, self.occupancies]
            retdict["Pix/Det"] = [None, self.hitPixPerDet, self.hitPixPerDetArea,
                                  self.hitPixPerDetAreaSec,self.hitPixPerDetAreaNorm, self.Detoccupancies]
            retdict["Clus/Lay"] = [self.hitClusters, self.hitClustersPerModule,
                                   self.hitClustersPerArea, self.hitClustersPerAreaSec, self.hitClustersPerAreaNorm]
            retdict["Clus/Det"] = [None, self.hitClustersPerDet,
                                   self.hitClustersPerDetArea, self.hitClustersPerDetAreaSec, self.hitClustersPerDetAreaNorm]
        return retdict
    def getValuesasDetailDict(self, valuetype, part = None):
        retdict = {"Pix/Lay" : None, "Pix/Det" : None, "Clus/Lay" : None, "Clus/Det" : None}
        if valuetype == "fullDetector":
            retdict["Pix/Lay"] = {"perMod" : self.hitPixPerModule,
                                  "perArea" : self.hitPixPerArea,
                                  "perAreaSec" : self.hitPixPerAreaSec,
                                  "perAreaNorm" : self.hitPixPerAreaNorm,
                                  "occupancy" : self.occupancies}
            retdict["Pix/Det"] = {"perMod" : self.hitPixPerDet,
                                  "perArea" : self.hitPixPerDetArea,
                                  "perAreaSec" : self.hitPixPerDetAreaSec,
                                  "perAreaNorm" : self.hitPixPerDetAreaNorm,
                                  "occupancy" : self.Detoccupancies}
            retdict["Clus/Lay"] = {"perMod" : self.hitClustersPerModule,
                                   "perArea" : self.hitClustersPerArea,
                                   "perAreaSec" : self.hitClustersPerAreaSec,
                                   "perAreaNorm" : self.hitClustersPerAreaNorm}
            retdict["Clus/Det"] =  {"perMod" : self.hitClustersPerDet,
                                    "perArea" : self.hitClustersPerDetArea,
                                    "perAreaSec" : self.hitClustersPerDetAreaSec,
                                    "perAreaNorm" : self.hitClustersPerDetAreaNorm}
        elif valuetype == "partialDetectorZ":
            if part in self.zpositions:
                retdict["Pix/Lay"] = {"perMod" : self.hitPixPerModuleZ[part],
                                      "perArea" : self.hitPixPerAreaZ[part],
                                      "perAreaSec" : self.hitPixPerAreaSecZ[part],
                                      "perAreaNorm" : self.hitPixPerAreaNormZ[part],
                                      "occupancy" : self.occupanciesZ[part]}
                """
                Not implemented yet
                retdict["Pix/Det"] = {"perMod" : self.hitPixPerDetZ[part],
                                      "perArea" : self.hitPixPerDetAreaZ[part],
                                      "perAreaSec" : self.hitPixPerDetAreaSecZ[part],
                                      "perAreaSecNorm" : self.hitPixPerDetAreaSecNormZ[part],
                                      "occupancy" : self.Detoccupancies}
                retdict["Clus/Lay"] = {"perMod" : self.hitClustersPerModuleZ[part],
                                       "perArea" : self.hitClustersPerAreaZ[part],
                                       "perAreaSec" : self.hitClustersPerAreaSecZ[part],
                                       "perAreaSecNorm" : self.hitClustersPerAreaSecNormZ[part]}
                retdict["Clus/Det"] =  {"perMod" : self.hitClustersPerDetZ[part],
                                        "perArea" : self.hitClustersPerDetAreaZ[part],
                                        "perAreaSec" : self.hitClustersPerDetAreaSecZ[part],
                                        "perAreaSecNorm" : self.hitClustersPerDetAreaSecNormZ[part]}
                """
        elif valuetype == "partialDetectorLadder":
            if part in ["inner", "outer"]:
                retdict["Pix/Lay"] = {"perMod" : self.hitPixPerModuleInOut[part],
                                      "perArea" : self.hitPixPerAreaInOut[part],
                                      "perAreaSec" : self.hitPixPerAreaSecInOut[part],
                                      "perAreaNorm" : self.hitPixPerAreaNormInOut[part],
                                      "occupancy" : self.occupanciesInOut[part]}

        return retdict

    def getValuesasDetailDict2(self, valuetype, part = None):
        """
        Returns dictionary with values for Pix/Lay, Pix/Det, Clus/Lay, Clus/Det for each layer.
        If valuetype is not fullDetector it is parsed and if supported a dictionary with the same
        structure but with the defined criteria applied is returned.
        """
        retdict = None
        if valuetype == "fullDetector":
            retdict = self.getValuesasDetailDict(valuetype)
            retdict["Pix/Lay"].update({"nhit" : self.hitPix})
            retdict["Pix/Det"].update({"nhit" : None})
            retdict["Clus/Lay"].update({"nhit" : self.hitClusters})
            retdict["Clus/Det"].update({"nhit" : None})
        if valuetype.startswith("partialDetector"):
            if valuetype.startswith("partialDetectorZ"):
                position = part
                if position in self.zpositions:
                    retdict = self.getValuesasDetailDict("partialDetectorZ", position)
                    retdict["Pix/Lay"].update({"nhit" : self.hitPixZ[position]})
                    """
                    Not implemented yet
                    retdict["Pix/Det"].update({"nhit" : None})
                    retdict["Clus/Lay"].update({"nhit" : self.hitClusters})
                    retdict["Clus/Det"].update({"nhit" : None})
                    """
                else:
                    logging.warning("Valuetype {0} in no valid argument for z-dependent values".format(valuetype))
            elif valuetype.startswith("partialDetectorInnerOuterLadders"):
                position = part
                if position in ["inner", "outer"]:
                    retdict = self.getValuesasDetailDict("partialDetectorLadder", position)
                    retdict["Pix/Lay"].update({"nhit" : self.hitPixInOut[position]})
            elif valuetype.startswith("partialDetectorLadders"):
                #TODO. Implement: See comment in init
                pass

        return retdict

    def getValuesDetailDictperLayer(self, valuetype, layer = "Layer1"):
        retdict = {"Pix/Lay" : None, "Pix/Det" : None, "Clus/Lay" : None, "Clus/Det" : None}
        if valuetype == "fullDetector":
            retdict["Pix/Lay"] = {"perMod" : self.hitPixPerModule[layer],
                                  "nhit" : self.hitPix[layer],
                                  "perArea" : self.hitPixPerArea[layer],
                                  "perAreaSec" : self.hitPixPerAreaSec[layer],
                                  "perAreaNorm" : self.hitPixPerAreaNorm[layer],
                                  "occupancy" : self.occupancies[layer]}
            retdict["Pix/Det"] = {"perMod" : self.hitPixPerDet[layer],
                                  "perArea" : self.hitPixPerDetArea[layer],
                                  "perAreaSec" : self.hitPixPerDetAreaSec[layer],
                                  "perAreaNorm" : self.hitPixPerDetAreaNorm[layer],
                                  "occupancy" : self.Detoccupancies[layer]}
            retdict["Clus/Lay"] = {"perMod" : self.hitClustersPerModule[layer],
                                   "perArea" : self.hitClustersPerArea[layer],
                                   "nhit" : self.hitClusters[layer],
                                   "perAreaSec" : self.hitClustersPerAreaSec[layer],
                                   "perAreaNorm" : self.hitClustersPerAreaNorm[layer]}
            retdict["Clus/Det"] =  {"perMod" : self.hitClustersPerDet[layer],
                                    "perArea" : self.hitClustersPerDetArea[layer],
                                    "perAreaSec" : self.hitClustersPerDetAreaSec[layer],
                                    "perAreaNorm" : self.hitClustersPerDetAreaNorm[layer]}
        return retdict

    def getpdDataFrame(self, valuetype):
        logging.debug("Generating pandas DF with valuetype: {0}".format(valuetype))
        import pandas as pd
        import numpy as np

        groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]
        subgroups = {"Pix/Lay" : ["nhit","perMod", "perArea", "perAreaNorm", "perAreaSec", "occupancy"],
                     "Pix/Det" : ["nhit","perMod", "perArea", "perAreaNorm", "perAreaSec", "occupancy"],
                     "Clus/Lay" : ["nhit","perMod", "perArea", "perAreaNorm", "perAreaSec"],
                     "Clus/Det" : ["nhit","perMod", "perArea", "perAreaNorm", "perAreaSec"]}
        layerlist = self.LayerNames
        if valuetype == "fullDetector":
            returndict = {}
            valuedict = self.getValuesasDetailDict2(valuetype)
            for group in groups:
                if valuetype == "fullDetector":
                    a = pd.DataFrame(valuedict[group], index = layerlist)
                    a = a[subgroups[group]] #Sort columns by subgroup order
                    a.fillna(value=np.nan, inplace=True)
                    returndict[group] = copy(a)

        elif valuetype.startswith("partialDetectorZ"):
            returndict = {}
            #for group in groups:
            for group in ["Pix/Lay"]: #necessary fir current implementation of z-dependency
                mulitcolumnstuples = [(x,y) for x in self.zpositions for y in subgroups[group]]
                mulitcolumns = pd.MultiIndex.from_tuples(mulitcolumnstuples, names=['position', 'value'])
                a = pd.DataFrame(index = self.LayerNames, columns = mulitcolumns)
                for position in self.zpositions:
                    valuedict = self.getValuesasDetailDict2(valuetype, position)
                    a[position] = pd.DataFrame(valuedict[group], index = layerlist)
                returndict[group] = copy(a)

        elif valuetype.startswith("partialDetectorInnerOuterLadders"):
            returndict = {}
            for group in ["Pix/Lay"]:
                mulitcolumnstuples = [(x,y) for x in ["inner","outer"] for y in subgroups[group]]
                mulitcolumns = pd.MultiIndex.from_tuples(mulitcolumnstuples, names=['position', 'value'])
                a = pd.DataFrame(index = self.LayerNames, columns = mulitcolumns)
                for position in ["inner","outer"]:
                    valuedict = self.getValuesasDetailDict2(valuetype, position)
                    a[position] = pd.DataFrame(valuedict[group], index = layerlist)
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
