
import logging
import json
from common.config import config
import unicodedata
import re

def obj_dict(obj):
    return obj.__dict__

def toJsonStr(obj):
    return json.dumps(obj, default=obj_dict, ensure_ascii=False)

def fromJson(jsonStr):
    return json.loads(jsonStr)

def getIntValueFromStr(value, defaultValue=0):
    if value != None and value != "":
        return int(value.replace(",", ""))
    else:
        return 0
    
def validate_file_name(songname):
    # trans chinese punctuation to english
    songname = unicodedata.normalize('NFKC', songname)
    songname = songname.replace('/', "-").replace('\"', "")
    rstr = r"[\/\\\:\*\?\"\<\>\|\+\-:;',=.?@]"
    # Replace the reserved characters in the song name to '-'
    rstr = r"[\/\\\:\*\?\"\<\>\|\+\-:;=?@]"  # '/ \ : * ? " < > |'
    return re.sub(rstr, "-", songname)

def set_logger():
    logger = logging.getLogger()
    logger.setLevel(config.logLevel)
    formatter = logging.Formatter(fmt=config.logFormat, datefmt='%Y-%m-%d %H:%M:%S')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if config.logFile:
        fh = logging.FileHandler(config.logFile, encoding="utf-8")
        fh.setLevel(config.logLevel)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

logger=set_logger()