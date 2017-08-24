import os
import logging

from datetime import datetime
from collections import OrderedDict

import modules.pandasOutput
import modules.output


def makeFiles(titlestring, generaldescription, containerlist, runlist, foldername,
              makeIndex = True, makeTables = True, makePlotOverview = True, plottuples = None,
              fullperRunDF = None, fullRunCompDF = None, ZperRunDF = None, ZRunCompDF = None,
              LadderperRunDF = None, LadderRunCompDF = None, cfgname = None,
              linkTeX = False, linkCSV = False, linkCFG = False):
    """
    Wrapper for other function defined in this module.
    """
    from ConfigParser import SafeConfigParser
    logging.info("Generating HTML files")
    ####################################################################
    # General HTML headers
    styleconfig = SafeConfigParser()
    logging.debug("Loading style config")
    styleconfig.read("configs/style.cfg")

    header = "<!DOCTYPE html> \n <html> \n <body> \n"
    style = "<style> \n table, th, td {{\nborder: {0} solid black;\n border-collapse: collapse;\n}}\nth, td {{ padding: {1}; }}\n</style>\n".format(styleconfig.get("Tables","bordersize"),styleconfig.get("Tables","padding"))
    footnote = "<br><br><small>Generated: {0} by K. Schweiger, korbinian.schweiger@cern.ch</small>\n".format(datetime.now())
    footer = "</body> \n </html> \n"
    htmltemplatetuple = (header, style, footnote, footer)
    ####################################################################
    if makeTables:
        #Check if DFs are passed -> Used to speed up the script
        if fullperRunDF is None or fullRunCompDF is None or ZperRunDF is None or LadderperRunDF is None or LadderRunCompDF is None:
            DFstopass = None
        else:
            DFstopass = (fullperRunDF, fullRunCompDF, ZperRunDF, ZRunCompDF, LadderperRunDF, LadderRunCompDF)
        makeComparisonFiles(titlestring, generaldescription, containerlist, runlist, foldername,
                            htmltemplates = htmltemplatetuple, DFs = DFstopass, linkTeX = linkTeX, linkCSV = linkCSV, linkCFG = linkCFG)
    if makeIndex: #Make a landing page called index.html linking tables and plots (if passed as plottuples)
        makeLandingPage(titlestring, runlist, foldername, htmltemplatetuple, makePlotOverview, cfgname)
    if makePlotOverview:
        if plottuples is None:
            logging.error("No plotlists and names are given! No adding plots to index.")
        else:
            for plottuple in plottuples: #Go through all groups
                plotlist, group = plottuple
                makePlotOverviewFile(titlestring, generaldescription, plotlist, runlist, foldername, group)


def makeComparisonFiles(titlestring, generaldescription, containerlist, runlist, foldername,
                        singlerun = False, htmltemplates = None, DFs = None, linkTeX = False, linkCSV = False, linkCFG = False):
    logging.info("Processing runs and generate HTML files")
    from ConfigParser import SafeConfigParser
    styleconfig = SafeConfigParser()
    logging.debug("Loading style config")
    styleconfig.read("configs/style.cfg")

    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]

    if DFs is None:
        perRunTables, runcomparisonperLayer = modules.pandasOutput.makeFullDetectorTables(containerlist, runlist, singlerun)
    else:
        perRunTables, runcomparisonperLayer = DFs[0], DFs[1]

    if htmltemplates is None:
        header = "<!DOCTYPE html> \n <html> \n <body> \n"
        style = "<style> \n table, th, td {{\nborder: {0} solid black;\n border-collapse: collapse;\n}}\nth, td {{ padding: {1}; }}\n</style>\n".format(styleconfig.get("Tables","bordersize"),styleconfig.get("Tables","padding"))
        footnote = ""
        footer = "</body> \n </html> \n"
    else:
        header,style, footnote, footer = htmltemplates
    if foldername is not None:
        if not os.path.exists(foldername):
            logging.info("Creating folder: {0}".format(foldername))
            os.makedirs(foldername)

    logging.info("Comparison HTML tables and files")
    #HTML file with "Pix/Lay", "Pix/Det", "Clus/Lay" and "Clus/Det" tables for all layer and all processed run

    title = "<h1>{0}</h1>{1}\n".format(titlestring, generaldescription)
    blocks = []
    blocks.append(header)
    blocks.append(style)
    blocks.append(title)
    PerRunDFs = modules.output.makePerRunDFs(perRunTables, runlist, groups)
    for run in runlist:
        block = "<hr>\n<h2 id={4}>{0}</h2>\n{1} with average inst. luminosity: {2} cm^-2 s^-1<br>\nDataset: {3}<br>\n".format(run, containerlist[run].comments[0], containerlist[run].instLumi, containerlist[run].comments[1],run)
        block = block + "Working modules (from hpDetMap):<br>"
        for layer in layerNames:
            block = block + "{0}: {1} modules<br>".format(layer, containerlist[run].nWorkingModules[layer])
        for group in groups:
            block += "<h3>{0} ({1})    ".format(styleconfig.get("Renaming", group), group)
            if linkTeX:
                block += "<small><a href=tex/fullPerRun_{0}_{1}.txt>LaTeX</a></small> ".format(run, group.replace("/","per"))
            if linkCSV:
                block += "<small><a href=csv/fullPerRun_{0}_{1}.csv>CSV</a></small> ".format(run, group.replace("/","per"))
            if linkCFG:
                block += "<small><a href=cfg/fullPerRun_{0}_{1}.txt>CFG</a></small> ".format(run, group.replace("/","per"))
            block += "</h3>\n{0}".format(PerRunDFs["{0}_{1}".format(run, group)].to_html())
        blocks.append(block+"<br>\n")
    blocks.append(footnote)
    blocks.append(footer)
    modules.pandasOutput.writeListToFile(blocks, "{0}/perRunTables.html".format(foldername))
    #HTML file per Layer with comparisons for all processed runs for "Pix/Lay", "Pix/Det", "Clus/Lay" and "Clus/Det"
    if runcomparisonperLayer is not None:
        RunCompDFs = modules.output.makeRunCompDFs(runcomparisonperLayer, layerNames, groups)
        for layer in layerNames:
            blocks = []
            blocks.append(header)
            blocks.append(style)
            blocks.append(title)
            block = "<h2>Run comparion for {0}</h2>\n".format(layer)
            for group in groups:
                block = block + "<hr>\n<h3>{0} ({1})   ".format(styleconfig.get("Renaming", group), group)
                if linkTeX:
                    block += "<small><a href=tex/fullRunComp_{0}_{1}.txt>LaTeX</a></small> ".format(layer, group.replace("/","per"))
                if linkCSV:
                    block += "<small><a href=csv/fullRunComp_{0}_{1}.csv>CSV</a></small> ".format(layer, group.replace("/","per"))
                if linkCFG:
                    block += "<small><a href=cfg/fullRunComp_{0}_{1}.txt>CFG</a></small> ".format(layer, group.replace("/","per"))
                block += "</h3>\n{0}".format(RunCompDFs["{0}_{1}".format(layer, group)].to_html())
            blocks.append(block+"<br>\n")
            blocks.append(footnote)
            blocks.append(footer)
            modules.pandasOutput.writeListToFile(blocks, "{0}/runComparison{1}.html".format(foldername, layer))
    #HTML file per group with z-dependent values per layer
    #for group in groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]:
    if DFs is None:
        perRunTables = modules.pandasOutput.makeZdepDetectorTables(containerlist, runlist, singlerun)[0]
    else:
        perRunTables = DFs[2]

    perRunDFs = modules.output.makePerRunDFs(perRunTables, runlist, ["Pix/Lay"], layerNames)
    for group in ["Pix/Lay"]:
        blocks = []
        blocks.append(header)
        blocks.append(style)
        blocks.append("<h1>{0} - z-dependency</h1>{1}\n<br><b>{2} ({3})</b>".format(titlestring, generaldescription, styleconfig.get("Renaming", group), group))
        for run in runlist:
            block = "<hr>\n<h2 id={4}>{0}</h2>\n{1} with average inst. luminosity: {2} cm^-2 s^-1<br>\nDataset: {3}<br>\n".format(run, containerlist[run].comments[0], containerlist[run].instLumi, containerlist[run].comments[1], run)
            for layer in layerNames:
                block = block + "<h3>{0}    ".format(layer)
                if linkTeX:
                    block += "<small><a href=tex/zPerRun_{0}_{1}_{2}.txt>LaTeX</a></small> ".format(run, group.replace("/","per"), layer)
                if linkCSV:
                    block += "<small><a href=csv/zPerRun_{0}_{1}_{2}.csv>CSV</a></small> ".format(run, group.replace("/","per"), layer)
                if linkCFG:
                    block += "<small><a href=cfg/zPerRun_{0}_{1}_{2}.txt>CFG</a></small> ".format(run, group.replace("/","per"), layer)
                block += "</h3>\n{0}".format(perRunDFs["{0}_{1}_{2}".format(run, group, layer)].to_html())
            blocks.append(block+"<br>\n")
        blocks.append(footnote)
        blocks.append(footer)
        modules.pandasOutput.writeListToFile(blocks, "{0}/zDependency{1}.html".format(foldername, group.replace("/","per")))

    #HTML file per group for inner/outer ladder values per layer
    if DFs is None:
        perRunTables = modules.pandasOutput.makeInnerOuterLadderDetectorTables(containerlist, runlist, singlerun)[0]
    else:
        perRunTables = DFs[4]

    perRunDFs = modules.output.makePerRunDFs(perRunTables, runlist, ["Pix/Lay"], layerNames)
    for group in ["Pix/Lay"]:
        blocks = []
        blocks.append(header)
        blocks.append(style)
        blocks.append("<h1>{0} - Inner/Outer ladder dependency</h1>{1}\n<br><b>{2} ({3})</b>".format(titlestring, generaldescription, styleconfig.get("Renaming", group), group))
        for run in runlist:
            block = "<hr>\n<h2 id={4}>{0}</h2>\n{1} with average inst. luminosity: {2} cm^-2 s^-1<br>\nDataset: {3}<br>\n".format(run, containerlist[run].comments[0], containerlist[run].instLumi, containerlist[run].comments[1], run)
            for layer in layerNames:
                block = block + "<h3>{0}    ".format(layer)
                if linkTeX:
                    block += "<small><a href=tex/InOutPerRun_{0}_{1}_{2}.txt>LaTeX</a></small> ".format(run, group.replace("/","per"), layer)
                if linkCSV:
                    block += "<small><a href=csv/InOutPerRun_{0}_{1}_{2}.csv>CSV</a></small> ".format(run, group.replace("/","per"), layer)
                if linkCFG:
                    block += "<small><a href=cfg/InOutPerRun_{0}_{1}_{2}.txt>CFG</a></small> ".format(run, group.replace("/","per"), layer)
                block += "</h3>\n{0}".format(perRunDFs["{0}_{1}_{2}".format(run, group, layer)].to_html())
            blocks.append(block+"<br>\n")
        blocks.append(footnote)
        blocks.append(footer)
        modules.pandasOutput.writeListToFile(blocks, "{0}/InnerOuterLadderDependency{1}.html".format(foldername, group.replace("/","per")))

    if DFs is None:
        RunCompDFs = modules.pandasOutput.makeInnerOuterLadderDetectorTables(containerlist, runlist, singlerun)[1]
    else:
        RunCompDFs = DFs[5]

    if RunCompDFs is not None:
        RunCompDFs = modules.output.makeRunCompDFs(RunCompDFs, layerNames, ["Pix/Lay"], ["inner", "outer"])

        for layer in layerNames:
            for ladder in ["inner", "outer"]:
                blocks = []
                blocks.append(header)
                blocks.append(style)
                blocks.append("<h1>Run comparison for {0} modules on {1}</h1>".format(ladder, layer))
                block = ""
                for group in ["Pix/Lay"]:
                    block += "<h2>{0} ({1})    ".format(styleconfig.get("Renaming", group), group)
                    if linkTeX:
                        block += "<small><a href=tex/partialRunComp_{0}_{1}_{2}.txt>LaTeX</a></small> ".format(layer, group.replace("/","per"), ladder)
                    if linkCSV:
                        block += "<small><a href=csv/partialRunComp_{0}_{1}_{2}.csv>CSV</a></small> ".format(layer, group.replace("/","per"), ladder)
                    if linkCFG:
                        block += "<small><a href=cfg/partialRunComp_{0}_{1}_{2}.txt>CFG</a></small> ".format(layer, group.replace("/","per"), ladder)
                    block += "</h3>\n{0}\n".format(RunCompDFs["{0}_{1}_{2}".format(layer, group, ladder)].to_html())
                blocks.append(block+"<br>\n")
                blocks.append(footnote)
                blocks.append(footer)
                modules.pandasOutput.writeListToFile(blocks, "{0}/runComparison{1}_{2}.html".format(foldername, layer, ladder))



def makePlotOverviewFile(titlestring, generaldescription, generatedplots, runlist, foldername, midfix = "Pix/Lay"):
    """
    Make overview page (subpages) for plot generated with modules.pandasOutput.makeRunComparisonPlots.

    Uses keywords which are expected in the filename. Currently implemented 'RunComp' and [runnumbers].
    For RunComp the keywords Layer[X] and allLayers are grouped.
    """
    if not os.path.exists(foldername):
        logging.info("Creating folder: {0}".format(foldername))
        os.makedirs(foldername)

    logging.info("Generating HTML plot overview files")
    header = "<!DOCTYPE html> \n <html> \n <body> \n"
    title = "<h1>{0}</h1>{1}\n".format(titlestring, generaldescription)
    footer = "</body> \n </html> \n"
    footnote = "<br><br><small>Generated: {0} by K. Schweiger, korbinian.schweiger@cern.ch</small>\n".format(datetime.now())
    #Single Runs
    blocks = []
    blocks.append(header)
    blocks.append(title)
    blocks.append("<h2>Comparison of rate and occupancy of all layer for each processed run</h2>\n")
    runsadded = 0
    for run in runlist:
        runblock = []
        nfiles = 0
        runblock.append("<hr>\n<h3 id={1}>{0}</h3>\n".format(run, run))
        for plot in generatedplots:
            filename = plot.split("/")[-1].split(".")[0]
            if run in filename:
                nfiles += 1
                runblock.append('<img src="{0}" alt="{0}" style="width:800px;height:600px;">\n'.format(plot[len(foldername)+1::]))
        if nfiles > 0:
            blocks = blocks + runblock
            runsadded += 1
    blocks.append(footnote)
    blocks.append(footer)
    if runsadded > 0:
        modules.pandasOutput.writeListToFile(blocks, "{0}/plots_{1}_perRun.html".format(foldername, midfix.replace("/","per")))
    logging.info("Saved: {0}/plots_{1}_perRun.html".format(foldername, midfix.replace("/","per")))

    blocks = []
    blocks.append(header)
    blocks.append(title)
    blocks.append("<h2>Run comparison</h2>\n")
    blocks.append("<hr>\n<h3 id=allLayers>Plots for all layers</h3>\n")
    for plot in generatedplots:
        filename = plot.split("/")[-1].split(".")[0]
        if "allLayers" in filename and not("inner" in filename or "outer" in filename):
            blocks.append('<img src="{0}" alt="{0}" style="width:800px;height:600px;">\n'.format(plot[len(foldername)+1::]))
    for layer in ["Layer1", "Layer2", "Layer3", "Layer4"]:
        blocks.append("<hr>\n<h3 id={0}>Plots for {0}</h3>\n".format(layer))
        for plot in generatedplots:
            filename = plot.split("/")[-1].split(".")[0]
            if layer in filename and not "InnerVsOuter" in filename:
                blocks.append('<img src="{0}" alt="{0}" style="width:800px;height:600px;">\n'.format(plot[len(foldername)+1::]))
    blocks.append(footnote)
    blocks.append(footer)
    modules.pandasOutput.writeListToFile(blocks, "{0}/plots_{1}_runComp.html".format(foldername, midfix.replace("/","per")))
    logging.info("Saved: {0}/plots_{1}_runComp.html".format(foldername, midfix.replace("/","per")))

    if midfix == "Pix/Lay":
        #Inner/outer comparisons per layer
        blocks = []
        blocks.append(header)
        blocks.append(title)
        blocks.append("<h2>Run comparison - Inner/outer ladder dependency</h2>\n")
        for layer in ["Layer1", "Layer2", "Layer3", "Layer4"]:
            blocks.append("<hr>\n<h3 id={0}>Plots for {0}</h3>\n".format(layer))
            for plot in generatedplots:
                filename = plot.split("/")[-1].split(".")[0]
                if "InnerVsOuter" in filename and layer in filename:
                    blocks.append('<img src="{0}" alt="{0}" style="width:800px;height:600px;">\n'.format(plot[len(foldername)+1::]))
        blocks.append(footnote)
        blocks.append(footer)
        modules.pandasOutput.writeListToFile(blocks, "{0}/plots_{1}_InnerVsOuterRunComp.html".format(foldername, midfix.replace("/","per")))
        logging.info("Saved: {0}/plots_{1}_InnerVsOuterRunComp.html".format(foldername, midfix.replace("/","per")))

        #Comparsion of layer for inner and outer modules
        blocks = []
        blocks.append(header)
        blocks.append(title)
        blocks.append("<h2>Run comparison - Inner/outer ladder dependency</h2>\n")
        for ladder in ["inner","outer"]:
            blocks.append("<hr>\n<h3 id={0}>Plots for {0} modules</h3>\n".format(ladder))
            for plot in generatedplots:
                filename = plot.split("/")[-1].split(".")[0]
                if filename.startswith("{0}RunComp".format(ladder)):
                    blocks.append('<img src="{0}" alt="{0}" style="width:800px;height:600px;">\n'.format(plot[len(foldername)+1::]))
        blocks.append(footnote)
        blocks.append(footer)
        modules.pandasOutput.writeListToFile(blocks, "{0}/plots_{1}_InnerOuterLadderRunComp.html".format(foldername, midfix.replace("/","per")))
        logging.info("Saved: {0}/plots_{1}_InnerOuterLadderRunComp.html".format(foldername, midfix.replace("/","per")))

def makeLandingPage(titlestring, runlist, foldername, htmltemplates, plotsgenerated = True, cfgname = None):

    header, style, footnote, footer = htmltemplates
    title = "<h1>{0}</h1>\n Codebase and instructions on <a href=https://github.com/kschweiger/Occupancy>GitHub</a> <br> \nClick <a href={1}>here</a> to view the configuration file.".format(titlestring, cfgname)
    blocks = []
    blocks.append(header)
    blocks.append(style)
    blocks.append(title)
    subheaderperRun = "<h2> Per run monitoring</h2>\n"
    fullDettableref = "Full Detector: Tabels for runs: "
    zDeptableref = "<br>Z-depencdency: Tabels for runs: "
    InOutDeptableref = "<br>Inner/Outer ladder dependency: Tables for runs: "
    zDepPlotref = "<br><br>Z-depencdency: Plots for runs: "
    for run in runlist:
        fullDettableref += "<a href=perRunTables.html#{0}>{1}</a> ".format(run, run)
        zDeptableref += "<a href=zDependencyPixperLay.html#{0}>{1}</a> ".format(run, run)
        InOutDeptableref += "<a href=InnerOuterLadderDependencyPixperLay.html#{0}>{1}</a> ".format(run, run)
        if plotsgenerated:
            zDepPlotref += "<a href=plots_PixperLay_perRun.html#{0}>{1}</a> ".format(run, run)
    fullDettableref += "\n"
    zDeptableref += "(calculated from pixels hit per layer)\n"
    if plotsgenerated:
        zDepPlotref += "(calculated from pixels hit per layer)\n"
    blocks.append(subheaderperRun)
    blocks.append(fullDettableref)
    blocks.append(zDeptableref)
    blocks.append(InOutDeptableref)
    if plotsgenerated:
        blocks.append(zDepPlotref)

    subheaderRunComp = "<h2>Run comparion</h2>\n"
    fullDettablerefcomp = "Full detector: Tables for: <a href=runComparisonLayer1.html>Layer 1</a> <a href=runComparisonLayer2.html>Layer 2</a> <a href=runComparisonLayer3.html>Layer 3</a> <a href=runComparisonLayer4.html>Layer 4</a><br> \n"
    innerLaddertablerefcomp = "Modules on inner Ladder: Tables for <a href=runComparisonLayer1_inner.html>Layer 1</a> <a href=runComparisonLayer2_inner.html>Layer 2</a> <a href=runComparisonLayer3_inner.html>Layer 3</a> <a href=runComparisonLayer4_inner.html>Layer 4</a><br> \n"
    outerLaddertablerefcomp = "Modules on outer Ladder: Tables for <a href=runComparisonLayer1_outer.html>Layer 1</a> <a href=runComparisonLayer2_outer.html>Layer 2</a> <a href=runComparisonLayer3_outer.html>Layer 3</a> <a href=runComparisonLayer4_outer.html>Layer 4</a><br> \n"
    if plotsgenerated:
        fullDetplotPixPerLayrefcomp = "<br>Full detector: Plots for <a href=plots_PixperLay_runComp.html#allLayers>all Layers</a>, <a href=plots_PixperLay_runComp.html#Layer1>Layer 1</a>, <a href=plots_PixperLay_runComp.html#Layer2>Layer 2</a>, <a href=plots_PixperLay_runComp.html#Layer3>Layer 3</a>, <a href=plots_PixperLay_runComp.html#Layer4>Layer 4</a> (calculated from <mark>pixels hit per layer</mark>)<br>\n"
        fullDetplotPixPerDetrefcomp = "Full detector: Plots for <a href=plots_PixperDet_runComp.html#allLayers>all Layers</a>, <a href=plots_PixperDet_runComp.html#Layer1>Layer 1</a>, <a href=plots_PixperDet_runComp.html#Layer2>Layer 2</a>, <a href=plots_PixperDet_runComp.html#Layer3>Layer 3</a>, <a href=plots_PixperDet_runComp.html#Layer4>Layer 4</a> (calculated from <mark>pixels hit per det</mark>)<br>\n"
        fullDetplotClusPerLayrefcomp = "Full detector: Plots for <a href=plots_ClusperLay_runComp.html#allLayers>all Layers</a>, <a href=plots_ClusperLay_runComp.html#Layer1>Layer 1</a>, <a href=plots_ClusperLay_runComp.html#Layer2>Layer 2</a>, <a href=plots_ClusperLay_runComp.html#Layer3>Layer 3</a>, <a href=plots_ClusperLay_runComp.html#Layer4>Layer 4</a> (calculated from <mark>clusters hit per layer</mark>)<br>\n"
        fullDetplotClusPerDetrefcomp = "Full detector: Plots for <a href=plots_ClusperDet_runComp.html#allLayers>all Layers</a>, <a href=plots_ClusperDet_runComp.html#Layer1>Layer 1</a>, <a href=plots_ClusperDet_runComp.html#Layer2>Layer 2</a>, <a href=plots_ClusperDet_runComp.html#Layer3>Layer 3</a>, <a href=plots_ClusperDet_runComp.html#Layer4>Layer 4</a> (calculated from <mark>clusters hit per det</mark>)<br>\n"
        Laddertablerefcompplots = "Comparison inner and outer ladder: Plots for <a href=plots_PixperLay_InnerVsOuterRunComp.html#Layer1>Layer 1</a>, <a href=plots_PixperLay_InnerVsOuterRunComp.html#Layer2>Layer 2</a>, <a href=plots_PixperLay_InnerVsOuterRunComp.html#Layer3>Layer 3</a>, <a href=plots_PixperLay_InnerVsOuterRunComp.html#Layer4>Layer 4</a> (calculated from <mark>pixels hit per layer</mark>)<br>\n"
        Laddertablerefcompplots2 = "Comparison inner and outer ladder: Plots for <a href=plots_PixperLay_InnerOuterLadderRunComp.html#inner>Inner modules</a>, <a href=plots_PixperLay_InnerOuterLadderRunComp.html#outer>Outer modules</a>(calculated from <mark>pixels hit per layer</mark>)<br>\n"
    blocks.append(subheaderRunComp)
    blocks.append(fullDettablerefcomp)
    blocks.append(innerLaddertablerefcomp)
    blocks.append(outerLaddertablerefcomp)
    if plotsgenerated:
        blocks.append(fullDetplotPixPerLayrefcomp)
        blocks.append(fullDetplotPixPerDetrefcomp)
        blocks.append(fullDetplotClusPerLayrefcomp)
        blocks.append(fullDetplotClusPerDetrefcomp)
        blocks.append(Laddertablerefcompplots)
        blocks.append(Laddertablerefcompplots2)
    blocks.append(footnote)
    blocks.append(footer)
    modules.pandasOutput.writeListToFile(blocks, "{0}/index.html".format(foldername))
