from common.crawler import Crawler
from rutracker.model import *
from common.utils import logger, toJsonStr
import json
import os
import sys
import io
import time
import random
from bs4 import BeautifulSoup 
from bs4.element import NavigableString, Tag
from db.database import *
from db.rutracker import *
import re
cookies="bb_guid=d75Tzc4cGg1T; bb_ssl=1; bb_session=0-31907274-Ah8gtWphowq8R6NgaqgB; bb_t=a%3A50%3A%7Bi%3A5879043%3Bi%3A1586580544%3Bi%3A5879038%3Bi%3A1586579261%3Bi%3A4135450%3Bi%3A1586576432%3Bi%3A4527226%3Bi%3A1586566522%3Bi%3A5675561%3Bi%3A1586563241%3Bi%3A5790215%3Bi%3A1586551045%3Bi%3A5878971%3Bi%3A1586548698%3Bi%3A2872119%3Bi%3A1586545975%3Bi%3A1126419%3Bi%3A1586545896%3Bi%3A5878569%3Bi%3A1586545075%3Bi%3A5026501%3Bi%3A1586545053%3Bi%3A3502497%3Bi%3A1586545005%3Bi%3A5878440%3Bi%3A1586544948%3Bi%3A3686412%3Bi%3A1586541938%3Bi%3A4648572%3Bi%3A1586539229%3Bi%3A5878526%3Bi%3A1586538824%3Bi%3A5250805%3Bi%3A1586538787%3Bi%3A5878865%3Bi%3A1586537747%3Bi%3A3614595%3Bi%3A1586537280%3Bi%3A4347519%3Bi%3A1586536421%3Bi%3A5878060%3Bi%3A1586535699%3Bi%3A4153859%3Bi%3A1586535251%3Bi%3A5224213%3Bi%3A1586534523%3Bi%3A4061105%3Bi%3A1586533785%3Bi%3A5581451%3Bi%3A1586533545%3Bi%3A3781847%3Bi%3A1586532653%3Bi%3A4702488%3Bi%3A1586532602%3Bi%3A5051447%3Bi%3A1586531994%3Bi%3A5051581%3Bi%3A1586531919%3Bi%3A5878792%3Bi%3A1586531546%3Bi%3A4766060%3Bi%3A1586531196%3Bi%3A3951790%3Bi%3A1586528658%3Bi%3A2121048%3Bi%3A1586525189%3Bi%3A5208782%3Bi%3A1586525161%3Bi%3A5878727%3Bi%3A1586524559%3Bi%3A4665138%3Bi%3A1586524180%3Bi%3A5878197%3Bi%3A1586521146%3Bi%3A5878065%3Bi%3A1586519906%3Bi%3A5433670%3Bi%3A1586519825%3Bi%3A4603571%3Bi%3A1586517549%3Bi%3A2915239%3Bi%3A1586515839%3Bi%3A5878607%3Bi%3A1586512620%3Bi%3A5878590%3Bi%3A1586511131%3Bi%3A5878587%3Bi%3A1586510784%3Bi%3A5802182%3Bi%3A1586509989%3Bi%3A5762642%3Bi%3A1586509850%3Bi%3A5181610%3Bi%3A1586509366%3Bi%3A5878560%3Bi%3A1586508330%3Bi%3A5878555%3Bi%3A1586507819%3Bi%3A4344078%3Bi%3A1586507464%3B%7D; opt_js={%22only_new%22:0%2C%22h_flag%22:0%2C%22h_av%22:0%2C%22h_rnk_i%22:0%2C%22h_post_i%22:0%2C%22h_smile%22:0%2C%22h_sig%22:0%2C%22sp_op%22:0%2C%22tr_tm%22:0%2C%22h_cat%22:%22%22%2C%22h_tsp%22:0%2C%22h_ta%22:0}; _ym_d=1585370144; _ym_uid=15738641931040225246; __cfduid=dbcf260767d865c1710f9b888239991ae1585373121; _ym_hostIndex=0-2%2C1-1; _ym_isad=2; _ym_wasSynced=%7B%22time%22%3A1586622210956%2C%22params%22%3A%7B%22eu%22%3A0%7D%2C%22bkParams%22%3A%7B%7D%7D"
#cookies="bb_guid=d75Tzc4cGg1T; bb_ssl=1; bb_session=0-31907274-Ah8gtWphowq8R6NgaqgB; opt_js={%22only_new%22:1%2C%22h_flag%22:0%2C%22h_av%22:0%2C%22h_rnk_i%22:0%2C%22h_post_i%22:0%2C%22h_smile%22:0%2C%22h_sig%22:0%2C%22sp_op%22:0%2C%22tr_tm%22:0%2C%22h_cat%22:%22%22%2C%22h_tsp%22:0%2C%22h_ta%22:0}; bb_t=a%3A50%3A%7Bi%3A5875985%3Bi%3A1586128241%3Bi%3A2391152%3Bi%3A1586107345%3Bi%3A5872006%3Bi%3A1586107220%3Bi%3A5875440%3Bi%3A1586105066%3Bi%3A5875498%3Bi%3A1586104820%3Bi%3A5876228%3Bi%3A1586099834%3Bi%3A5876217%3Bi%3A1586098677%3Bi%3A5586279%3Bi%3A1586090397%3Bi%3A5107865%3Bi%3A1586085404%3Bi%3A5876081%3Bi%3A1586084330%3Bi%3A5876061%3Bi%3A1586082165%3Bi%3A5224358%3Bi%3A1586081899%3Bi%3A5876058%3Bi%3A1586081846%3Bi%3A2715186%3Bi%3A1586081810%3Bi%3A5875082%3Bi%3A1586081558%3Bi%3A5876050%3Bi%3A1586080879%3Bi%3A5876040%3Bi%3A1586080194%3Bi%3A5874286%3Bi%3A1586080176%3Bi%3A4722474%3Bi%3A1586080100%3Bi%3A5876028%3Bi%3A1586079406%3Bi%3A5876027%3Bi%3A1586079321%3Bi%3A5813883%3Bi%3A1586078314%3Bi%3A4202396%3Bi%3A1586078175%3Bi%3A5216687%3Bi%3A1586078169%3Bi%3A5812159%3Bi%3A1586077996%3Bi%3A5502408%3Bi%3A1586077143%3Bi%3A4575696%3Bi%3A1586076839%3Bi%3A2641781%3Bi%3A1586076640%3Bi%3A5875268%3Bi%3A1586076047%3Bi%3A5245595%3Bi%3A1586074646%3Bi%3A5875952%3Bi%3A1586073638%3Bi%3A5875950%3Bi%3A1586073399%3Bi%3A5875948%3Bi%3A1586073157%3Bi%3A5484008%3Bi%3A1586072845%3Bi%3A5547622%3Bi%3A1586070325%3Bi%3A5875911%3Bi%3A1586070059%3Bi%3A3330271%3Bi%3A1586067407%3Bi%3A5875868%3Bi%3A1586062692%3Bi%3A5731107%3Bi%3A1586061234%3Bi%3A5875863%3Bi%3A1586061071%3Bi%3A5875862%3Bi%3A1586060944%3Bi%3A5813840%3Bi%3A1586044790%3Bi%3A3002619%3Bi%3A1586042013%3Bi%3A5340534%3Bi%3A1586037150%3Bi%3A5875179%3Bi%3A1586036577%3Bi%3A5729085%3Bi%3A1586036161%3Bi%3A5875802%3Bi%3A1586033772%3Bi%3A3924101%3Bi%3A1586031209%3Bi%3A5805722%3Bi%3A1586030008%3Bi%3A5476038%3Bi%3A1586027192%3B%7D; _ym_d=1585370144; _ym_uid=15738641931040225246; __cfduid=dbcf260767d865c1710f9b888239991ae1585373121; _ym_isad=2; _ym_wasSynced=%7B%22time%22%3A1586134735836%2C%22params%22%3A%7B%22eu%22%3A0%7D%2C%22bkParams%22%3A%7B%7D%7D; _ym_hostIndex=0-3%2C1-2"
cookies2 = dict(map(lambda x:x.split('='),cookies.split(";")))


headers={
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Mode":"navigate",
    "Sec-Fetch-User":"?1",
    "Sec-Fetch-Sit":"None",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
    "Upgrade-Insecure-Requests":"1",
    "Cache-Control":"max-age=0",
    "Connection":"keep-alive",
    "Sec-Fetch-Dest":"document"
}

class Rutracker(object):
    def __init__(self, baseUrl):
        self.baseUrl = baseUrl
        self.crawler = Crawler(headers=headers, cookies=cookies2, encoding='windows-1251', proxies={'http':"http://127.0.0.1:10001", 'https':"https://127.0.0.1:10001"})
    
    def __getPage(self, url):
        return self.crawler.fetch(urladdr=url)
    
    def parseTorTitle(self, title):
        index = title.find(")")
        if index == -1:
            logger.warn("解析错误, 没有genre：%s", title)
            return
        
        genre = title[1:index]
        
        remains = title[index + 1:]
         
        albumName = None
        
      
    
        if remains.find("дискография")  == -1 and remains.find("Дискография") == -1 and  remains.find("Коллекция") == -1 and remains.find("Discography") == -1: 
            groups=re.match("^(\([^\)]+\))\s*(?:\[[^\]]+\]\s*)?([^-:]+)\s*-\s*(.*)\s*-\s*([0-9]+(?:/[0-9]+)?)\s*,(.*)", title)
            if groups:
               # logger.info(" %s:%s:%s:%s:%s",groups.group(1),groups.group(2),groups.group(3),groups.group(4),groups.group(5))
                pass
            else:
                #logger.warn("解析错误, 没有genre：%s", title)
                pass
        else:
            key="(?:Официальная дискография|Почти полная дискография|Дискография|Полная студийная дискография|Discography|Studio Discography|Неофициальная дискография|Studio Discography|Unofficial Discography|Полная Дискография|Collection/Коллекция|Дискография|Студийная дискография|FULL Discography|Full Discography|Discography/Дискография|Студийная дискография|Коллекция|Discography|дискография|Дискография|Дискография|Официальная Дискография|Двухальбомная дискография)"
            noKey="(?=[-:—–,\(·/]\s*" + key + ")"
            musicFormat="(?:FLAC|Flac|APE|MP3|flac|WavPack|WAVPack|ISO.WAVPack|Ape&Wav)"
            groups = re.match("^(?:\[[^\]]+\]\s*)?\(([^\)]+)\)\s*(?:\[[^\]]+\]\s*)?(.*"+ noKey +")[-:–—,\(·/]\s*(" + key + ".*)(?:\[|\()?.*([0-9]{4})\s*[-,/—]\s*([0-9]{4}).*(?=\[|\))?.*("+musicFormat+".*)$", title)
            if groups:
                #logger.info(" %s:%s:%s:%s:%s:%s",groups.group(1),groups.group(2),groups.group(3),groups.group(4),groups.group(5),groups.group(6))
                return
            groups = re.match("^(?:\[[^\]]+\]\s*)?\(([^\)]+)\)\s*(?:\[[^\]]+\]\s*)?(.*"+ noKey +")[-:—,\(·/]\s*(" + key + ".*).*("+musicFormat+".*)$", title)    
            if groups :
               # logger.info(" %s:%s:%s:%s:%s:%s",groups.group(1),groups.group(2),groups.group(3),groups.group(4),groups.group(5),groups.group(6))
                pass
            else:
                logger.warn("解析错误, %s", title)
  
    def getForumInfoByPage(self, id, page=0):
        forum = RutrackerForum(forumId=id)
        url=forum.url
        if page > 0:
            url = forum.url + "&start=" + str(page * 50)

        contentPage = self.__getPage(url)
        #outputFile=CURRENT_PATH+"/forum.html"
        #with open(outputFile, 'w', encoding="windows-1251") as f:
        #    f.write(page)
        #page = open(outputFile, 'r', encoding="windows-1251").read()
        self.__parseForum(contentPage, forum, page == 0)
        return forum
    
    def __parseNavgateInfo(self, contentTag, forum):
        #取第一个元素
        tableNav = contentTag.find(name="table", attrs={"class":"w100"})
        tdNav = tableNav.td
        h1MainTitle=tdNav.h1
        aMainTitle=h1MainTitle.a
        forum.name = aMainTitle.text
        divNavigate=tdNav.div
        aNavItems = tdNav.findAll(name="a", attrs={"class":"pg"})
        if aNavItems != None:
            navItems=[]
            for aNavItem in aNavItems:
                navItems.append(aNavItem.text)
            if len(navItems) >= 2:
                forum.totalPage = int(navItems[len(navItems) - 2])
        
        tableForumNav=tdNav.find(name="table", attrs={"class":"w100"})
        
        tdForumNav=tableForumNav.find(name="td", attrs={"class":"nav"})
        aNavItems = tdForumNav.findAll(name="a")
        lastLink=""
        lastId=-2
        naviList=[]
        for aNavItem in aNavItems:
            name=aNavItem.text
            link = aNavItem["href"]
            index =link.find("index.php")
            id = -1
            if name == "Главная":
                id = -2
            elif index != -1:
                id = link[index + len("index.php?c="):]
            else:
                id = link[len("viewforum.php?f="):]
            navItem = NaviItem(forumId=id, name=name, url=RutrackerConfig.url.format(link), parentForumId=lastId, parentUrl=RutrackerConfig.url.format(lastLink))
            lastId=id
            lastLink=link
            naviList.append(navItem)
        forum.naviList = naviList
        cNav=naviList[len(naviList) - 1]
        forum.parentForumId=cNav.parentForumId
        forum.parentUrl=RutrackerConfig.url.format(cNav.parentUrl)
    def __parseLastReplyInfo(self, tdLastPost):
        lastReplyInfo=RutrakcerTopicLastPostInfo()
        for child in tdLastPost.children:
            if not isinstance(child, Tag):
                continue
            if not child.has_attr("style"):
                lastReplyInfo.lastPostTime=child.text
            else:
                for aChild in child.children:
                    if not isinstance(aChild, Tag):
                        continue
                    href=aChild["href"]
                    if href.find("viewtopic") != -1:
                        lastReplyInfo.lastPostLink=RutrackerConfig.url.format(href)
                    else:
                        lastReplyInfo.lastPostUser=aChild.text
        return lastReplyInfo
    def __parseTopicReplies(self, trForumItem):
        spanNReplies=trForumItem.find(name="span", attrs={"title":"Ответов"})
        spanNDownload=trForumItem.find(name="span", attrs={"title":"Ответов"})
        if spanNReplies == None and spanNDownload == None:
            return None
        return RutrakcerTopicReplies(spanNReplies.text, spanNDownload.text)
    def __parseTorrentInfo(self, trForumItem):
        seeders = ""
        leechers=""
        spanSeeders=trForumItem.find(name="span", attrs={"title":"Seeders", "class":"seedmed"});
        if spanSeeders != None:
            seeders=spanSeeders.b.text
        spanLeechers=trForumItem.find(name="span", attrs={"title":"Leechers", "class":"leechmed"})
        if spanLeechers != None:
            leechers=spanLeechers.b.text
        fileSize=""
        spanFileSize=trForumItem.find(name="a", attrs={ "class":"small f-dl dl-stub"})
        if spanFileSize != None:
            fileSize = spanFileSize.text
        torrentInfo=RutrackerTorrentInfo(seeders=seeders, leechers=leechers, fileSize=fileSize)
        return torrentInfo
    def __parseForum(self, page, forum, loadPage=True):
        bs = BeautifulSoup(page,"html.parser")
        divPageContent = bs.find(id="main_content_wrap")
        if divPageContent == None:
            logger.info("下载页面出错:%s", bs.find(name="div", attrs={"class":"msg-main"}).text)
            forum.error = True
            return
        if loadPage:
            self.__parseNavgateInfo(divPageContent, forum)
        
        tableTor=divPageContent.find(name="table", attrs={"class":"vf-tor"})
        if tableTor == None:
            return
        forumItemList=[]
        for trForumItem in tableTor.children:
            if not isinstance(trForumItem, Tag) or trForumItem.name != "tr" or not trForumItem.has_attr("id")  or trForumItem["id"] == "" or not trForumItem.has_attr("data-topic_id"):
                continue
            topicId=trForumItem["data-topic_id"]
            
            id=trForumItem["id"]
            imgTopicIcon=trForumItem.img
            topicIcon=imgTopicIcon["src"]
            divColumTitle=trForumItem.find(name="td", attrs={"class":"vf-col-t-title"})
      
            divTorTopic=divColumTitle.div
            spanApprovedLabel=divTorTopic.span
            if spanApprovedLabel != None:
                approvedLabel=spanApprovedLabel.text
            else :
                logger.info("no approvedLabel info for %s", topicId)
                continue
            spanAuthLabel=divTorTopic.find(name="span", attrs={"class":"ttp-label ttp-auth"})
            authLabel=""
            if spanAuthLabel != None:
                authLabel=spanAuthLabel.text
        
            torTopicTitle=divTorTopic.find(name="a", attrs={"id": "tt-"+topicId}).text
                
            divtopicAuthor=divColumTitle.find(name="a", attrs={"class":"topicAuthor"})
            if divtopicAuthor != None:
                topicAuthor = divtopicAuthor.text
            else:
                topicAuthor=divColumTitle.find(name="div", attrs={"class":"topicAuthor"}).text
            torrentInfo=self.__parseTorrentInfo(trForumItem)
            topicReplies=self.__parseTopicReplies(trForumItem)
            tdLastPost=trForumItem.find(name="td", attrs={"class":"vf-col-last-post"})
            lastPostInfo=self.__parseLastReplyInfo(tdLastPost)
            forumItem=RutrackerForumItem(topicId=topicId, topicIcon=topicIcon, approvedLabel=approvedLabel, authLabel=authLabel, rutrackerForumId=forum.forumId,
                                         torTopicTitle=torTopicTitle, topicAuthor=topicAuthor, torrentInfo=torrentInfo, topicReplies=topicReplies,
                                         lastPostInfo=lastPostInfo)
            forumItemList.append(forumItem)

        forum.forumItemList=forumItemList 
        
    def __getRealUrl(self, path):
        return "https://rutracker.org/" + path
    def parseMusicTags(self, spanTag, idc):
        lastKey=None
        for child in spanTag.children:
            if  not child.string == None and not str.strip(child.string) == "":
                value=str.strip(child.string)
                if value.startswith(":"):
                    idc[lastKey]= value
                elif "Треклист" == value:
                    break
                else:
                    lastKey = value
                
    def parseAlbumInfo(self, page):
        bs = BeautifulSoup(page,"html.parser")
        musicAddressTag=bs.find(name="div", attrs={ "class":"post_body"})
        print(musicAddressTag.text)
        spanTags = musicAddressTag.findAll(name="span", attrs={"class":"post-font-serif1"})
        idc={}
        self.parseMusicTags(musicAddressTag, idc)
        lastKey=None       
        if spanTags != None:
            for spanTag in spanTags:
                hasText=False
                
                for child in spanTag.children:
                    if child.name == "span" :
                        for clazz in child["class"]:
                            if clazz == "post-b":
                                hasText = True
                                break
                if hasText == True:
                    self.parseMusicTags(spanTag, idc)
                else:
                    for child in spanTag.children:
                       if child.name == "span":
                           self.parseMusicTags(child, idc) 
        print(idc)  
        
        maginnetA = bs.find(name="a", attrs={"class":"magnet-link"})
        if maginnetA != None:
            print("magnet:{0}".format(maginnetA["href"]))
        else:
            print("not found")
    
    def getForumAllPage(self, id, start=1):
        firstForumInfo = self.getForumInfoByPage(id=id)
        
        if hasattr(firstForumInfo, "error") and firstForumInfo.error != None:
            return
        totalPage= firstForumInfo.totalPage
        logger.info("下载第1页, 共%d",totalPage )
        self.saveForumInfo(firstForumInfo, saveForumNavi=True)
        
        for i in range(start, totalPage - 1):
            time.sleep(random.uniform(0.1, 1))
            logger.info("下载第{0}页".format(i + 1))
            forumInfo= self.getForumInfoByPage(id, i)
            self.saveForumInfo(forumInfo, saveForumNavi=False)
    def __parseNavList(self, page):
        tableForumNav=page.find(name="table", attrs={"class":"w100"})
        tdForumNav=tableForumNav.find(name="td", attrs={"class":"nav"})
        aNavItems = tdForumNav.findAll(name="a")
        lastLink=""
        lastId=-2
        naviList=[]
        for aNavItem in aNavItems:
            name=aNavItem.text
            link = aNavItem["href"]
            index =link.find("index.php")
            id = -1
            if name == "Главная":
                id = -2
            elif index != -1:
                id = link[index + len("index.php?c="):]
            else:
                id = link[len("viewforum.php?f="):]
            navItem = NaviItem(forumId=id, name=name, url=RutrackerConfig.url.format(link), parentForumId=lastId, parentUrl=RutrackerConfig.url.format(lastLink))
            lastId=id
            lastLink=link
            naviList.append(navItem)
        return naviList
    def getSubForumList(self, id, parentId=-9999):
        url = RutrackerConfig.forumUrl.format(id)
        contentPage = self.__getPage(url)
        bs = BeautifulSoup(contentPage,"html.parser")
        divPageContent = bs.find(id="main_content_wrap")
        if divPageContent == None:
            logger.info("下载页面出错:%s", bs.find(name="div", attrs={"class":"msg-main"}).text)
            return 
        naviList = []
        name = divPageContent.find(name="h1", attrs={"class":"maintitle"}).text
        currentNav = NaviItem(forumId=id, name=name)
        
        if parentId != -9999:
            currentNav.parentForumId = parentId
            currentNav.url = url
            currentNav.parentUrl=RutrackerConfig.forumUrl.format(parentId),
        else:
            tableNav = divPageContent.find(name="table", attrs={"class":"w100"})
            tdNav = tableNav.td
            forumNavList=self.__parseNavList(tableNav)
            cNav=forumNavList[len(forumNavList) - 1]
            currentNav.parentForumId=cNav.parentForumId
            naviList.append(forumNavList[len(forumNavList) - 2])
        naviList.append(currentNav)
        h4ForumList=divPageContent.findAll(name="h4", attrs={"class":"forumlink"})
        for h4Forum in h4ForumList:
            aLink = h4Forum.a
            link = aLink["href"]
            cid = link[len("viewforum.php?f="):]
            name = aLink.text
            parentForumId=id
            parentForumUrl=url
            nav=NaviItem(forumId=cid, name=name, url=RutrackerConfig.url.format(link), parentForumId=parentForumId, parentUrl=parentForumUrl)
            naviList.append(nav)
        return naviList
    @staticmethod
    def saveForumInfo(forum, saveForumNavi=False):
        
        if saveForumNavi:
            if forum.naviList != None:
                for nav in forum.naviList:
                    nav.persist()
            forum.persist()
        
        if forum.forumItemList != None:
            for item in forum.forumItemList:
                item.persist()
    @staticmethod
    def saveSubForumInfo(naviList):
        if naviList != None:
            for nav in naviList:
                nav.persist()
            for nav in naviList:
                nav.updateLink()
    
    def getAllSubForumInfo(self, saveColume=False):
        url="https://rutracker.org/forum/index.php"
        contentPage = self.__getPage(url)
        bs = BeautifulSoup(contentPage,"html.parser")
        divPageContent = bs.find(id="categories-wrap")
        if divPageContent == None:
            logger.info("下载页面出错:%s", bs.find(name="div", attrs={"class":"msg-main"}).text)
            return 
        
        divCategoryList=divPageContent.findAll(name="div", attrs={"class":"category"})
        cateGoryList=[]
        naviList=[]
        for divCategory in divCategoryList:
            aTitle=divCategory.h3.a
            categoryTitle=aTitle.text
            categoryLink =aTitle["href"]
            categoryUrl=RutrackerConfig.url.format(categoryLink)
            categoryId = divCategory["id"][len("c-"):]
            catagoryNav=NaviItem(forumId=categoryId, name=categoryTitle, 
                                 url=categoryUrl, 
                                 parentForumId=-2, parentUrl=url)
            cateGoryList.append(catagoryNav)
            h4ForumList=divCategory.findAll(name="h4", attrs={"class":"forumlink"})
            for h4Forum in h4ForumList:
                aLink = h4Forum.a
                link = aLink["href"]
                cid = link[len("viewforum.php?f="):]
                name = aLink.text
                parentForumId=categoryId
                parentForumUrl=categoryUrl
                nav=NaviItem(forumId=cid, name=name, url=RutrackerConfig.url.format(link), parentForumId=parentForumId, parentUrl=parentForumUrl)
                naviList.append(nav)
        if saveColume:
            self.saveSubForumInfo(cateGoryList)
            self.saveSubForumInfo(naviList)
        return naviList
rutracker=Rutracker(baseUrl="https://rutracker.org/")
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
  
    