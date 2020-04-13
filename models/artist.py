
from models.common import MusicObject, defaultAge
import db.basic as dbm

class Artist(MusicObject):
    def __init__(self, id = 0, name = "", country="", location="", image="", age=defaultAge, gender=GenderEnum.MALE, 
                 isBand=BandEnum.UNKOWN, status=StatusEnum.ACTIVE, genre=None, lyricalThemes="", 
                 currentLabel="UNKOWN", formedIn=0, yearsActive=""):
        self.id = id
        self.name = name
        self.country = country
        self.location = location
        self.image = image
        self.age = age
        self.gender = gender
        self.isBand = isBand
        self.status = status
        self.genre = genre
        self.lyricalThemes=lyricalThemes
        self.currentLabel=currentLabel
        self.formedIn=formedIn
        self.yearsActive=yearsActive
        
    @staticmethod
    def fromDBModel(artistDb):
        genre = []
        if artistDb.genre != None:
            genre = artistDb.split(",")
        return Artist(
            id = artistDb.id,
            name = artistDb.name,
            country = artistDb.country,
            location = artistDb.location,
            image = artistDb.image,
            age = artistDb.age,
            gender = artistDb.gender,
            isBand = artistDb.isBand,
            status = artistDb.status,
            genre = genre,
            lyricalThemes = artistDb.lyricalThemes,
            currentLabel = currentLabel,
            formedIn = artistDb.formedIn,
            yearsActive = artistDb.yearsActive
        )
    def toDbModel(self):
        genre = ""
        if self.genre != None:
            genre = str.join(self.genre)
        return dbm.Artist(
            id = self.id,
            name = self.name,
            country = self.country,
            location = self.location,
            image = self.image,
            age = self.age,
            gender = self.gender,
            isBand = self.isBand,
            status = self.status,
            genre = genre,
            lyricalThemes = self.lyricalThemes,
            currentLabel = currentLabel,
            formedIn = self.formedIn,
            yearsActive = self.yearsActive
        )
        