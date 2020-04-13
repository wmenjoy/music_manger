


'''
  用来记录一首歌的信息
'''
class MusicInfo(object):
    def __init__(self, name, album, url, artist="", postion="0", **tag = {}):
        self.name = name
        self.url = url
        self.album = album
        self.artist = artist
        self.position = postion
        self.tag = tag
