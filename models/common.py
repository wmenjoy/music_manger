import enum

class InformationSrc(enum.IntEnum):
    Rutracker = 1
    Myzcloud = 2
    MetalTracker=3
    MetalArchives=4
    discogs = 5
class DownloadStatus(enum.IntEnum):
    NOT = 0
    STARTING = 1
    FINISHED = 2

class GenderEnum(enum.IntEnum):
    UNKOWN = -1
    MALE = 0
    FAMALE = 1
    MIDDLE = 2
    
class BandEnum(enum.IntEnum):
    UNKONW = 0
    BAND = 1
    SINGLE = 2
    
class StatusEnum(enum.IntEnum):
    UNKOWN = 0
    ACTIVE = 1
    SPLIT_UP = 2
    ON_HOLD = 3
    CHANGE_NAME = 4
    DEAD = 5

class AlbumType(enum.IntEnum):
        Unsorted = 1
        Album = 2
        Ep = 3
        Single = 4
        BootLeg = 5
        Live = 6
        Compilation = 7
        MixType = 8
        Demo = 9
        DJMix = 10
        GroupCompilation = 11
        Split = 12
        UnofficalCompilation=13
        OST=15
        Score=16

class ArtistBandRelationType(enum.IntEnum):
    ACTIVE = 0
    PAST = 1
    GUEST__SESSION = 2

class MusicObject(object):
    pass

## 表示年龄未知
defaultAge=0 