import logging

from modules.tests import isHistoinFile

def modulecounter(inputfile):
    logging.info("Counting working modules")
    nmodules =  {"Layer1": 96, "Layer2": 224, "Layer3": 352, "Layer4": 512}
    workingmodules = {"Layer1": None, "Layer2": None, "Layer3": None, "Layer4": None}
    lnames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    Histos2D = []
    for ilayer, layer in enumerate(lnames):
        currenthName = "d/hpDetMap{0}".format(ilayer+1)
        currenthName2 = "d/hpixDets{0}".format(ilayer+1)
        if isHistoinFile(inputfile, currenthName):
            Histos2D.append(inputfile.Get(currenthName))
        elif isHistoinFile(inputfile, currenthName2):
            Histos2D.append(inputfile.Get(currenthName2))
        else:
            logging.warning("Histo for {1} {0} or {2} not found. Will set modules to standard value!".format(currenthName,layer,currenthName2))
            Histos2D.append(None)

    for ih2D, h2D in enumerate(Histos2D):
        if h2D is not None:
            workingmodules[lnames[ih2D]] = getworkingmodulesfromHisto(h2D)
        else:
            workingmodules[lnames[ih2D]] = nmodules[lnames[ih2D]]
    return workingmodules


def getworkingmodulesfromHisto(hMap):
    nworkingModules = 0

    nbins = hMap.GetSize()
    for i in range(nbins):
        if hMap.GetBinContent(i) > 0:
            nworkingModules += 1

    return nworkingModules

def main():
    import ROOT

    tfile = ROOT.TFile.Open("~/Code/data/pixel/occupancy/Run298653_v3.root")

    print modulecounter(tfile)

if __name__ == "__main__":
    main()
