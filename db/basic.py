import sqlite3
from datetime import date, datetime
import pony.orm as orm
from pony.orm.core import PrimaryKey, Required, Optional

from .database import *
from models.common import GenderEnum, BandEnum, ArtistBandRelationType, AlbumType, StatusEnum
from models.common import defaultAge


class Artist(db.Entity):
    """
        Artist table
    """
    _table_ = "artist"
    id = PrimaryKey(int, auto=True)
    name= Required(str, max_len=512)
    country=Optional(str)
    location=Optional(str)
    image=Optional(str)
    age=Required(int, default=defaultAge)
    gender=Required(int, default=GenderEnum.MALE)
    isBand=Required(int, default=BandEnum.UNKOWN)
    status=Required(int, default=StatusEnum.ACTIVE)
    genre=Optional(str)
    lyricalThemes=Optional(str)
    currentLabel=Required(str, default="UNKOWN")
    FormedIn=Required(int, default=0)
    yearsActive=Optional(str)
    extra=Required(str, default="{}", max_len=4096)
    createTime=Required(datetime, default=datetime.today)
    lastModifiedTime=Required(datetime, default=datetime.today)
    lastOperator=Required(str, default="system")
    orm.composite_key(name, country)


class ArtistMemberRelation(db.Entity):
    _table_ = "artist_relation"
    id = PrimaryKey(int, auto=True)
    artistId = Required(int)
    bandName = Required(str)
    bandId =  Required(int)
    type = Required(str, default=ArtistBandRelationType.ACTIVE)
    work = Optional(str)
    extra=Required(str, default="{}", max_len=4096)
    createTime=Required(datetime, default=datetime.today)
    lastModifiedTime=Required(datetime, default=datetime.today)
    lastOperator=Required(str, default="system")
    
class Album(db.Entity):
    _table_ = "album"
    id = PrimaryKey(int, auto=True)
    image=Optional(str)
    artistId = Optional(int, default=0)
    name = Required(str)
    type = Required(int ,default=AlbumType.Unsorted)
    releaseDate = Required(int, default=1900)
    label=Optional(str, default="")
    format=Optional(str, default="CD")
    duration=Optional(str)
    extra=Required(str, default="{}", max_len=4096)
    createTime=Required(datetime, default=datetime.today)
    lastModifiedTime=Required(datetime, default=datetime.today)
    lastOperator=Required(str, default="system")
    
class Music(db.Entity):
    _table_ = "music"
    id = PrimaryKey(int, auto=True)
    position=Required(int, auto=0)
    name=Required(str)
    artistId=Optional(int, default=0)
    otherArtistIds=Optional(str)
    duration=Optional(str)
    lyrics=Optional(str)
    extra=Required(str, default="{}", max_len=4096)
    createTime=Required(datetime, default=datetime.today)
    lastModifiedTime=Required(datetime, default=datetime.today)
    lastOperator=Required(str, default="system")

if __name__ == "__main__":
    db.drop_table(table_name="artist", if_exists=True, with_all_data=True)

    db.generate_mapping(create_tables=True)
    
    with orm.db_session:
        a = Artist(name="Linkin Park",
                    country="America",
                    location="CA",
                    genre="Alternative",
                    lyricalThemes="Love, War",
                    currentLabel="Unsigned",
                    FormedIn=1998,
                    yearsActive="1998-2018"
                   )
        orm.commit()
        b = orm.select(p for p in Artist if p.name == "Linkin Park")[:]
        print(b[0].name)
        
      