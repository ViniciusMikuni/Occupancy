from CRABAPI.RawCommand import crabCommand

def submit(config):
    res = crabCommand('submit', config = config)

from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

"""
("298653",'/ExpressPhysics/Run2017B-Express-v2/FEVT'),
("298809",'/ExpressPhysics/Run2017B-Express-v2/FEVT'),
("298853",'/ExpressPhysics/Run2017B-Express-v2/FEVT'),
("298996",'/ExpressPhysics/Run2017B-Express-v2/FEVT'),
("299061",'/ExpressPhysics/Run2017B-Express-v2/FEVT'),
("299096",'/ExpressPhysics/Run2017B-Express-v2/FEVT'),
("299380",'/ExpressPhysics/Run2017C-Express-v1/FEVT'),
("299381",'/ExpressPhysics/Run2017C-Express-v1/FEVT'),
("299592",'/ExpressPhysics/Run2017C-Express-v1/FEVT'),
("299614",'/ExpressPhysics/Run2017C-Express-v1/FEVT'),
("300122",'/ExpressPhysics/Run2017C-Express-v1/FEVT'),
("300459",'/ExpressPhysics/Run2017C-Express-v2/FEVT'),
("300466",'/ExpressPhysics/Run2017C-Express-v2/FEVT'),
("300780",'/ExpressPhysics/Run2017C-Express-v3/FEVT'),
("301417",'/ExpressPhysics/Run2017C-Express-v3/FEVT')
("301627","/ExpressPhysics/Run2017C-Express-v3/FEVT"),
("301970","/ExpressPhysics/Run2017C-Express-v3/FEVT"),
("302031","/ExpressPhysics/Run2017D-Express-v1/FEVT"),
("302042","/ExpressPhysics/Run2017D-Express-v1/FEVT")
("302472","/ExpressPhysics/Run2017D-Express-v1/FEVT")
("302654","/ExpressPhysics/Run2017D-Express-v1/FEVT"),
("303832","/ExpressPhysics/Run2017E-Express-v1/FEVT")
("303999","/ExpressPhysics/Run2017E-Express-v1/FEVT")
("304447","/ExpressPhysics/Run2017E-Express-v1/FEVT")
("305044","/ExpressPhysics/Run2017F-Express-v1/FEVT")
"""

runs = [
    ("305840","/ExpressPhysics/Run2017F-Express-v1/FEVT")
       ]


for run, dataset in runs: 
    config.General.requestName     = 'Run'+run
    config.General.workArea        = 'crab_data'
    config.General.transferOutputs = True
    config.General.transferLogs    = True
    
    config.JobType.pluginName = 'Analysis'
    config.JobType.psetName = 'PixClusterAna.py'
    
    config.Data.inputDataset  = dataset
    config.Data.inputDBS = 'global'
    config.Data.splitting = 'LumiBased'
    config.Data.unitsPerJob = 10
    config.Data.runRange = run+'-'+run
    #config.Data.lumiMask = '/afs/cern.ch/user/k/koschwei/work/pixel/CMSSW_9_2_0_patch2/src/DPGAnalysis-SiPixelTools/HitAnalyzer/test/occupancyMask.json'
    config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/DCSOnly/json_DCSONLY.txt'
    config.Data.outLFNDirBase = '/store/user/koschwei/PixClusAna_v2/Run'+run
    config.Data.publication = False
    
    config.Site.storageSite = 'T3_CH_PSI'

    submit(config)
