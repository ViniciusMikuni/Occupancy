def npixZdependency(inputfile):

    print "Getting pixel per event per ladder"

    facets = [12, 28, 44, 64]
    ladder = ["-4", "-3", "-2", "-1", "1", "2", "3", "4"]
    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    hpixdetMAPL1 = inputfile.Get("d/hpDetMap1")
    hpixdetMAPL2 = inputfile.Get("d/hpDetMap2")
    hpixdetMAPL3 = inputfile.Get("d/hpDetMap3")
    hpixdetMAPL4 = inputfile.Get("d/hpDetMap4")

    Histos2D = [hpixdetMAPL1, hpixdetMAPL2, hpixdetMAPL3, hpixdetMAPL4]

    phitperladder = {"Layer1": None, "Layer2": None, "Layer3": None, "Layer4": None}

    for ih2D, h2D in enumerate(Histos2D):
        zvalDic = {}
        for il, l in enumerate(ladder):
            pixelperL = 0
            for iface in range(facets[ih2D]):
                # Ignore the "0" lines for facest and ladder
                if iface < facets[ih2D]/2 and il <= 3:
                    x,y = 1,1
                elif iface >= facets[ih2D]/2 and il <= 3:
                    x,y = 1,2
                elif iface < facets[ih2D]/2 and il > 3:
                    x,y = 2,1
                else:
                    x,y = 2,2
                pixelperL += h2D.GetBinContent(x+il, y+iface) #h2D.GetBinContent(1,1) is lower left corner
                #print "Events -> x: {0} | y: {1} ===> {2}".format(x+il, y+iface, pixelperL)
            zvalDic.update({l : pixelperL})
        #print zvalDic
        phitperladder[layerNames[ih2D]] = zvalDic
    return phitperladder


def main():
    import ROOT

    tfile = ROOT.TFile.Open("~/Code/data/pixel/occupancy/Run298653_v3.root")

    hitpixelzdepDic = npixZdependency(tfile)
    print hitpixelzdepDic

    for layer in ["Layer1", "Layer2", "Layer3", "Layer4"]:
        print "---------------\n",layer
        layerinfo = hitpixelzdepDic[layer]
        for pos in ["-4", "-3", "-2", "-1", "1", "2", "3", "4"][::-1]:
            s = layerinfo[pos]
            print str(s).replace('.', ',') #Only for german excel



if __name__ == "__main__":
    main()
