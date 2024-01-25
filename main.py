import requests
from bs4 import BeautifulSoup 
from bs4.element import NavigableString, Tag
from common.utils import *
from common.config import *
import json
import re
import unicodedata
import os
import sys
import io
from concurrent.futures import ThreadPoolExecutor
import time
import random
import logging
import collections
from functools import partial
import tqdm
import click
import argparse
from http import cookiejar as cookielib
from urllib3.exceptions import NewConnectionError



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


headers={'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'Proxy-Connection':'keep-alive',
            'Cache-Control':'max-age=0',
            'Upgrade-Insecure-Requests':'1',
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }

LOG_FILE = 'download.log' or False
LOG_FORMAT = '%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s'
LOG_LEVEL = logging.INFO
MINIMUM_SIZE = 10

DOWNLOAD_DIR = os.path.join(os.getcwd(), "songs_dir")
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))


def fromFile(file):
    albumInfo = AlbumInfo()
    oDict = None
    with open(file, 'r') as f:
        oDict = json.load(f)
    albumInfo.__dict__ = oDict
    musicList =  oDict["musicList"]
    albumInfo.musicList = []
    for val in musicList:
        musicInfo = MusicInfo()
        musicInfo.__dict__.update(val)
        albumInfo.musicList.append(musicInfo)
    return albumInfo

def toFile(obj, file):
    with open(file, 'w') as f:
        json.dump(obj,  f, default=obj_dict)

    
class ArtistInfo(object):
    def __init__(self, name="", members=None, country=None):
        self.name = name
        self.members=[]
        self.country=country

class MusicInfo(object):
    def __init__(self, name="", album="", url="", artist="", dataTitle="", postion="0", downloadDir=None, download=None, downloadUrl=""):
        self.name = name
        self.url = url
        self.album = album
        self.artist = artist
        self.position = postion
        self.dataTitle = dataTitle
        self.downloadDir=downloadDir
        self.download = download
        self.downloadUrl=downloadUrl
    def getSongName(self):
        downloadDir = self.downloadDir   
        if self.downloadDir == None or self.downloadDir == "":
            downloadDir = os.path.join(DOWNLOAD_DIR, validate_file_name(self.album))
        if self.download == None or self.download == "":
            return  os.path.join(downloadDir, validate_file_name(self.position + "."+ self.artist + "-" +self.name + ".mp3"))
        else:
            return  os.path.join(downloadDir, validate_file_name(self.download))
                    
class AlbumInfo(object):
    def __init__(self, name="", image="", url="", artist="", genre="", musicList=None, dataType="0", year="", category="artist", fullName="", downloadPath=None):
        self.name = name
        self.fullName=fullName
        self.image = image
        self.artist = artist
        self.genre = genre
        self.musicList = musicList
        self.dataType = dataType
        self.year = year
        self.category=category
        self.url=url
        self.downloadPath=downloadPath
     
    def getAlbumDownloadDir(self):
        if self.downloadPath != None:
            return self.downloadPath 
        artist=self.artist
        if artist == None:
            artist = "Various Artists"
        
        albumDir = None
        if self.year != None and self.year != "":
            albumDir=os.path.join(DOWNLOAD_DIR, validate_file_name(artist), self.year + " - " + validate_file_name(self.name)) 
        else:
            albumDir=os.path.join(DOWNLOAD_DIR, validate_file_name(artist),  validate_file_name(self.name)) 

        if not os.path.exists(albumDir):
            os.makedirs(albumDir, exist_ok=True)
        self.downloadPath = albumDir
        return albumDir
    def getAlbumInfoFile(self):
        path = self.getAlbumDownloadDir()
        
        if path == None:
            return None
        
        return os.path.join(path, "album.txt");
    
    def loadf(self):
        path = self.getAlbumInfoFile();
        if not os.path.exists(path):
            return False
        try:
            oDict = None
            with open(path, 'r', encoding="utf-8") as f:
                oDict = json.load(f)
            self.__dict__ = oDict
            musicList =  oDict["musicList"]
            self.musicList = []
            for val in musicList:
                musicInfo = MusicInfo()
                musicInfo.__dict__.update(val)
                self.musicList.append(musicInfo)
            return True        
        except BaseException as e:
            logger.info("读取文件出错", str(e))
            return False
        

class Crawler(object):
    def __init__(self, timeout=180, proxies=None):
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.download_session = requests.Session()
        self.timeout = timeout
        self.proxies = proxies
    def downloadImage(self, image_url, image_address):
        try:
            resp = requests.Session().get(
                    image_url, timeout=self.timeout, stream=True)
            if resp.status_code != 200:
                logger.info("download pic %s error", image_url)
                return
            
            length = int(resp.headers.get('content-length'))
            label = 'Downloading {} {}kb'.format(image_url, int(length/1024))

            with click.progressbar(length=length, label=label) as progressbar:
                with open(image_address, 'wb') as image_file:
                    for chunk in resp.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            image_file.write(chunk)
                            progressbar.update(1024)
        except requests.exceptions.Timeout as err:
            logger.error("%s during download filepath" % err)
        except requests.exceptions.ConnectionError:
            logger.error("%s during download filepath" % err)
    def getRealAddress(self, song_url):
        if song_url == None or song_url == "":
            return song_url
        resp = requests.Session().head(
            song_url, timeout=self.timeout, stream=True, headers=headers, proxies=self.proxies)
        
        if resp.status_code == 302:
            realLocation = resp.headers.get("Location")
            print("地址被重定向:", realLocation)
            return realLocation
        return song_url            
    def getSongByUrl(self, song_url, song_name, counter = None, checkHeader=False):       
        i = 0
        while i < 3:
            try:
                result =  self.__getSongByUrl(song_url, song_name, counter, checkHeader)
                if result == True:
                    return result
                i = i + 1
            except BaseException as e:
                print("有异常发生" + str(e))
                i = i + 1
                
        return False
    def __getSongByUrl(self, song_url, song_name, counter, checkHeader=False):
        try:
            url = song_url
            length = 0
            resp = None
            if checkHeader:
                resp = requests.Session().head(
                    url, timeout=self.timeout, stream=True, headers=headers, proxies=self.proxies)
                if resp.status_code == 302:
                    url = resp.headers.get("Location")
                    print("地址被重定向:", url)
                elif resp.status_code != 200:
                    print("download Error for ", song_name)
                    return False
                
                resp = requests.Session().get(
                    url, timeout=self.timeout, stream=True, headers=headers, proxies=self.proxies)
                if resp.status_code != 200:
                    print("download Error for ", song_name)
                    return False
            
                length = int(resp.headers.get('content-length'))
            else:
                resp = requests.Session().get(
                    url, timeout=self.timeout, stream=True, headers=headers, proxies=self.proxies)
                if resp.status_code != 200:
                    print("download Error for ", song_name)
                    return False
                length = int(resp.headers.get('content-length'))
            
            while(length == 0):
                if resp.status_code == 302:
                    realLocation = resp.headers.get("Location")
                    print("地址再次被重定向:", realLocation)
                    resp = requests.Session().get(
                    realLocation, timeout=self.timeout, stream=True, headers=headers,  proxies=self.proxies)
                    length = int(resp.headers.get('content-length'))
                else: 
                    counter['error'] += 1    
                    return False
            
            
            
            label = 'Downloading {} {}kb'.format(song_name, int(length/1024))

            with click.progressbar(length=length, label=label) as progressbar:
                with open(song_name, 'wb') as song_file:
                    for chunk in resp.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            song_file.write(chunk)
                            progressbar.update(1024)
            if counter != None:
                counter["success"] += 1
            return True
        except requests.exceptions.Timeout as err:
            logger.error("%s during download filepath" % err)
            if counter != None:
                counter['error'] += 1
            return False       
    def getSongWithDisplayByUrl(self, song_url,  song_name, display, counter):   
        try:
            resp = self.download_session.get(
                song_url, timeout=self.timeout, stream=True)
            print(resp.headers)
            length = int(resp.headers.get('content-length'))
            label = 'Downloading {} {}kb'.format(song_name, int(length/1024))
            with open(song_name, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)                      
                        display.update(1024 * 100/ length)
            counter["success"] += 1
        except requests.exceptions.Timeout as err:
            logger.error("%s during download filepath" % err)
            counter['error'] += 1
            display.update()
    
    def fetch(self, urladdr):  
        i = 0
        while i < 3:
            try:
                return self.__fetch(urladdr)
            except BaseException as e:
                print("有异常发生" + str(e))
                i = i + 1
        return None
    
    
    def __fetch(self, urladdr):
            res = requests.Session().get(urladdr, headers=headers, proxies=self.proxies)
            res.encoding = 'UTF-8'
            return res.text
    # realName
    def changeBakToRealFile(self, bakFile, realFileName):
        newName=realFileName
        if not os.path.exists(newName):
            os.rename(bakFile, newName)
        else:
            i = 0
            (filepath,shotname,extension) = get_filePath_fileName_fileExt(newName)
            newName= os.path.join(filepath, shotname + "(" + str(i) + ")" + "." + extension)
            while os.path.exists(newName):
                i = i + 1
                newName= os.path.join(filepath, shotname + "(" + str(i) + ")" + "." + extension)
            os.rename(bakFile, newName)
        return newName
                
def get_filePath_fileName_fileExt(filename):
    (filepath,tempfilename) = os.path.split(filename);
    (shotname,extension) = os.path.splitext(tempfilename);
    return filepath,shotname,extension



class MyzcloudParser(object):
    def __init__(self, crawler, baseUrl="https://musify.club/{0}"):
        self.baseUrl=baseUrl
        self.crawler=crawler
    def __getUrl(self, url):
        return self.baseUrl.format(url)
    def __parseArtist(self, bodyContent):
        breakcrumb = bodyContent.find(name="ol", attrs={"class":"breadcrumb"})
        if breakcrumb == None:
            return None
        for child in breakcrumb.children:
            if isinstance(child, Tag):
                meta = child.meta
                if not meta == None and meta["content"] == "2" and  not child.span.string == "Artists" and not child.span.string == "Исполнители":
                    return "Various Artists"
                if not meta == None and meta["content"] == "3":
                    return child.span.string
    def parseAlbumInfoList(self, page):
        bs = BeautifulSoup(page,"html.parser")
        bodyContent = bs.find(id='bodyContent')

        artist=self.__parseArtist(bodyContent)
        albumList=[]
        divAlblumsList=bodyContent.find(id="divAlbumsList")
        for divAlblum in divAlblumsList.children:
            if not isinstance(divAlblum, Tag):
                continue
            dataType=divAlblum["data-type"]
            addrAlbum=divAlblum.a
            url= self.__getUrl(addrAlbum["href"])
            imgAddr=addrAlbum.img
            image=imgAddr["data-src"]
            name=imgAddr["alt"]
            value=divAlblum.p.a.string
            year = ""
            if value != None and value.isdigit():
                year=value
            
            ## 其他label暂时不解析
        
            albumInfo=AlbumInfo(name=name, artist=artist, image=image, url=url, dataType=dataType, category=categoryTypeDic[dataType], year=year)
            albumList.append(albumInfo)
        return albumList

    def _getAlbumInfoByUrl(self, page, albumInfo=None):
        
        if page == None:
            raise Exception("获取网页失败")

        bs = BeautifulSoup(page,"html.parser")
        
        fullName = None
        albumName = None
        if albumInfo != None:
            albumName = albumInfo.name
        
        bodyContent = bs.find(id='bodyContent')
        if bodyContent == None :
            return None
    
        header = bodyContent.header
    
        fullName = header.h1.string
        artist = self.__parseArtist(bodyContent)
        albumInfoDiv = bodyContent.find(name="div", attrs={"class":"row justify-content-center"})
        
        image = ""
        genre = []
        artist = ""
        year=""
        for child in albumInfoDiv.children:
            if isinstance(child, NavigableString):
                continue
            if albumInfo == None and isinstance(child, Tag) and child["class"][0] == "col-auto":
                imgTag = child.img
                albumName = imgTag["alt"]
                image = imgTag["data-src"]
            if isinstance(child, Tag) and child["class"][0] == "col-md-7": 
                genreTag=child.p
                for aChild in genreTag.children:
                    if aChild.string != " " and  aChild.string != "\n":
                        genre.append(aChild.string)
                albumInfoTag =  child.ul
                for uChild in   albumInfoTag.children:
                    if not isinstance(uChild, Tag):
                        continue
                    timeTag = uChild.time
                    if timeTag == None:
                        metaTag = uChild.find(name="meta", attrs={"itemprop":"name"})
                        if metaTag != None:
                            artist=metaTag["content"]
                    else:
                        year = uChild.a.string  
    
        playlistDiv = bodyContent.find(name="div", attrs={"class":"playlist playlist--hover"})
        musicList=[]
    
        for playListItemDiv in playlistDiv.children:
            if isinstance(playListItemDiv, Tag) and playListItemDiv['class'][0] == "playlist__item":
                musicArtist=playListItemDiv['data-artist']
                musicName=playListItemDiv['data-name']
                playerControllDiv=playListItemDiv.find(name="div", attrs={"class":"playlist__control play"})
                if playerControllDiv == None:
                    print(musicName)
                    continue
                musicPostion=playerControllDiv['data-position']
                musicDatatile=playerControllDiv['data-title']
                playHeadingDiv=playListItemDiv.find(name="div", attrs={"class":"playlist__actions"})
                spanDelete=playHeadingDiv.find(name="span", attrs={"class":"badge badge-pill badge-danger"})
                if spanDelete  != None:
                    print(musicName + " is " + spanDelete.string)
                    continue
                headATag=playHeadingDiv.a
                musicUrl=self.__getUrl(headATag["href"])
                print(musicUrl)
                musicInfo = MusicInfo(name=musicName, album=albumName, url=musicUrl, artist=musicArtist, dataTitle=musicDatatile, postion=musicPostion)
                musicList.append(musicInfo)
        
        newAlumInfo = albumInfo
        if albumInfo == None:
            newAlumInfo = AlbumInfo(name=albumName, fullName=fullName, image=image, artist=artist, genre=genre, musicList=musicList, year=year)
        else:
            albumInfo.fullName=fullName
            albumInfo.genre=genre
            albumInfo.musicList=musicList
            if artist == "Various Artists":
                albumInfo.artist=artist
            if year != None or year != "":
                albumInfo.year=year

        for musicInfo in newAlumInfo.musicList:
            musicInfo.downloadDir=newAlumInfo.getAlbumDownloadDir()
        return newAlumInfo
        
    def __parseMusicDownloadInfo(self, page, musicInfo):
        bs = BeautifulSoup(page,"html.parser")
        musicAddressTag=bs.find(name="a", attrs={"itemprop":"audio", "class":"no-ajaxy yaBrowser"})
        if musicAddressTag != None:
            musicInfo.download=musicAddressTag["download"]
            musicInfo.downloadUrl=self.__getUrl(musicAddressTag["href"])
        else:
            print(musicInfo.name)
        return
    def queryAlbumInfoByUrl(self, albumInfo):
        result = albumInfo.loadf()
        if result == True:
            return albumInfo
        
        albumInfo=self._getAlbumInfoByUrl(self.crawler.fetch(albumInfo.url), albumInfo)
        return albumInfo

    def writeAlbumInfo(self, albumInfo):
        logger.info("开始写专辑%s的信息", albumInfo.name)
        json_string = json.dumps(albumInfo, default=obj_dict, ensure_ascii=False)
        with open(albumInfo.getAlbumInfoFile(), "w+", encoding="utf-8") as code:
            code.write(json_string)
        logger.info("完成写专辑%s的信息", albumInfo.name)
        return albumInfo
    def downloadAlbumImage(self, albumInfo):
        try: 
            url=albumInfo.image
            logger.info("开始获取专辑%s的图片", albumInfo.name)
            coverPage= os.path.join(albumInfo.getAlbumDownloadDir(), "cover.jpg")
            if os.path.exists(coverPage):
                return albumInfo
            downloadName=coverPage+".bak"
            
            self.crawler.downloadImage(url, downloadName)
            newName=self.crawler.changeBakToRealFile(downloadName, coverPage)       
            logger.info("完成获取专辑%s的图片", albumInfo.name)
            return albumInfo
        except PermissionError:
            logger.info("获取专辑%s的失败", str(PermissionError))
        except NewConnectionError:
            logger.info("获取专辑%s的失败", str(PermissionError))
        except requests.exceptions.MissingSchema as e:
             logger.info("获取专辑%s的失败", str(e))   

    def loadDownloadCache(self, albumInfo):
        result = albumInfo.loadf()
        return albumInfo
        
    def getMusicDownloadInfo(self, musicInfo):
        musicInfo.downloadUrl = musicInfo.url

        if musicInfo.downloadUrl != None and  musicInfo.downloadUrl != "":
            return musicInfo

        logger.info("开始获取第%s歌曲%s的信息", musicInfo.position, musicInfo.name)



        page=self.crawler.fetch(musicInfo.url)

        return
        if page == None:
            print(musicInfo.name)
            return musicInfo
        
        self.__parseMusicDownloadInfo(page, musicInfo)
        logger.info("完成获取第%s歌曲%s的信息", musicInfo.position, musicInfo.name)
        return musicInfo
#        try:
 #           time.sleep(random.uniform(0.1, 0.5))
 #           musicInfo.downloadUrl = self.crawler.getRealAddress(musicInfo.downloadUrl)
 #       except BaseException as e:
 #           logger.info("获取url失败", str(e))
      
        
    
    def downloadInfoAndSong(self, musicInfo, counter):
        self.getMusicDownloadInfo(musicInfo)
        self.downloadSong(musicInfo, counter)
    
    def downloadSong(self, musicInfo, counter):
        logger.info("开始下载第%s歌曲%s:%s", musicInfo.position, musicInfo.name, musicInfo.downloadUrl)
        try:
            
            song_name = musicInfo.getSongName()
            
            if os.path.exists(song_name):
                if os.path.getsize(song_name) < 10:
                    os.remove(song_name)
                else :
                    logger.info("已经下载过第%s歌曲%s", musicInfo.position, musicInfo.name)
                    return
            print(musicInfo.downloadUrl)
            downloadName=song_name + ".bak"
            time.sleep(random.uniform(0.1,2))
            success=self.crawler.getSongByUrl(song_url=musicInfo.downloadUrl, song_name=downloadName, counter=counter, checkHeader=False)
            if success == True:
                newName=self.crawler.changeBakToRealFile(downloadName, song_name)       
                logger.info("完成下载第%s歌曲%s到%s", musicInfo.position, musicInfo.name, newName)
            else:
               # if os.path.exists(downloadName):
                  #  os.remove(downloadName)
                logger.info("下载第%s歌曲%s失败", musicInfo.position, musicInfo.name)
        except Exception as e:
            print("下载歌曲发生异常%s", str(e))



# 禁止 requests 模组使用系统代理
#os.environ['no_proxy'] = '*'
#logger = set_logger()
#crawler = Crawler(proxies={'http':"http://127.0.0.1:10001", 'https':"https://127.0.0.1:10001"})
crawler = Crawler(proxies={'http':None, 'https':None})
parser = MyzcloudParser(baseUrl="https://musify.club/{0}", crawler=crawler);

def get_args():
    parser = argparse.ArgumentParser(
        usage="python main.py url",
        description="根据专辑或者艺术家地址下载专辑."
    )
    #parser.add_argument('-a', '--url',dest='url', type=str, help="专辑或者艺术家的url")
    parser.add_argument('url', type=str, help="专辑或者艺术家的url")
    parser.add_argument('-t', '--type',dest='type', type=int, default=1, help="1:模拟人操作， 2：批量操作")
    parser.add_argument('-n', '--threadNum',dest='threadNum', type=int, default=1, help="线程数，最大不超过5，容易被封")
    parse_result = parser.parse_args()

    return parse_result
def main():
    
    start = time.time()
    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)
    
    args=get_args()
    
    if args.url == None:
        print("album_url 参数必须传递")
        return 
    
    logger.info("开始获取：%s", args.url)
    
    albumList=[]
    isAlbum=args.url.startswith("https://musify.club/release") or args.url.startswith("https://musify.club/en/release") or args.url.startswith("http://myzcloud.me/album") or args.url.startswith("http://myzcloud.me/en/album")
    if isAlbum:
        albumInfo=parser._getAlbumInfoByUrl(crawler.fetch(urladdr=args.url))
        albumList.append(albumInfo)
    else:
        if not args.url.endswith("albums"):
            args.url = args.url + "/albums"
        page = crawler.fetch(urladdr=args.url)
       # outputFile=CURRENT_PATH+"/albumList.html"
        #page = open(outputFile, 'r').read()
       # with open(outputFile, 'w') as f:
           # f.write(page)
        albumList=parser.parseAlbumInfoList(page)
  
    
    artist=albumList[0].artist
    logger.info("完成专辑列表获取%s信息获取, 供：%s张", artist, len(albumList))
    #json_string = json.dumps(albumList, default=obj_dict)
    #print(json_string)
   
    
 #   print(json.dumps(albumInfo.musicList[0], default=obj_dict))
 #   print(albumInfo.musicList[0])
 

    if artist == None:
        artist = "VA"
 
    download_folder = os.path.join(DOWNLOAD_DIR, validate_file_name(artist))
    if not os.path.exists(download_folder):
        os.mkdir(download_folder)
    if args.type == 1:
        counter = collections.Counter()
        for albumInfo in albumList:
            if albumInfo.dataType == "13" or albumInfo.dataType == "7":
                continue
            logger.info("开始下载专辑%s", albumInfo.name)
            if not isAlbum:
                parser.queryAlbumInfoByUrl(albumInfo)
            else:
                completeAlbumList = parser.loadDownloadCache(albumInfo) 
            
            
            parser.downloadAlbumImage(albumInfo)
            with ThreadPoolExecutor(max_workers=args.threadNum) as executor:
                download = partial(parser.downloadInfoAndSong,  counter=counter)
                musicList = executor.map(download, albumInfo.musicList)
                for musicInfo in musicList:
                    pass
                
            parser.writeAlbumInfo(albumInfo)
            logger.info("完成下载专辑%s", albumInfo.name)

        return

    with ThreadPoolExecutor(max_workers=args.threadNum) as executor:
        counter = collections.Counter()
        completeAlbumList = []
        if not isAlbum:
            completeAlbumList = executor.map(parser.queryAlbumInfoByUrl, albumList)
        else:
            completeAlbumList = executor.map(parser.loadDownloadCache, albumList)

        musicList=[]
        
        for albumInfo in completeAlbumList:
            for musicInfo in albumInfo.musicList:
                musicList.append(musicInfo)
        
        newMusicList  = executor.map(parser.getMusicDownloadInfo, musicList)
        
        for musicInfo in newMusicList:
            if musicInfo.downloadUrl == "":
                logger.log("music get download Info  for %s error", musicInfo.name)
        
        afterDownloadImageList = executor.map(parser.downloadAlbumImage, albumList)
        
#        for album in afterDownloadImageList:
 #           pass
        
    
        afterSavedFileList = executor.map(parser.writeAlbumInfo, albumList)
        for album in afterSavedFileList:
            pass
                    
        logger.info("获取歌曲信息完成，开始下载。")
        download = partial(parser.downloadSong,  counter=counter)
        executor.map(download, musicList)
        logger.info("获取歌曲信息完成，完成下载。")
    



    end = time.time()    
    logger.info("共耗时 %s s", str(end - start))


if __name__=='__main__':
    main()
   # counter = collections.Counter()

    #crawler.getSongByUrl("http://myzcloud.me/song/dl/637217576190066843/fee95f7cbc5c54ed91484d069241c069/43373455", CURRENT_PATH+"/test.mp3", counter)
    #albumInfoList=parser.parseAlbumInfoList(crawler.fetch("http://myzcloud.me/en/artist/366735/paradise-inc/albums"))
    
    #print(json_string)
      
