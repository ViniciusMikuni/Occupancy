import logging

def getLadderidList(layer, position = "inner"):
    ret = False
    if layer not in ["Layer1","Layer2","Layer3","Layer4"]:
        logging.error("Passed layer not in Layer1, Layer2, Layer3, Layer4")
        ret = None
    if position not in ["inner", "outer"]:
        logging.error("Passed position neither inner nor outer")
        ret = None

    if layer == "Layer1":
        if position == "inner":
            ret = ["-5","-3","-1",
                   "2","4","6"]
        else:
            ret = ["-6","-4","-2",
                   "1","3","5"]
    elif layer == "Layer2":
        if position == "inner":
            ret = ["-13","-11","-9","-7","-5","-3","-1",
                   "2","4","6","8","10","12","14"]
        else:
            ret = ["-14","-12","-10","-8","-6","-4","-2",
                   "1","3","5","7","9","11","13"]
    elif layer == "Layer3":
        if position == "inner":
            ret = ["-21","-19","-17","-15","-13","-11","-9","-7","-5","-3","-1",
                   "2","4","6","8","10","12","14","16","18","20","22"]
        else:
            ret = ["-22","-20","-18","-16","-14","-12","-10","-8","-6","-4","-2",
                   "1","3","5","7","9","11","13","15","17","19","21"]
    elif layer == "Layer4":
        if position == "inner":
            ret = ["-31","-29","-27","-25","-23","-21","-19","-17","-15","-13","-11","-9","-7","-5","-3","-1",
                   "2","4","6","8","10","12","14","16","18","20","22","24","26","28","30","32"]
        else:
            ret = ["-32","-30","-28","-26","-24","-22","-20","-18","-16","-14","-12","-10","-8","-6","-4","-2",
                   "1","3","5","7","9","11","13","15","17","19","21","23","25","27","29","31"]
    return ret

def getworkingInOutladderModules(inputfile):
    logging.info("Getting working modules for inner and outer ladder of all layers")
    logging.debug("Using histograms from inputfile {0}".format(inputfile))

    workingmodulesperpositon =  getworkingladderModules(inputfile)

    workingmodules = {"Layer1": {}, "Layer2": {}, "Layer3": {}, "Layer4": {}}

    for ilayer, layer in enumerate(["Layer1","Layer2","Layer3","Layer4"]):
        workingmodules[layer]["inner"] = 0
        workingmodules[layer]["outer"] = 0
        for ladder in ["inner","outer"]:
            logging.debug("Getting number of working modules in {0}, {1} ladder".format(layer, ladder))
            for module in getLadderidList(layer, ladder):
                workingmodules[layer][ladder] += workingmodulesperpositon[layer][module]

    return workingmodules

def getworkingladderModules(inputfile):
    logging.info("Getting working modules per ladder position")
    logging.debug("Using histograms from inputfile {0}".format(inputfile))
    facets = [12, 28, 44, 64]
    zbins = [1,2,3,4,6,7,8,9]

    hpixdetMAPL1 = inputfile.Get("d/hpDetMap1")
    hpixdetMAPL2 = inputfile.Get("d/hpDetMap2")
    hpixdetMAPL3 = inputfile.Get("d/hpDetMap3")
    hpixdetMAPL4 = inputfile.Get("d/hpDetMap4")

    Histos2D = [hpixdetMAPL1, hpixdetMAPL2, hpixdetMAPL3, hpixdetMAPL4]

    workingmodules = {"Layer1": {}, "Layer2": {}, "Layer3": {}, "Layer4": {}}

    for ilayer, layer in enumerate(["Layer1","Layer2","Layer3","Layer4"]):
        h2D = Histos2D[ilayer]
        ladderZero = (facets[ilayer]/2)+1
        for ladder in ["inner","outer"]:
            for module in getLadderidList(layer, ladder):
                workingmodules[layer][module] = 0
                for z in zbins:
                    if h2D.GetBinContent(z,ladderZero+int(module)) > 0:
                        workingmodules[layer][module] += 1

    return workingmodules

def getPixelHitsladderModules(inputfile, nfiles):
    logging.debug("Getting pixel hits per ladder position")
    facets = [12, 28, 44, 64]

    hpladder1 = inputfile.Get("d/hpladder1id")
    hpladder2 = inputfile.Get("d/hpladder2id")
    hpladder3 = inputfile.Get("d/hpladder3id")
    hpladder4 = inputfile.Get("d/hpladder4id")

    hPixHits = [hpladder1, hpladder2, hpladder3, hpladder4]

    pixelHits = {"Layer1": {}, "Layer2": {}, "Layer3": {}, "Layer4": {}}

    for ilayer, layer in enumerate(["Layer1","Layer2","Layer3","Layer4"]):
        histo = hPixHits[ilayer]
        ladderZero = (facets[ilayer]/2)+1
        for ladder in ["inner","outer"]:
            for module in getLadderidList(layer, ladder):
                pixelHits[layer][module] = histo.GetBinContent(ladderZero+int(module)) / float(nfiles)

    return pixelHits

def getPixelHitsInOutladderModules(inputfile, nfiles):
    logging.debug("Getting pixel hits for inner and outer ladders")

    pixelhitspermodule = getPixelHitsladderModules(inputfile, nfiles)

    pixelHits = {"Layer1": {}, "Layer2": {}, "Layer3": {}, "Layer4": {}}

    for ilayer, layer in enumerate(["Layer1","Layer2","Layer3","Layer4"]):
        pixelHits[layer]["inner"] = 0
        pixelHits[layer]["outer"] = 0
        for ladder in ["inner","outer"]:
            logging.debug("Getting pixel hits in {0}, {1} ladder".format(layer, ladder))
            for module in getLadderidList(layer, ladder):
                pixelHits[layer][ladder] += pixelhitspermodule[layer][module]

    return pixelHits
