# -*- coding: utf-8 -*-

import os
import sys, getopt
import string
sys.path.append("..")
#print(sys.path)
import hashlib
import codecs
import requests
import re
from six.moves import queue as Queue
from threading import Thread
import json
from clipDB.clipsdb import clipsDB as clipsDB
from clipDB.clipsdb import clipClass as clipClass
from getdouyin import KuaiYinShi

# Setting timeout
TIMEOUT = 10

# Retry times
RETRY = 5

# Numbers of downloading threads concurrently
THREADS = 10

userVideoType = 'all'
diggLevelNumber = 5000

HEADERS = {
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
}

PC_HEADERS = {
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
}

FAILED_FILE_MD5 = '6419a414275112dcc2e073f62a3ce91e'


class DownloadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            medium_type, uri, download_url, target_folder = self.queue.get()
            self.download(medium_type, uri, download_url, target_folder)
            self.queue.task_done()
    def videoDowloadedCheck(self, fileName):
        print('file name is '+fileName)
        clipDB_instance = clipsDB()
        videoInsetSuccessFlag = clipDB_instance.getOneClipById(fileName)
        if videoInsetSuccessFlag == False: 
            print("video %s downloaded before!!" % fileName)
            return False
        else:
            return True
    def videoLogIntoDB(self, fileName):
        clip1 = clipClass()
        clip1.clipID = fileName
        clipDB_instance = clipsDB()
        clipDB_instance.insertOneClip(clip1)
        
        print('input video to DB')
        

    def download(self, medium_type, uri, download_url, target_folder):
        if medium_type == 'image':
            self._download(uri, 'image', download_url, target_folder)
        elif medium_type == 'video':
            download_url = 'https://aweme.snssdk.com/aweme/v1/play/?{0}'
            download_params = {
                'video_id': uri,
                'line': '0',
                'ratio': '720p',
                'media_type': '4',
                'vr_type': '0',
                'test_cdn': 'None',
                'improve_bitrate': '0'
            }
            download_url = download_url.format(
                '&'.join(
                    [key + '=' + download_params[key] for key in download_params]
                )
            )
            self._download(uri, 'video', download_url, target_folder)
        elif medium_type == 'videowm':
            self._download(uri, 'video', download_url, target_folder)
            download_url = 'https://aweme.snssdk.com/aweme/v1/playwm/?video_id={0}&line=0'
            download_url = download_url.format(uri)
            res = requests.get(download_url, headers=HEADERS, allow_redirects=False)
            download_url = res.headers['Location']
            self._download(uri, 'video', download_url, target_folder)
        elif medium_type == 'all':
            download_url = 'https://aweme.snssdk.com/aweme/v1/play/?{0}'
            download_params = {
                'video_id': uri,
                'line': '0',
                'ratio': '720p',
                'media_type': '4',
                'vr_type': '0',
                'test_cdn': 'None',
                'improve_bitrate': '0'
            }
            download_url = download_url.format(
                '&'.join(
                    [key + '=' + download_params[key] for key in download_params]
                )
            )
            self._download(uri, 'video', download_url, target_folder)

    def _download(self, uri, medium_type, medium_url, target_folder):
        file_name = uri
        if medium_type == 'video':
            file_name += '.mp4'
        elif medium_type == 'image':
            file_name += '.jpg'
            file_name = file_name.replace("/", "-")
        else:
            return

        file_path = os.path.join(target_folder, file_name)
        fileExistFlag = self.videoDowloadedCheck(file_name)
        print(str(fileExistFlag))
        if not (os.path.isfile(file_path) or fileExistFlag):#如果文件不存在，即下载
            print("Downloading %s from %s.\n" % (file_name, medium_url))
            retry_times = 0
            while retry_times < RETRY:
                try:
                    resp = requests.get(medium_url, headers=HEADERS, stream=True, timeout=TIMEOUT)
                    if resp.status_code == 403:
                        retry_times = RETRY
                        print("Access Denied when retrieve %s.\n" % medium_url)
                        raise Exception("Access Denied")
                    with open(file_path, 'wb') as fh:
                        for chunk in resp.iter_content(chunk_size=1024):
                            fh.write(chunk)
                        self.videoLogIntoDB(file_name)
                    break
                except:
                    pass
                retry_times += 1
            else:
                try:
                    os.remove(file_path)
                except OSError:
                    pass
                print("Failed to retrieve %s from %s.\n" % (file_name, medium_url))
                

class CrawlerScheduler(object):

    def __init__(self, items):
        self.all = items
        self.queue = Queue.Queue()
        self.scheduling()


    def scheduling(self):
        for x in range(THREADS):
            worker = DownloadWorker(self.queue)
            worker.daemon = True
            worker.start()

        for item in self.all:
            self.queue.put(('all', item.clipID, item.DownloadURL, 'all'))
            self.queue.join()


if __name__ == "__main__":
    content, opts, args = None, None, []
    for i in range(0,10,1):
        L = KuaiYinShi.getClipsList()
        LL = L[:]
        #print('8888888888888888888888888888888888888888888')
        #print(*LL, sep = ", ") 
        for item in L:
            #print("item.digg_count %s" % item.digg_count)
            if not (item.digg_count>diggLevelNumber):
                LL.remove(item)
                #print('remove')
        #print('8888888888888888888888888888888888888888888')
        #print(*LL, sep = ", ") 
        CrawlerScheduler(LL)
