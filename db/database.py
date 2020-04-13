
import os
import pony.orm as orm

from common.config import config

class MusicDatabase(orm.Database):
    __instance = None
    __first_init = True

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = orm.Database.__new__(cls)
        return cls.__instance

    def __init__(self, *args, **kwargs):
        if self.__first_init:
            orm.Database.__init__(self, *args, **kwargs)
            self.__first_init = False
   
    @classmethod
    def db(cls):
        return MusicDatabase("sqlite",os.path.join(config.dataPath, "music.sqlite"),create_db=True)
 
db = MusicDatabase.db(); 

if config.debug == True:
    orm.sql_debug(True)	
