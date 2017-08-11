import os
import json
import logging
import logging.config

from array import array
from glob import glob

from ConfigParser import SafeConfigParser

def setup_logging( default_path='configs/logging.json', default_level=logging.INFO,
                   logname = "output", errname = "error", loglevel = 20):
    """
    Setup logging configuration
    """
    path = default_path
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        #Overwrite config definitions with command line arguments (Default is same as in config)
        config["handlers"]["info_file_handler"]["filename"] = logname+".log"
        config["handlers"]["error_file_handler"]["filename"] = errname+".log"
        config["handlers"]["console"]["level"] = loglevel
        config["handlers"]["info_file_handler"]["level"] = loglevel
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def cmstext(AdditionalText):
    import ROOT

    if not AdditionalText in ["Wip","WipSimul","Prelim"]:
        logging.warning("cmstext() called with wrong argument. Will do WiP")

    simul, cms = None, None
    if AdditionalText == "WIPSimul":
        simul = ROOT.TLatex(0.18, 0.908, '#scale[1.2]{#bf{CMS}} #it{simulation}')
    if AdditionalText == "Prelim":
        simul = ROOT.TLatex(0.18, 0.908, '#scale[1.2]{#bf{CMS}} #it{Preliminary}')
    if AdditionalText == "Wip":
        simul = ROOT.TLatex(0.18, 0.908, '#scale[1.2]{#bf{CMS}}')
    simul.SetTextFont(42)
    simul.SetTextSize(0.045)
    simul.SetNDC()


    if AdditionalText.startswith("Wip"):
        cms = ROOT.TLatex(0.18, 0.86, ' #it{work in progress}')
        cms.SetTextFont(42)
        cms.SetTextSize(0.045)
        cms.SetNDC()

    return simul, cms



def makeArraysFromCfg(config, value):

    x, y = array('f'), array('f')

    axislabels = []

    #TODO: Test for values not in config

    for isection, section in enumerate(config.sections()):
        logging.debug("Making x,y axis for {0} - {1}".format(section, config.getfloat(section, value)))
        axislabels.append(section)
        x.append(isection)
        y.append(config.getfloat(section, value))


    return axislabels, x, y

def makeGraph(plotvalues, ytitle, legendnames, cmslabel):
    styleconfig = SafeConfigParser()
    logging.debug("Loading style config")
    styleconfig.read("configs/style.cfg")

    import ROOT

    color = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kViolet]

    graphs = []
    npoints = 0
    xLabelText = None
    for icurve, curve in enumerate(plotvalues):
        xlabels, xvalues, yvalues = curve
        xLabelText = xlabels
        graph = ROOT.TGraph(len(xvalues), xvalues, yvalues)
        npoints = len(xvalues)
        graph.SetLineColor(color[icurve])
        graph.SetLineWidth(2)
        graph.SetMarkerColor(color[icurve])
        graph.SetMarkerSize(1)
        graph.SetMarkerStyle(21)

        graphs.append(graph)

    c1 = ROOT.TCanvas("c1","c1",800,640)
    c1.cd()

    #SetLogy()

    leg = ROOT.TLegend(0.7,0.5,0.9,0.7)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    for igraph, graph in enumerate(graphs):
        logging.debug("Adding graph {0}".format(igraph))
        if igraph == 0:
            graph.Draw("AP")
            graph.GetHistogram().SetMinimum(0.0 )
            graph.GetXaxis().SetLimits(-0.5, npoints-1+0.5)
            graph.SetTitle("")
            if styleconfig.has_option("Renaming", ytitle):
                ytitle = styleconfig.get("Renaming", ytitle)
            graph.GetYaxis().SetTitle(ytitle)
            graph.GetYaxis().SetTitleOffset(graph.GetYaxis().GetTitleOffset() * 2)
            xax = graph.GetXaxis()
            for i in range(npoints):
                binIndex = xax.FindBin(i)
                xax.SetBinLabel(binIndex, str(xLabelText[i]))
            graph.GetXaxis().LabelsOption("v");
            graph.GetXaxis().SetTitle()
            graph.Draw("AP")
        else:
            graph.Draw("P")
        leg.AddEntry(graph, legendnames[igraph], "p")

    if len(graphs) > 1:
        leg.Draw("same")

    a,b = cmstext(cmslabel)
    a.Draw("same")
    b.Draw("same")

    c1.Update()
    raw_input("")

def main(args):
    import ROOT

    setup_logging(logname = "ROOTplotting_output", errname = "ROOTplotting_error", loglevel = args.logging)

    logger = logging.getLogger(__name__)

    logger.info("Starting ROOT plotting for occupancy measurement")
    logger.debug("Logging level set to: "+str(args.logging))

    if args.logging > 0:
        ROOT.gErrorIgnoreLevel = ROOT.kError# kPrint, kInfo, kWarning, kError, kBreak, kSysError, kFatal;

    if len(args.config) > 1:
        if len(args.config) != len(args.names):
            logger.error("If more than one config is passes, the same amount of names is required (--names).")
            logger.info("Exiting script")
            exit()
    if "*" in args.config:
        print glob(args.config)

    plotvalues = []
    for conf in args.config:
        logging.info("Setting values for config: {0}".format(conf))
        cfg = SafeConfigParser()
        cfg.read( conf )

        plotvalues.append(makeArraysFromCfg(cfg, args.parameter))
        del cfg

    makeGraph(plotvalues, args.parameter, args.names, args.cmslabel)



if __name__ == "__main__":
    import argparse

    # Argument parser definitions:
    argumentparser = argparse.ArgumentParser(
        description='ROOT plotting utility for measureOccupancy.py'
    )

    argumentparser.add_argument(
        "-l", "--logging",
        action = "store",
        help = "Define logging level: CRITICAL - 50, ERROR - 40, WARNING - 30, INFO - 20, DEBUG - 10, NOTSET - 0 \nSet to 0 to activate ROOT root messages",
        type=int,
        default=20
    )

    argumentparser.add_argument(
        "-cfg", "--config",
        nargs='+',
        action = "store",
        help = "Config file",
        type=str,
        required = True,
    )

    argumentparser.add_argument(
        "-p", "--parameter",
        action = "store",
        help = "Parameter to be plotted",
        type = str,
        required = True,
    )

    argumentparser.add_argument(
        "--cmslabel",
        action = "store",
        help = "Text for the plot next to the CMS label. User Wip, Prelim",
        choices=["Wip", "Prelim"],
        default = "Wip",
        type = str
    )

    argumentparser.add_argument(
        "--names",
        action = "store",
        help = "If more than one config this is necessary for the legend",
        nargs='+',
        type=str,
        default = None
    )

    main(argumentparser.parse_args())
