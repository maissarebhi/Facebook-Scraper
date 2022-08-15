#!/usr/bin/env python
# coding: utf-8

import sys
import warnings
import re
import urllib.request
from urllib.error import HTTPError
#error.HTTPError
import bs4 as bs


import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from re import S
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import warnings
import time
import pandas as pd
from time import sleep
from sqlalchemy import create_engine
import re
def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))


import os



class facebookScraper:
    url_search = None
    url_selenium = None
    #chrome browser
    browser = None
    base_url = 'https://www.facebook.com/'
    
    #path to chrome driver
    
    def __init__(self,user=None,pwd=None,delay=15,path_to_chrome='path to chrome driver \\chromedriver.exe'):
        self.path_to_chrome=path_to_chrome
        self.get_browser()
        self.user=user
        self.pwd=pwd
        self.delay=delay
        if self.user!=None and self.pwd!=None:
            self.login(self.user,self.pwd)
            time.sleep(30)
        pass
    def __exit__(self):
        try:
            self.browser.close()
        except Exception as e:
            pass
    def login(self,usr,pwd):
        self.browser.get('https://www.facebook.com/')
        sleep(1)
        username_box = self.browser.find_element(By.ID,'email')
        username_box.send_keys(usr)
        sleep(1)
  
        password_box = self.browser.find_element(By.ID,'pass')
        password_box.send_keys(pwd)
  
        boxs = self.browser.find_elements(By.TAG_NAME,'button')
        for i in boxs:
            if i.text.find('Log')!=-1:
                login_box=i
        login_box.click()
    def get_browser(self):
        try:
            warnings.filterwarnings("ignore")
            options = Options()
            options.add_argument("start-maximized")
            options.add_argument("disable-infobars")
            options.add_argument("--disable-extensions")
            options.add_argument('--disable-notifications')
            options.add_argument("start-maximized")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            prefs = {"profile.default_content_setting_values.notifications" : 2}
            options.add_experimental_option("prefs",prefs)
            self.browser = webdriver.Chrome(chrome_options=options, executable_path=self.path_to_chrome)
        except Exception as e:
            print('get_browser Error: ',e)

    def get_fb_info(self,pagename):
        res = {}
        res['fb_followers'] = 0
        res['fb_likers'] = 0
        res['Activity']=None
        res['people checked']=0
        LLL=list()
        if fb_url is not None:
            fb_url='https://www.facebook.com/'+pagename
            self.browser.get(fb_url+'/about')
            time.sleep(self.delay)
            TT=self.browser.find_elements(By.TAG_NAME,"div")
            print(len(TT))
            for i in TT:
                if i.text.find("like")>-1:
                    res['fb_likers']= i.text.split()[0]
                if i.text.find("follow")>-1:
                    res['fb_followers']= i.text.split()[0]
                    act=TT[TT.index(i)+1].text
                    if act.find('checked')>-1:
                        res['people checked']=act.split()[0]
                        res['Activity']=TT[TT.index(i)+6].text
        return res
    def get_info_from_list(self,list_of_urls):
        result=[]
        for i in list_of_urls:
            result.append(self.get_fb_info(i))
        return pd.DataFrame(result)
    def collect_page(self, pagename,depth=2):
        # navigate to page
        fb_url='https://www.facebook.com/'+pagename
        fb_url=fb_url.replace('www',"m")
        self.browser.get(fb_url)

        # Scroll down depth-times and wait delay seconds to load
        # between scrolls
        for scroll in range(depth):
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(self.delay)

        # Once the full page is loaded, we can start scraping
        links = self.browser.find_elements(By.LINK_TEXT,"See more")
        for link in links:
            link.click()
            
        posts = self.browser.find_elements(By.CLASS_NAME,"_3drp")
        print(len(posts))
        result=[]
        for i in posts:
            temp={}
            header=i.find_element(By.TAG_NAME,'header').text
            l=header.split()
            l.pop(0)
            l.pop(-1)
            temp['Page name']=pagename
            temp['Time']=' '.join(l)
            try:
                temp['Post']=i.find_element(By.TAG_NAME,"p").text.strip()
            except:
                temp['Post']=i.find_element(By.TAG_NAME,"div").text.strip()
            footer=i.find_element(By.TAG_NAME,'footer').text
            L=footer.split()
            L=[i for i in L if has_numbers(i)]
            temp['reacts']=L[0]
            temp['comments']=L[1]
            temp['shares']=L[2].replace('Comments','')
            result.append(temp)
        self.browser.close()
        self.posts=result
        return result
    def save_data_to_database(self):
        engine = create_engine('Database', echo=False)  
        pd.DataFrame(self.posts).to_sql('Posts',con=engine, if_exists='append')
        
    
