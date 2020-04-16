
from common.crawler import *
from bs4 import BeautifulSoup 
from bs4.element import NavigableString, Tag
from common.utils import *

categoryTypeDic={"0":"All", 
              "1":"Unsorted",
              "2":"Album", 
              "3":"EP",
              "4":"Single", 
              "5":"Bootleg",
              "6":"Live", 
              "7":"Compilation",
              "8":"MixType", 
              "9":"Demo",
              "10":"DJ Mix", 
              "11":"Group Compilations",
              "12":"Split",
              "13":"Unoffical Compilation",
              "14":"OST",
              }

class MyzcloudConfig(object):
    artistBaseUrl="https://myzcloud.me/letter/{0}"
    baseUrl="https://myzcloud.me/{0}"

headers={'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'Proxy-Connection':'keep-alive',
            'Cache-Control':'max-age=0',
            'Upgrade-Insecure-Requests':'1',
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }
class MycloudAlbumInfo(object):
    def __init__(self, id = None, name = None, image = None, artistId="", artistName="", year="", songNum = 0, rating = ""):
        self.id = id
        self.url = "https://myzcloud.me/{0}".format(id)
        self.name = name
        self.image = image
        self.songNum = songNum
        self.artistId=artistId
        self.year =year
        self.artistName=artistName
        self.rating = rating
class MycloudArtistInfo(object):
    def __init__(self, id = None, name = None, image = None, songNum = 0, rating=""):
        self.id = id
        self.url = "https://myzcloud.me/{0}".format(id)
        self.name = name
        self.image = image
        self.songNum = songNum
class MycloudSongInfo(object):
    def __init__(self, id = None, name = None, artistName=""):
        self.id = id
        self.url = "https://myzcloud.me/{0}".format(id)
        self.name = name
        self.artistName = artistName
    
class MycloudSearchResult(object):
    def __init__(self, artistInfoList = None, ablumInfoList = None, songInfoList = None):
        self.artistInfoList = artistInfoList
        self.ablumInfoList = ablumInfoList
        self.songInfoList = songInfoList
class MyzcloudParser(object):
    def __init__(self, crawler, baseUrl="https://myzcloud.me/{0}"):
        self.baseUrl=baseUrl
        self.searchUrl="https://myzcloud.me/search"
        self.crawler=crawler
    def __getUrl(self, url):
        return self.baseUrl.format(id)
    def search(self, text):
        page = self.crawler.fetch(self.searchUrl, params={"searchText": text})
        return self.__parse_search_result(page)
    def __parse_search_result(self, page):
        bs = BeautifulSoup(page,"html.parser")
        divBodyContent = bs.find(id="bodyContent")
    
        divTables = divBodyContent.findAll(name="table", attrs={"class":"table table-condensed table-no-border"})
        
        result = MycloudSearchResult() 

   
        if divTables != None:
            result.artistInfoList = []
            result.ablumInfoList = []
            for divTable in divTables:
                ths = divTable.findAll(name="th")
                
                isArtistInfo = False
                for th in ths:
                    if th.string == "Artist" or th.string == "Исполнитель":
                        isArtistInfo = True
                        break
                    elif th.string == "Artist / Album" or th.string == "Исполнитель / Альбом":
                        isArtistInfo = False
                        break
                if isArtistInfo == True:
                    trs = divTable.tbody.findAll(name="tr")
                    for tr in trs:
                        imageTd=tr.td 
                        artistId = imageTd.a["href"]
                        image = imageTd.img["src"]
                        name = imageTd.img["alt"]
                        nameTd = imageTd.next_sibling.next_sibling
                        songNumTd = nameTd.next_sibling.next_sibling
                        songNum = int(songNumTd.text)
                        artistInfo = MycloudArtistInfo(id=artistId, name=name, image=image, songNum=songNum)
                        result.artistInfoList.append(artistInfo)
                else:
                    trs = divTable.tbody.findAll(name="tr")
                    for tr in trs:
                        imageTd=tr.td 
                        albumId = imageTd.a["href"]
                        image = imageTd.img["src"]
                        name = imageTd.img["alt"]
                        nameTd = imageTd.next_sibling.next_sibling 
                        artistId = nameTd.strong.a["href"]
                        artistName = nameTd.strong.a.text
                        yearTd = nameTd.next_sibling.next_sibling
                        year = yearTd.text
                        songNumTd = yearTd.next_sibling.next_sibling
                        songNum = int(songNumTd.text.replace(",", ""))
                        ratingTd=songNumTd.next_sibling.next_sibling
                        rating = ratingTd.text.replace(",", "")
                        artistInfo = MycloudAlbumInfo(id=artistId, name=name, image=image, artistId=artistId,
                                                      artistName = artistName, year= year,
                                                      songNum=songNum, rating=rating)
                        result.ablumInfoList.append(artistInfo)
            divPlayList = divBodyContent.find(name="div", attrs={"class": "playlist playlist--hover"})
                
            if divPlayList != None:
                result.songInfoList = []
                playListItems = divPlayList.findAll(name="div", attrs={"class": "playlist__item"})
                for playListItem in playListItems:
                    artistName = playListItem["data-artist"]
                    name = playListItem["data-name"]
                    aAdress = playListItem.find(name="a", attrs={"class":"dl-song"})
                    id = aAdress["href"]
                    songInfo = MycloudSongInfo(id=id,name=name, artistName=artistName)
                    result.songInfoList.append(songInfo)
                
                return result
   
    def __parseArtistList(self, page, parseHead = True):
        bs = BeautifulSoup(page,"html.parser")
        divBodyContent = bs.find(id="bodyContent")
        page = -1
        if parseHead:
            navList=divBodyContent.nav
            liLastPage=navList.find(name="li", attrs={"class":"page-item pagination-last"})
            page=int(liLastPage.a["href"][len("/len/letter/A/page") - 1:])
            
        artistList=[]
        divArtist=divBodyContent.find(name="div", attrs={"class":"table-responsive"})
        tbody = divArtist.table
        for tr in tbody.children:
            if not isinstance(tr, Tag) or tr.a == None:
                continue
            name = tr.a.text
            id = tr.a["href"]
            songNumTd = tr.td.next_sibling.next_sibling
            songNumStr= songNumTd.text.replace(",", "")
            ratingTd = tr.td.next_sibling.next_sibling
            rating = ratingTd.text 
            artistInfo=MycloudArtistInfo(id=id, name=name, songNum=int(songNumStr), rating=rating)
            artistList.append(artistInfo)
        return int(page), artistList
    
    def getArtistPage(self, alphabet = "A", page = 1, parseHeader=True):
        url = MyzcloudConfig.artistBaseUrl.format(alphabet)
        if page > 1:
            url = url +"/" + page
        page = self.crawler.fetch(url);
        return self.__parseArtistList(page, parseHead=True)
    def getArtistList(self, alphabet = "A"):
       
        totalPage, artiList=self.getArtistPage(alphabet, 1, True)
        
        if totalPage > 1:
            for page in range(2, totalPage):
                _, artiList = self.getArtistPage(alphabet, page, False)
    
    def __getAlbumList(self, type="albums", page = 1, year=None, parseHead = True):
        url = MyzcloudConfig.baseUrl.format(type)
        
           


crawler = Crawler(headers=headers, proxies={'http':"http://127.0.0.1:10001", 'https':"https://127.0.0.1:10001"})
#crawler = Crawler(proxies={'http':None, 'https':None})
parser = MyzcloudParser(baseUrl="https://myzcloud.me/{0}", crawler=crawler);
