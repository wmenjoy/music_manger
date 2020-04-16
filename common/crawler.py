
import requests
import click
import logging

from common.utils import logger, toJsonStr



class Crawler(object):
    def __init__(self, headers={}, cookies=None, encoding="UTF-8", proxies=None):
        self.headers = headers
        self.cookies = cookies
        self.encoding=encoding
        self.proxies = proxies
        if self.proxies == None:
            self.proxies = {"http":None, "https":None}
    def __fetch(self, urladdr, params={}, headers={}, cookies=None):
        res = requests.get(urladdr, params=params, headers = headers, cookies = cookies, proxies=self.proxies)
        res.encoding = self.encoding
        return res.text
    
    def fetch(self, urladdr, params={}):  
        i = 0
        while i < 3:
            try:
                return self.__fetch(urladdr, params=params, headers=self.headers, cookies = self.cookies)
            except BaseException as e:
                print("有异常发生" + str(e))
                i = i + 1
        return None
    def getSongByUrl(self, song_url, song_name, counter):       
        i = 0
        while i < 3:
            try:
                return self.__getSongByUrl(song_url, song_name, counter)
            except BaseException as e:
                print("有异常发生" + str(e))
                i = i + 1
                
        return False
    def __getSongByUrl(self, song_url, song_name, counter):
        try:
            
            resp = requests.Session().head(
                    song_url, timeout=self.timeout, stream=True, headers=headers, proxies=self.proxies)
            if resp.status_code == 302:
                realLocation = resp.headers.get("Location")
                print("地址被重定向:", realLocation)
            else:
                realLocation = song_url
            
            resp = requests.Session().get(
                    realLocation, timeout=self.timeout, stream=True, headers=headers, proxies=self.proxies)
            length = int(resp.headers.get('content-length'))
            
            while(length == 0):
                if resp.status_code == 302:
                    realLocation = resp.headers.get("Location")
                    print("地址再次被重定向:", realLocation)
                    resp = requests.Session().get(
                    realLocation, timeout=self.timeout, stream=True, headers=headers,  proxies=self.proxies)
                    length = int(resp.headers.get('content-length'))
                else: 
                    print("服务器返回:", resp.status_code, resp )
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

