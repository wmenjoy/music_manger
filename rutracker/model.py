from db.rutracker import RutrackerForumItemPo, RutrackerForumPo
from db.download import AlbumDownloadInfo
from common.utils import *
from pony.orm.core import PrimaryKey, Required, Optional, db_session


class RutrackerConfig(object):
    forumUrl="https://rutracker.org/forum/viewforum.php?f={0}"
    topicUml="https://rutracker.org/forum/viewtopic.php?t={0}"
    url="https://rutracker.org/{0}"

class NaviItem(object):
    def __init__(self, forumId=-1, name="",  url="", parentForumId=-1,parentUrl=""):
        self.id=0
        self.parentId=0
        self.forumId=forumId
        self.parentForumId=parentForumId
        self.name = name
        self.url = url
        self.parentUrl=parentUrl
        
    def toDbModel(self):
        return RutrackerForumPo(
            forumId=self.forumId,
            name=self.name,
            parentForumId=self.parentForumId,
            url = self.url,
            parentUrl=self.parentUrl,
        )
    
    @staticmethod
    def fromDbModel(forumPo):
        return RutrackerForum(
            id=forumPo.id,
            forumId=forumPo.forumId,
            name=forumPo.name,
            parentId=forumPo.parentId,
            parentForumId=forumPo.parentForumId,
            url=forumPo.url,
            parentUrl=forumPo.parentUrl,
            totalPage = forumPo.totalPage,
        )
    
    @db_session
    def updateLink(self):
        forumPo = RutrackerForumPo.get(forumId=self.forumId)
        parentPo = RutrackerForumPo.get(forumId=self.parentForumId)
        forumPo.parentId=parentPo.parentId
    @db_session
    def persist(self):
        if not RutrackerForumPo.exists(lambda po: po.forumId==self.forumId):
            forumPo = self.toDbModel()
        else:
            forumPo = RutrackerForumPo.get(forumId=self.forumId)
            forumPo.parentForumId=self.parentForumId

class RutrackerForum(object):
    def __init__(self,forumId, name="", parentForumId=-1, naviList=[], forumItemList=[], totalPage=0, parentUrl=""):
        self.forumId = forumId
        self.url=RutrackerConfig.forumUrl.format(forumId)
        self.parentUrl=parentUrl
        self.name = name
        self.naviList=naviList
        self.parentForumId=parentForumId
        self.forumItemList=forumItemList
        self.totalPage=totalPage
        self.id= 0
        self.parentId=0
    def toDbModel(self):
        extra={}
        extra["naviList"]=naviList
        
        return RutrackerForumPo(
            id=self.id,
            forumId=self.forumId,
            name=self.name,
            parentId=self.parentId,
            parentForumId=self.parentForumId,
            url = self.url,
            parentUrl= parentUrl,
            totalPage = self.totalPage,
            extra = toJsonStr(extra)
        )
    
    @staticmethod
    def fromDbModel(forumPo):
        extra = fromJson(forumPo.extra)
        naviListAttr=extra["naviList"]
        naviList=[]
         
        for  val in naviListAttr:
          naviItem = NaviItem()
          naviItem.__dict__.update(val)
          naviList.append(naviItem)
        
        return RutrackerForum(
            naviList=naviList,
            id=forumPo.id,
            forumId=forumPo.forumId,
            name=forumPo.name,
            parentId=forumPo.parentId,
            parentForumId=forumPo.parentForumId,
            url=forumPo.url,
            parentUrl=forumPo.parentUrl,
            totalPage = forumPo.totalPage,
        )
    
    @db_session
    def persist(self):
        forumPo = None
        if not RutrackerForumPo.exists(lambda po: po.forumId==self.forumId):
            forumPo = self.toDbModel()
        else:
            forumPo = RutrackerForumPo.get(forumId=self.forumId)
            forumPo.parentForumId=self.parentId
            forumPo.totalPage=self.totalPage
        
        parentPo = RutrackerForumPo.get(forumId=self.parentForumId)
        if parentPo != None:
            forumPo.parentId = parentPo.id
        if self.naviList == None:
            return
        
        for nav in self.naviList:
            parentPo = RutrackerForumPo.get(forumId=nav.parentForumId)
            po = RutrackerForumPo.get(forumId=nav.forumId)
            if parentPo != None and po != None:
                po.parentId = parentPo.id
    

class RutrackerTorrentInfo(object):
    def __init__(self, seeders="", leechers="", fileSize="0",magnet="", torrentUrl=""):
        self.seeders =  getIntValueFromStr(seeders)
        self.leechers = getIntValueFromStr(leechers)
        self.magnet = magnet
        self.torrentUrl = torrentUrl
        self.fileSize=fileSize
        
class RutrakcerTopicReplies(object):
    def __init__(self, nReplies, nDownloads):
        self.nReplies = getIntValueFromStr(nReplies)
        self.nDownloads = getIntValueFromStr(nDownloads.replace(",", ""))

class RutrakcerTopicLastPostInfo(object):
    def __init__(self, lastPostTime='', lastPostUser='', lastPostUrl=''):
        self.lastPostTime=lastPostTime
        self.lastPostUser = lastPostUser
        self.lastPostUrl = lastPostUrl
        
class RutrackerForumItem(object):
    def __init__(self, topicId, rutrackerForumId="", topicIcon='',newstLink='', approvedLabel="√", authLabel="", 
                 torTopicTitle="", topicAuthor='', torrentInfo=None, topicReplies=None, lastPostInfo=None):
        
        self.topicId=topicId
        self.id= 0
        self.forumId=0
        self.rutrackerForumId=rutrackerForumId
        self.topicUrl=RutrackerConfig.topicUml.format(topicId)
        self.topicIcon = topicIcon
        self.newstLink = newstLink
        self.approvedLabel = approvedLabel
        self.authLabel = authLabel
        self.torTopicTitle = torTopicTitle
        self.topicAuthor = topicAuthor
        self.torrentInfo = torrentInfo
        self.topicReplies = topicReplies
        self.lastPostInfo=lastPostInfo
 
    @staticmethod
    def fromDbModel(itemPo):
        return RutrackerForumItem(
            id = itemPo.id,
            forumId=itemPo.forumId,
            rutrackerForumId=itemPo.rutrackerForumId,
            topicId=itemPo.topicId,
            topicUrl=itemPo.topicUrl,
            topicIcon=itemPo.topicIcon,
            newstLink=itemPo.newstLink,
            approvedLabel=itemPo.approvedLabel,
            torTopicTitle=itemPo.torTopicTitle,
            topicAuthor=itemPo.topicAuthor,
            torrentInfo=RutrackerTorrentInfo(
                seeders=itemPo.seeders,
                leechers=itemPo.leechers,
                magnet=itemPo.magnet,
                torrentUrl=itemPo.torrentUrl,
            ),
            topicReplies=RutrakcerTopicReplies(
                nReplies=itemPo.nReplies,
                nDownloads=itemPo.nDownloads),
            lastPostInfo=RutrakcerTopicLastPostInfo(
            lastPostTime=itemPo.lastPostTime,
            lastPostUser=itemPo.lastPostUser,
            lastPostUrl=itemPo.lastPostUrl)
        )
        
    def toDbModel(self):
        seeders=""
        leechers=""
        magnet=""
        torrentUrl=""
        fileSize=""
        if self.torrentInfo != None:
            seeders = self.torrentInfo.seeders
            leechers = self.torrentInfo.leechers
            magnet= self.torrentInfo.magnet
            torrentUrl=self.torrentInfo.torrentUrl
            fileSize=self.torrentInfo.fileSize
        nReplies=""
        nDownloads=""
        if self.topicReplies != None:
            nReplies=self.topicReplies.nReplies
            nDownloads=self.topicReplies.nDownloads
        lastPostTime=""
        lastPostUser=""
        lastPostUrl=""
        if self.lastPostInfo != None:
            lastPostTime=self.lastPostInfo.lastPostTime
            lastPostUser=self.lastPostInfo.lastPostUser
            lastPostUrl=self.lastPostInfo.lastPostUrl
            
        
        return RutrackerForumItemPo(
            forumId=self.forumId,
            rutrackerForumId=self.rutrackerForumId,
            topicId=self.topicId,
            topicUrl=self.topicUrl,
            topicIcon=self.topicIcon,
            newstLink=self.newstLink,
            approvedLabel=self.approvedLabel,
            torTopicTitle=self.torTopicTitle,
            topicAuthor=self.topicAuthor,
            seeders=seeders,
            leechers=leechers,
            magnet=magnet,
            fileSize=fileSize,
            torrentUrl=torrentUrl,
            nReplies=nReplies,
            nDownloads=nDownloads,
            lastPostTime=lastPostTime,
            lastPostUser=lastPostUser,
            lastPostUrl=lastPostUrl,
        )
    @db_session
    def persist(self):
        forumPo = RutrackerForumPo.get(lambda po: po.forumId == self.rutrackerForumId)
        if forumPo != None:
            self.forumId=forumPo.id
        if not RutrackerForumItemPo.exists(lambda po: po.topicId==self.topicId):
            forumItemPO = self.toDbModel()
         
        else:
            forumItemPO = RutrackerForumItemPo.get(topicId=self.topicId)
            forumItemPO.forumId=self.forumId
            if self.torrentInfo != None:
                forumItemPO.seeders = self.torrentInfo.seeders
                forumItemPO.leechers = self.torrentInfo.leechers
                forumItemPO.magnet=self.torrentInfo.magnet
                forumItemPO.torrentUrl=self.torrentInfo.torrentUrl
            if self.topicReplies != None:
                forumItemPO.nReplies=self.topicReplies.nReplies
                forumItemPO.nDownloads=self.topicReplies.nDownloads
            if self.lastPostInfo != None:
                forumItemPO.lastPostTime=self.lastPostInfo.lastPostTime
                forumItemPO.lastPostUser=self.lastPostInfo.lastPostUser
                forumItemPO.lastPostUrl=self.lastPostInfo.lastPostUrl
    
    class RutrackerArtist(object):
        def __init__(self, artist, genre="", members=[], location=""):
            self.artist = artist
            
        
    class RutrackerAlbumInfo(object):
        def __init__(self, title, name="", artists=[], genre=[], year="", format="MP3", rate="320kbps"):
            self.artists = artists
            self.genre = genre
            self.year = year
            self.name = name
            self.format = format
            self.rate = rate
            self.title= title
        def isAlbum(self):
            title = self.title.upper()
            if title.find("Discography".upper()) != -1:
                return False
            elif title.find("Дискография".upper()) != -1:
                return False
            else:
                return True
            
        
    class RutrackerDiscography(object):
        def __init__(self, title, artist, years, format, rate, statistics, genre, **other):
            self.artist = artist
            self. years = years
            self.format = format
            self.rate = rate
            self.statistics = statistics
            self.genre = genre 
            self.other = other
            self.title= title
        def isDiscography(self):
            title = self.title.upper()
            if title.find("Discography".upper()) != -1:
                return True
            elif title.find("Дискография".upper()) != -1:
                return True
            else:
                return False