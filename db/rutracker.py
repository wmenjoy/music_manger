from datetime import date, datetime
import pony.orm as orm
from pony.orm.core import PrimaryKey, Required, Optional, db_session
from models.common import DownloadStatus

from .database import *




class RutrackerForumPo(db.Entity):
    _table_ = "rutracker_forum_info"
    id = PrimaryKey(int, auto=True)
    forumId=Required(int, unique=True)
    name=Required(str, max_len=512)
    parentId=Required(int, default=0)
    parentForumId=Required(int)
    parentUrl=Optional(str, max_len=1024)
    url=Required(str, max_len=1024)
    totalPage=Required(int, default=0)
    extra=Required(str, default="{}", max_len=4096)
    createTime=Required(datetime, default=datetime.today)
    lastModifiedTime=Required(datetime, default=datetime.today)
    lastOperator=Required(str, default="system")

class RutrackerForumItemPo(db.Entity):
    _table_ = "rutracker_forum_item_info"
    id = PrimaryKey(int, auto=True)
    topicId=Required(str)
    topicUrl=Required(str, max_len=1024)
    forumId=Required(int, default=0)
    rutrackerForumId=Required(int)
    topicIcon=Optional(str, max_len=1024)
    newstLink=Optional(str, max_len=1024)
    approvedLabel=Optional(str, max_len=128)
    torTopicTitle=Required(str, max_len=2048)
    topicAuthor=Required(str, max_len=128)
    seeders=Optional(int, default=0)
    leechers=Optional(int, default=0)
    magnet=Optional(str, max_len=2048, default="")
    torrentUrl=Optional(str, max_len=1024, default="")
    fileSize=Optional(str, max_len=32)
    nReplies=Optional(int, default=0)
    nDownloads=Optional(int, default=0)
    lastPostTime=Optional(str)
    lastPostUser=Optional(str)
    lastPostUrl=Optional(str)


class RutrackerDownloadInfoPo(db.Entity):
    _table_ = "rutracker_album_download_info"
    id = PrimaryKey(int, auto=True)
    name= Required(str, max_len=512)
    url=Required(str)
    topicId=Required(int)
    status=Required(int, default=DownloadStatus.NOT)
    extra=Required(str, default="{}", max_len=4096)
    createTime=Required(datetime, default=datetime.today)
    lastModifiedTime=Required(datetime, default=datetime.today)
    lastOperator=Required(str, default="system")