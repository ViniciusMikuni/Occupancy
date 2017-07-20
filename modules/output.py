"""
Module for output formatting and plotting

K. Schweiger, 2017
"""
import copy
import logging
from datetime import datetime

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
    if tabletype == "Markdown":
        delimiter = "|"
        endline = ""
    elif tabletype == "LaTeX":
        delimiter = "&"
        endline = "\\"
    if Datatype == "fullDetector":
        data = formatContainerFullPixelDetector(container)
    with open("outputname.dat", "w+") as f:
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
