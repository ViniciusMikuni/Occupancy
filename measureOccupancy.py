"""
Main script for occupancy measurement

K. Schweiger, 2017
"""
# Python standard lib imports
import os
import json
import logging
import logging.config

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
        #Overwrite config definitions with system arguments (Default is same as in config)
        config["handlers"]["info_file_handler"]["filename"] = logname+".log"
        config["handlers"]["error_file_handler"]["filename"] = errname+".log"
        config["handlers"]["console"]["level"] = loglevel
        config["handlers"]["info_file_handler"]["level"] = loglevel
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

def main(args):
    import ROOT

    import modules.measurement

    setup_logging(logname = args.outlog, errname = args.errlog, loglevel = args.logging)

    logger = logging.getLogger(__name__)

    logger.info("Starting occupancy measurement")
    logger.debug("Logging level set to: "+str(args.logging))

    if args.logging > 0:
        ROOT.gErrorIgnoreLevel = ROOT.kError# kPrint, kInfo, kWarning, kError, kBreak, kSysError, kFatal;


    if args.config is not None:
        logger.info("Using config set in arguments: {0}".format(args.config))
        modules.measurement.occupancyFromConfig(args.config)

    elif args.inputfile is not None and args.collBunch is not None:
        logger.info("Using file {0} and number of colliding bunches {1}".format(args.inputfile, args.collBunch))
        modules.measurement.occupancyFromFile(args.inputfile, args.collBunch)
    else:
        pass
if __name__ == "__main__":
    import argparse
    ##############################################################################################################
    ##############################################################################################################
    # Argument parser definitions:
    argumentparser = argparse.ArgumentParser(
        description='Main script for occupancy measurement'
    )

    argumentparser.add_argument(
        "--logging",
        action = "store",
        help = "Define logging level: CRITICAL - 50, ERROR - 40, WARNING - 30, INFO - 20, DEBUG - 10, NOTSET - 0 \nSet to 0 to activate ROOT root messages",
        type=int,
        default=20
    )

    argumentparser.add_argument(
        "--outlog",
        action = "store",
        help = "Define name of output logfile",
        type=str,
        default="output"
    )

    argumentparser.add_argument(
        "--errlog",
        action = "store",
        help = "Define name of error logfile",
        type=str,
        default="error"
    )

    argumentparser.add_argument(
        "--config",
        action = "store",
        help = "Not implemented yet",
        type=str,
        default = None,
    )

    argumentparser.add_argument(
        "--inputfile",
        action = "store",
        help = "Input file",
        type=str,
        default = None,
    )

    argumentparser.add_argument(
        "--collBunch",
        action = "store",
        help = "Colliding bunches for this fill",
        type=float,
        default = None,
    )

    args = argumentparser.parse_args()

    if args.config is None and (args.inputfile is None and args.collBunch is None):
        print "Either set config or inputfile and colliding bunches"
        exit()
    #
    ##############################################################################################################
    ##############################################################################################################
    main(args)
