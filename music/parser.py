
'''
解析的基类
'''
class Parser(object):
    def __init__(self, name, baseUrl):
        self.name = name
        self.baseUrl = baseUrl
    
    def getAblumListByArtist(self):
        pass