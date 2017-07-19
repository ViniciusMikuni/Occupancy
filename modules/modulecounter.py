def modulecounter(inputfile):

    hpixdetMAPL1 = inputfile.Get("d/hpDetMap1")
    hpixdetMAPL2 = inputfile.Get("d/hpDetMap2")
    hpixdetMAPL3 = inputfile.Get("d/hpDetMap3")
    hpixdetMAPL4 = inputfile.Get("d/hpDetMap4")

    Histos2D = [hpixdetMAPL1, hpixdetMAPL2, hpixdetMAPL3, hpixdetMAPL4]

    workingmodules = {"Layer1": None, "Layer2": None, "Layer3": None, "Layer4": None}
    lnames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    for ih2D, h2D in enumerate(Histos2D):
        workingmodules[lnames[ih2D]] = getworkingmodulesfromHisto(h2D)

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
