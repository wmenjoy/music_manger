import os
import logging


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = 'download.log' or False
LOG_FORMAT = '%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s'
LOG_LEVEL = logging.INFO

dataPath=os.path.join(CURRENT_PATH, "db")

if not os.path.exists(dataPath):
    os.makedirs(dataPath)



class Config(object):
    #__slots__= ["downloadPath", "dataPath"]
    def __init__(self, downloadPath="", dataPath="", logFile="", logFormat=None, logLevel=logging.INFO, debug=False, fileNameWay="default"):
        self.downloadPath = downloadPath
        self.debug = debug
        self.dataPath = dataPath
        self.logLevel = logLevel
        self.logFormat = logFormat
        self.logFile = logFile
        if self.logFormat == None:
            self.logFormat = LOG_FORMAT
        self.fileNameWay = fileNameWay

config = Config()