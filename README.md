# Occupancy

Use    
`python measureOccupancy.py --inputfile=path/to/file --collBunch=int --instLumi=int/float --nFiles=int`  (Single Mode)  
or   
`python measureOccupancy.py --config=configs/testconfig.cfg`  (Config Mode)   
to run the code.

Add the flag __--skipplots__ (without argument) if the plotting module should be skipped. Plots are only implemented for config mode.

## Requirements
The following python modules are necessary:
* __ROOT__ (pyROOT)
* __pandas__ (dependencies (?): numpy, scipy, matplotlib)

_Note:_ If run on the T3@PSI using some versions of CMSSW (e.g. 8_0_26) results in crash because matplotlib can not be correctly imported.

## Config description
The configs used for config mode need to contain a __General__ section and one or more __Run__ sections:

    [General]
    title=string
    description=string
    foldername=string
    latexexport=bool
    csvexport=bool
    cfgexport=bool

* __title__ will be displayed as `<h1>` in the top of the output HTML file
* __description__  will be displayed as subtitle in the output HTML file
* __foldername__ is used as name of the folder containing the output files. If not present it will be created
* __latexexport__ if _True_, all tables will be exported in LaTex and saved in _foldername_/tex
* __csvexport__ if _True_, all tables will be exported in CSV (separator ;) and saved in _foldername_/csv
* __cfgexport__ if _True_, all tables will be exported as config file written with the python config parser and saved in _foldername_/cfg

```
[RunName]
collidingBunches=float/int
lumi=float
file=string
nFiles=int
fill=int
comment=string
dataset=string
```
* __RunName__ is a unique name used the index the runs and is displayed as name in the output tables
* __collidingBunches__ and __lumi__ are used for calculations and can be obtained form WBM. __lumi__ is the average inst. luminosity in the considered LS range in e30 cm^-2 s^-1.
* __comment__ and __dataset__ are displayed in the output HTML files
* __nFiles__ is needed for some histograms that are normalized to the number of processed events in preprocessing. If this is done on a batch system the normalization is not valid anymore after _hadd_-ing the files.
* __fill__ will be displayed in a separate overview and is not necessary for any calculations (can be left without value)
If a config option is desired to be empty (for example if the section is a placeholder with empty file option), also remove the __=__ sign.


## Plotting
In `configs/style` some option for plotting can be set:

```
[Plotting]
dpi=int
savepdf=bool
```

For fast code execution __savepdf__ should be set to _False_ and __dpi__ to _200 or lower_.

### ROOTplotting
Using `ROOTplotting.py` the output of `measureOccupancy.py` can be plotted as ROOT TGraph. Use the __cfgexport__ option in the general section of you config to get the tables in a python readable config. The configs are used for the plotting.

#### Required arguments and usage
`python ROOTplotting.py --config [config.cfg ....] --names [legendtext ....] --parameter [internalValueName]`   

* The __--config__ and __--names__ arguments can be lists (separated with space) and need to be the same length. If only one config is passed, names can also be skipped.
* __--parameter__ need to be one of the options in the config used for plotting.
