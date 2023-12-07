import selenium
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import os
import re
import requests
from operator import itemgetter

class TestKeyWords():
    
    source_file = 'demo.m3u'
    finalFile = "result.m3u"

    #初始化
    def __init__(self):
        self.main()
        
        
        
    # 从文件列表中获取频道名列表
    def getChannelNameList(self):
        # 文件路径
        strings = []
        pattern = r",(.*?)\n"
        with open(self.source_file, 'r') as file:
            for line in file:
                match = re.search(pattern, line)
                if match:
                    strings.append(match.group(1))
        
        print('所有频道：')     
        print(strings)      
        return strings
     
     
    #  根据频道名字和数据源数组，重写m3u文件
    def outputM3u(self,channelName,channelResourceList):
        #如果finalFile不存在，则创建
        if not os.path.exists(self.finalFile):
            with open(self.finalFile, 'w') as file:
                file.write('#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"\n')
       
        # 在基础文件中找channelName的那条数组
        with open(self.source_file, 'r') as file:
            for line in file:
                match = re.search(r'#EXTINF:-1.*?,\s*'+channelName, line)
                if match:
                    strings = match.group(0)
                    for channelResource in channelResourceList:
                        with open(self.finalFile, 'a') as file:
                            file.write(strings+'\n')
                            file.write(channelResource+'\n')
                    break
                    
            
     
    # 请求一个地址 计算网速  返回响应时间
    def getSpeed(self,url):
        print('发起测速请求')
        start = time.time()
        try:
            r = requests.get(url,timeout=4)
            resStatus = r.status_code
        except:
            print('请求超时或失败')
        end = time.time()
        print('用时')
        print(url)
        print(str(end-start))
        return end - start
    
    # 移除文件
    def removeFile(self):
        if os.path.exists(self.finalFile):
            os.remove(self.finalFile)
            print("文件已成功移除")
        else:
            print("文件不存在")
    
    # 比较网速排序 返回排序后的列表
    def compareSpeed(self,pageUrls):
        # response_times = []
        # for pageUrl in pageUrls:
        #     response_times.append(self.getSpeed(pageUrl))
        
        # sorted_urls = zip(pageUrls, response_times)
        # sorted_urls = sorted(sorted_urls, key=itemgetter(1))

        # pageUrls_new =[]
        # for url, _ in sorted_urls:
        #     pageUrls_new.append(url)
            
        # return pageUrls_new
        return pageUrls
        
    #调用浏览器以及相关操作
    def visitPage(self,channelNameList):
         # # 创建浏览器驱动实例
        global driver
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--remote-debugging-port=9222')
        driver = webdriver.Chrome(options=options)

        
        # # # 在当前窗口打开页面
        driver.get("https://www.foodieguide.com/iptvsearch/")

        # 移除文件
        self.removeFile()
            
        # 获取前三个数据源地址 
        for channelName in channelNameList:
            element=driver.find_element(By.ID, "search")
            element.clear()
            element.send_keys(channelName)
            driver.find_element(By.ID, "form1").find_element(By.NAME,"Submit").click()
            urls=[]
            allRangeElement=driver.find_elements(By.CLASS_NAME, "m3u8")
            if len(allRangeElement)<=0:
                continue
            for i in range(0,5):
                if allRangeElement[i]:
                    urls.append(allRangeElement[i].text)
            # 根据请求速度返回排好的地址
            urls=self.compareSpeed(urls)
            print('排好的地址：')
            print(urls)
            self.outputM3u(channelName,urls)
       
        
    def main(self):
        self.visitPage(self.getChannelNameList())
        # self.visitPage(['东方卫视'])
        # self.getChannelNameList()
        
        # self.removeFile()
        # self.outputM3u('东方卫视',['http://cfss.cc/api/ysp/dfws.m3u8','http://180.97.247.27/4403-tx.otvstream.otvcloud.com/otv/skcc/live/channel26/index.m3u8'])

TestKeyWords()

