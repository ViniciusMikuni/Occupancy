import os
import logging

import modules.pandasOutput

def makeComparisonFiles(titlestring, generaldescription, containerlist, runlist, foldername, singlerun = False):
    logging.info("Processing runs and generate HTML files")
    from ConfigParser import SafeConfigParser
    styleconfig = SafeConfigParser()
    logging.debug("Loading style config")
    styleconfig.read("configs/style.cfg")

    layerNames = ["Layer1", "Layer2", "Layer3", "Layer4"]
    groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]

    perRunTables, runcomparisonperLayer = modules.pandasOutput.makeFullDetectorTables(containerlist, runlist, singlerun)

    if not os.path.exists(foldername):
        logging.info("Creating folder: {0}".format(foldername))
        os.makedirs(foldername)

    logging.info("Generating HTML files")
    #HTML file with "Pix/Lay", "Pix/Det", "Clus/Lay" and "Clus/Det" tables for all layer and all processed run
    header = "<!DOCTYPE html> \n <html> \n <body> \n"
    style = "<style> \n table, th, td {{\nborder: {0} solid black;\n border-collapse: collapse;\n}}\nth, td {{ padding: {1}; }}\n</style>\n".format(styleconfig.get("Tables","bordersize"),styleconfig.get("Tables","padding"))
    title = "<h1>{0}</h1>{1}\n".format(titlestring, generaldescription)
    blocks = []
    blocks.append(header)
    blocks.append(style)
    blocks.append(title)
    for run in runlist:
        block = "<hr>\n<h2>{0}</h2>\n{1} with average inst. luminosity: {2} cm^-2 s^-1<br>\nDataset: {3}<br>\n".format(run, containerlist[run].comments[0], containerlist[run].instLumi, containerlist[run].comments[1])
        block = block + "Working modules (from hpDetMap):<br>"
        for layer in layerNames:
            block = block + "{0}: {1} modules<br>".format(layer, containerlist[run].nWorkingModules[layer])
        for group in groups:
            block = block + "<h3>{0} ({1})</h3>\n{2}".format(styleconfig.get("Renaming", group), group, perRunTables[run][group].to_html())
        blocks.append(block+"<br>\n")
    footer = "</body> \n </html> \n"
    blocks.append(footer)
    modules.pandasOutput.writeListToFile(blocks, "{0}/perRunTables.html".format(foldername))
    #HTML file per Layer with comparisons for all processed runs for "Pix/Lay", "Pix/Det", "Clus/Lay" and "Clus/Det"
    if runcomparisonperLayer is not None:
        for layer in layerNames:
            blocks = []
            blocks.append(header)
            blocks.append(style)
            blocks.append(title)
            block = "<h2>Run comparion for {0}</h2>\n".format(layer)
            for group in groups:
                block = block + "<hr>\n<h3>{0} ({1})</h3>\n{2}".format(styleconfig.get("Renaming", group), group, runcomparisonperLayer[layer][group].to_html())
            blocks.append(block+"<br>\n")
            blocks.append(footer)
            modules.pandasOutput.writeListToFile(blocks, "{0}/runComparison{1}.html".format(foldername, layer))
    #HTML file per group with z-dependent values per layer
    #for group in groups = ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]:
    perRunTables = modules.pandasOutput.makeZdepDetectorTables(containerlist, runlist, singlerun)[0]
    for group in ["Pix/Lay"]:
        blocks = []
        blocks.append(header)
        blocks.append(style)
        blocks.append("<h1>{0} - z-dependency</h1>{1}\n<br><b>{2} ({3})</b>".format(titlestring, generaldescription, styleconfig.get("Renaming", group), group))
        for run in runlist:
            block = "<hr>\n<h2>{0}</h2>\n{1} with average inst. luminosity: {2} cm^-2 s^-1<br>\nDataset: {3}<br>\n".format(run, containerlist[run].comments[0], containerlist[run].instLumi, containerlist[run].comments[1])
            for layer in layerNames:
                block = block + "<h3>{0}</h3>\n{1}".format(layer, perRunTables[run][group][layer].to_html())
            blocks.append(block+"<br>\n")
            blocks.append(footer)
            modules.pandasOutput.writeListToFile(blocks, "{0}/zDependency{1}.html".format(foldername, group.replace("/","per")))



def makePlotOverviewFile(titlestring, generaldescription, generatedplots, runlist, foldername):
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
    #Single Runs
    blocks = []
    blocks.append(header)
    blocks.append(title)
    blocks.append("<h2>Comparison of rate and occupancy of all layer for each processed run</h2>\n")
    for run in runlist:
        blocks.append("<hr>\n<h3>{0}</h3>\n".format(run))
        for plot in generatedplots:
            filename = plot.split("/")[-1].split(".")[0]
            if run.split(" ")[1] in filename:
                blocks.append('<img src="{0}" alt="{0}" style="width:800px;height:600px;">\n'.format(plot[len(foldername)+1::]))
    blocks.append(footer)
    modules.pandasOutput.writeListToFile(blocks, "{0}/plots_perRun.html".format(foldername))

    blocks = []
    blocks.append(header)
    blocks.append(title)
    blocks.append("<h2>Run comparison</h2>\n")
    blocks.append("<hr>\n<h3>Plots for all layers</h3>\n")
    for plot in generatedplots:
        filename = plot.split("/")[-1].split(".")[0]
        if "allLayers" in filename:
            blocks.append('<img src="{0}" alt="{0}" style="width:800px;height:600px;">\n'.format(plot[len(foldername)+1::]))
    for layer in ["Layer1", "Layer2", "Layer3", "Layer4"]:
        blocks.append("<hr>\n<h3>Plots for {0}</h3>\n".format(layer))
        for plot in generatedplots:
            filename = plot.split("/")[-1].split(".")[0]
            if layer in filename:
                blocks.append('<img src="{0}" alt="{0}" style="width:800px;height:600px;">\n'.format(plot[len(foldername)+1::]))
    blocks.append(footer)
    modules.pandasOutput.writeListToFile(blocks, "{0}/plots_runComp.html".format(foldername))
