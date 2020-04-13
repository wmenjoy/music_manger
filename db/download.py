from datetime import date, datetime
import pony.orm as orm
from pony.orm.core import PrimaryKey, Required, Optional
from models.common import DownloadStatus

from .database import *


class AlbumDownloadInfo(db.Entity):
    """
        Artist table
    """
    _table_ = "album_download_info"
    id = PrimaryKey(int, auto=True)
    albumId=Required(int)
    name= Required(str, max_len=512)
    src=Required(int)
    srcAlbumId=Optional(str)
    srcAlbumUrl=Optional(str)
    status=Required(int, default=DownloadStatus.NOT)
    extra=Required(str, default="{}", max_len=4096)
    createTime=Required(datetime, default=datetime.today)
    lastModifiedTime=Required(datetime, default=datetime.today)
    lastOperator=Required(str, default="system")
    
