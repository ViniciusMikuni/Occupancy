"""
Modules containing different testing functions

K. Schweiger, 2017
"""


def isHistoinFile(inputfile, histoname):
    isinFile = False
    if inputfile.Get(histoname) != None:
        isinFile = True
    return isinFile
