# -*- coding: utf-8 -*-
import requests as rq
import json
import time
import os
import get_video_id as kysid
import re
import sys
sys.path.append("C:\\Users\\Globalock1\\Desktop\\randomfile\\autoyou")
from clipDB.clipsdb import clipsDB as clipsDB
from clipDB.clipsdb import clipClass as clipClass


class KuaiYinShi():
    def __init__(self, siteType):
        pass
    @staticmethod
    def getClipsList():
        ClipList = []

        millis = int(round(time.time() * 1000))
        print(millis)
        test_url = "https://kuaiyinshi.com/api/dou-yin/recommend/?callback=showData&_="+str(millis)
        s = rq.Session()
        my_headers = {
            'authority': 'kuaiyinshi.com',
            'path': '/api/dou-yin/recommend/?callback=showData&_='+str(millis),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',        
            'content-type':'application/javascript'
            } 
        response = s.get(test_url, headers = my_headers)
        response.encoding='utf-8'
        html = response.text
        res = html[9:-2]
        contentJson = json.loads(res)
        js = json.dumps(contentJson, sort_keys=True, indent=4, separators=(',', ':'))
        #print(js, file = f)
        data_list = contentJson.get('data', [])
        for data in data_list:
            clip = clipClass()
            #print(data['video_url'])
            old_id = (re.findall('(?<=video_id=).*?(?=&line)', data['video_url']))[0]
            #print(old_id)
            new_id = kysid.kuaiyinshi_id(old_id)
            #print(new_id)
            data['video_url'] = data['video_url'].replace(old_id, new_id).replace('playwm', 'play')
            #print(data['video_url'])
            clip.clipID = new_id
            clip.digg_count = data['statistics']['zan']
            clip.DownloadURL = 'http:' + data['video_url']
            ClipList.append(clip)
        #print(*ClipList, sep = ", ") 
        return ClipList
           
 

f = open('js.txt','w+')
if __name__ == '__main__':
    L = KuaiYinShi.getClipsList()
    print(*L, sep = ", ") 
        
