# 导入SQLite驱动:
import sqlite3
import sys
import os
# 连接到SQLite数据库
# 数据库文件是test.db
# 如果文件不存在，会自动在当前目录创建:

class clipClass(object):
    def __init__(self):
        self.clipID = 'N/A'
        self.aweme_id = 'N/A'
        self.digg_count = 'N/A'
        self.DownloadURL = 'N/A'

    def __str__(self):
        return "xx" + str(self.clipID) + str(self.aweme_id) + str(self.digg_count) + self.DownloadURL


class clipsDB(object):
    def __init__(self):
        self.connectDB()
        self.create_table()
        
    def connectDB(self):
        dir = os.path.split(os.path.realpath(__file__))[0] + '\\'
        self.conn = sqlite3.connect(dir+'clipsdb.db')
        print ("Opened database successfully");
    def closeDB(self):
        self.conn.commit()
        self.conn.close()
    #插入一条记录
    def insertOneClip(self, clip):
        self.connectDB()
        cursor = self.conn.cursor()
        try:
            create_record_cmd="insert into CLIPS (clipID, aweme_id, digg_count, DownloadURL, used0, used1) values ('" + clip.clipID + "', '" + clip.aweme_id + "', '" + clip.digg_count + "', '" + clip.DownloadURL + "', " + "0, " + "0 " + ")"
            
            print(create_record_cmd)
            cursor.execute(create_record_cmd)
            cursor.close()
            self.closeDB()
            return True
        except:
            print('item exsiting')
            cursor.close()
            self.closeDB()
            return False
            
    #获取一条记录
    def getOneClipById(self, clipID):
        self.connectDB()
        cursor = self.conn.cursor()
        try:
            get_record_cmd="SELECT * FROM CLIPS where clipID = '" + clipID + "'"
            
            print(get_record_cmd)
            #尝试查询，如果查询失败，提示没有该元素
            try:
                cursor.execute(get_record_cmd)
            except:
                cursor.close()
                self.closeDB()
                print("no item")
                return False
            #取第一条记录
            clipTuple = cursor.fetchone()
            clipTemp = clipClass()
            clipTemp.clipID = clipTuple[0]
            clipTemp.aweme_id = clipTuple[1]
            clipTemp.digg_count = clipTuple[2]
            cursor.close()
            self.closeDB()
            
            return clipTemp
        except:
            print('getOneClipById Crashed')
            cursor.close()
            self.closeDB()
            return False
    #更新一条记录
    def updateOneClip(self, clip):
        pass
    #判断表存不存在来创建表
    def create_table(self):
        try:
            create_tb_cmd='''
            CREATE TABLE IF NOT EXISTS CLIPS
            (clipID TEXT primary key,
            aweme_id TEXT,
            digg_count TEXT,
            DownloadURL TEXT,
            used0 BOOL,
            used1 BOOL);
            '''
            #主要就是上面的语句
            #print(create_tb_cmd)
            self.conn.execute(create_tb_cmd)
            return True
        except:
            print ('Create table failed')
            return False
            


#self test
if __name__ == "__main__":
    content, opts, args = None, None, []
    clip1 = clipClass()
    clip1.clipID = 'v0200fc10000beropd6lg9jigectmqsg'
    clipDB_instance = clipsDB()
    clipDB_instance.insertOneClip(clip1)
    #clipReturn = clipDB_instance.getOneClipById(clip1.clipID)
    #print(clipReturn)
