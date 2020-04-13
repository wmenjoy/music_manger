from rutracker.rutracker import *
from db.database import *
from pony.orm import *
import argparse

def get_args():
    parser = argparse.ArgumentParser(
        usage="python rutracker.py url",
        description="根据专辑或者艺术家地址下载专辑."
    )
    #parser.add_argument('-a', '--url',dest='url', type=str, help="专辑或者艺术家的url")
    parser.add_argument('id', type=int, default=1727, help="topic或者forumId")
    parser.add_argument('-t', '--type',dest='type', type=int, default=1, help="1:forumId， 2：topicId, 3:subForumId")
    parser.add_argument('-q', '--query',dest='query', type=int, default=0, help="辅助查询")
   # parser.add_argument('-n', '--threadNum',dest='threadNum', type=int, default=1, help="线程数，最大不超过5，容易被封")
    parse_result = parser.parse_args()

    return parse_result

def main():
    #db.drop_table(table_name="rutracker_forum_item_info", if_exists=True, with_all_data=True)
    #db.drop_table(table_name="rutracker_forum_info", if_exists=True, with_all_data=True)
    #db.drop_table(table_name="rutracker_album_download_info", if_exists=True, with_all_data=True)
    db.generate_mapping(create_tables=True,check_tables=True)
    
    args=get_args()
    

    #page = rutracker.__getPage(url="https://rutracker.org/forum/viewtopic.php?t=5640504")
    #outputFile=CURRENT_PATH+"/list.html"
    #sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') 
    #with open(outputFile, 'w', encoding="windows-1251") as f:
    #    f.write(page)
    #page = open(outputFile, 'r', encoding="windows-1251").read()
    #rutracker.parseAlbumInfo(page)
    if args.type == 1:
        forum = rutracker.getForumAllPage(args.id)
    elif args.type == 2:
        rutracker.parseAlbumInfo(args.id)
    elif args.type == 3:
        navList=rutracker.getSubForumList(args.id)
        logger.info("%s", toJsonStr(navList))
        rutracker.saveSubForumInfo(navList)
    elif args.type == 4:
        logger.info("同步所有Category")
        navList=rutracker.getAllSubForumInfo()
        logger.info("同步所有Category结束")

    elif args.type == 5:
        subForumList=rutracker.getAllSubForumInfo()
        length = len(subForumList)
        i = 0
        logger.info("同步论坛总数：%d", length)
        for nav in subForumList:
            logger.info("同步子论坛%d:%s:%s", i, nav.forumId, nav.name)
            navList=rutracker.getSubForumList(nav.forumId)
            rutracker.saveSubForumInfo(navList)
            logger.info("同步子论坛%d:%s:%s结束", i, nav.forumId, nav.name)
            i = i + 1


    #jsonStr = toJsonStr(forum)
    
   # Rutracker.saveForumInfo(forum)
   
    if args.query == 1:
        with db_session:
            result=orm.select(c.torTopicTitle for c in RutrackerForumItemPo)[:]
            result.show()
    elif args.query == 2:
        with db_session:
            result=orm.select(c for c in RutrackerForumPo)[:]
            result.show()
    #new = json.loads(str)
    
   # print(new["naviList"][0]["name"])
   # print(jsonStr)
    
if __name__ == "__main__":
   main()  