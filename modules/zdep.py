"""
Module for all function related to the z dependent values
"""
import logging

from modules.tests import isHistoinFile

def npixZdependency(inputfile, nFiles = 1):
    logging.debug("Getting pixel per event per zpositions and working modules")

    facets = [12, 28, 44, 64]
    zpositions = ["-4", "-3", "-2", "-1", "1", "2", "3", "4"]
    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    Histos2D = []
    for i in range(1,5):
        if isHistoinFile(inputfile, "d/hpDetMap{0}".format(i)):
            logging.debug("Using d/hpDetMap{0} for z dependent values".format(i))
            Histos2D.append(inputfile.Get("d/hpDetMap{0}".format(i)))
        elif isHistoinFile(inputfile, "d/hpixDets{0}".format(i)):
            logging.debug("Using d/hpixDets{0} for z dependent values".format(i))
            Histos2D.append(inputfile.Get("d/hpixDets{0}".format(i)))
        else:
            logging.error("Histo for Layer{0} d/hpDetMap{0} or d/hpixDets{0} not found. Final Fix not ready. Remove run from config!")
            exit()

    phitperzpositions = {"Layer1": None, "Layer2": None, "Layer3": None, "Layer4": None}
    workingmodules = {"Layer1": None, "Layer2": None, "Layer3": None, "Layer4": None}

    for ih2D, h2D in enumerate(Histos2D):
        zvalDict = {}
        zmoduleDict = {}
        for il, l in enumerate(zpositions):
            pixelperL = 0
            modulesworking = 0
            for iface in range(facets[ih2D]):
                # Ignore the "0" lines for facest and zpositions
                if iface < facets[ih2D]/2 and il <= 3:
                    x,y = 1,1
                elif iface >= facets[ih2D]/2 and il <= 3:
                    x,y = 1,2
                elif iface < facets[ih2D]/2 and il > 3:
                    x,y = 2,1
                else:
                    x,y = 2,2
                pixelperL += h2D.GetBinContent(x+il, y+iface) #h2D.GetBinContent(1,1) is lower left corner
                #print h2D.GetBinContent(x+il, y+iface)
                if h2D.GetBinContent(x+il, y+iface) > 0:
                    modulesworking += 1
            #print l,pixelperL
            zvalDict.update({l : pixelperL / nFiles})
            zmoduleDict.update({l : modulesworking})
        phitperzpositions[layerNames[ih2D]] = zvalDict
        workingmodules[layerNames[ih2D]] = zmoduleDict
    return phitperzpositions, workingmodules


def main():
    import ROOT

    tfile = ROOT.TFile.Open("~/Code/data/pixel/occupancy/v2/Run302742.root")

    hitpixelzdepDic, modules = npixZdependency(tfile)
    print hitpixelzdepDic
    print modules

    for layer in ["Layer1", "Layer2", "Layer3", "Layer4"]:
        print "---------------\n",layer
        layerinfo = hitpixelzdepDic[layer]
        modulesinfo = modules[layer]
        for pos in ["-4", "-3", "-2", "-1", "1", "2", "3", "4"][::-1]:
            s = layerinfo[pos]
            m = modulesinfo[pos]
            print pos,str(s).replace('.', ','),m #Only for german excel



if __name__ == "__main__":
    main()
