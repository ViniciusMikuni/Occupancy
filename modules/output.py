"""
Module for output formatting and plotting

K. Schweiger, 2017
"""
import copy
import logging
from datetime import datetime

def getDelimiters(fortype):
    delimiter = ""
    endline = ""
    if fortype == "Markdown":
        delimiter = "|"
        endline = ""
    elif fortype == "LaTeX":
        delimiter = "&"
        endline = "\\"
    return delimiter, endline

def formatContainerFullPixelDetector(container):
    """
    Returns dict for each data group. Each data group is a list of the columns. The columns are also lists.
    """
    formattedData = {"Pix/Lay" : None, "Pix/Det" : None, "Clus/Lay" : None, "Clus/Det" : None}
    values = container.getValuesasDict("fullDetector")
    for data in formattedData:
        formatted = []
        if data.startswith("Pix"):
            formatted.append(["","hit pixel", "hit pixel / module", "hit pixel / cm^2", "hit pixel / cm^2 s", "Occupancy"])
        elif data.startswith("Clus"):
            formatted.append(["","cluster", "cluster / module", "cluster / cm^2", "cluster / cm^2 s"])
        for layer in container.LayerNames:
            vallist = [layer]
            for val in values[data]:
                if val != None:
                    vallist.append(val[layer])
                else:
                    vallist.append(None)
            formatted.append(copy.copy(vallist))
        formattedData[data] = copy.copy(formatted)
    return formattedData

def makeTabel(container, tabletype = "Markdown", Datatype = "fullDetector", outputname = "tableoutput"):
    delimiter, endline = getDelimiters(tabletype)
    if Datatype == "fullDetector":
        data = formatContainerFullPixelDetector(container)
    with open(outputname+".dat", "w+") as f:
        f.write("File created at: "+str(datetime.now())+"\n")
        for datacollection in data:
            f.write("\n "+str(datacollection)+"\n\n")
            for irow in range(len(data[datacollection][0])):
                row = ""
                for icolumn, column in enumerate(data[datacollection]):
                    if column[irow] is None:
                        column[irow] = ""
                    if icolumn == 0:
                        if isinstance(column[irow], float) and column[irow] > 0.01:
                            row = row + "{0:8.4f}".format(column[irow])
                        elif isinstance(column[irow], float) and column[irow] < 0.01:
                            row = row + "{0:8.4e}".format(column[irow])
                        else:
                            row = row + "{0}".format(column[irow])
                    else:
                        if isinstance(column[irow], float) and column[irow] > 0.01:
                            row = row + delimiter + "{0:8.4f}".format(column[irow])
                        elif isinstance(column[irow], float) and column[irow] < 0.01:
                            row = row + delimiter + "{0:8.4e}".format(column[irow])
                        else:
                            row = row + delimiter + "{0}".format(column[irow])
                f.write(row + endline + "\n")
                if irow == 0:
                    if tabletype == "Markdown":
                        f.write("----|----|----|----|----\n")
                    elif tabletype == "LaTeX":
                        f.write("\midrule\n")

def makeRunComparisonTable(listofcontainers,
                           tabletype = "Markdown", Datatype = "fullDetector", outputname = "tableoutput"):
    delimiter, endline = getDelimiters(tabletype)
    #TODO: compare one value in all layers for reach run
    #TODO: compare all values of one datagroup for one layer
    with open(outputname+".dat", "w+") as f:
        f.write("File created at: "+str(datetime.now())+"\n")
        for group in ["Pix/Lay", "Pix/Det", "Clus/Lay", "Clus/Det"]:
            f.write("\n "+str(group)+"\n\n")
            midrule = ""
            if group.startswith("Pix"):
                valuelist = ["perMod", "perArea", "perAreaSec", "occupancy"]
                if tabletype == "Markdown":
                    midrule = "----|----|----|----|----\n"
            else:
                valuelist = ["perMod", "perArea", "perAreaSec"]
                if tabletype == "Markdown":
                    midrule = "----|----|----|----\n"
            for layer in ["Layer1", "Layer2", "Layer3", "Layer4"]:
                f.write("\n "+str(layer)+"\n\n")
                for irun, runcontainerkey in enumerate(listofcontainers):
                    runcontainer = listofcontainers[runcontainerkey]
                    values = runcontainer.getValuesasDetailDict(Datatype)
                    if irun == 0:
                        firstline = str(layer)
                        for val in valuelist:
                            firstline = firstline + delimiter + val
                        firstline = firstline + endline + "\n"
                        f.write(firstline)
                        f.write(midrule)
                    line = str(runcontainer.name)
                    for val in valuelist:
                        line = line + delimiter + values[group][val]
                    line = line + endline + "\n"
                    f.write(line)
