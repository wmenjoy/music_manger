
from myzcloud.parser import *

if __name__=='__main__':
    result = parser.search("Baka Beyond")
    #result= parser.getArtistPage("A", 1)
    print(toJsonStr(result))