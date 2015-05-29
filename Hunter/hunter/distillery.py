from datetime import datetime
from random import Random
import os

from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import re
import time

__author__ = 'uriklarman'



class Distillery:

    def __init__(self, essence_len, keywords_dict, page_load_timeout=6):
        self.essence_len = essence_len
        self.regex = re.compile('[^a-zA-Z]')
        self.keywords_dict = keywords_dict
        self.page_load_timeout = page_load_timeout
        self.start_browser()

    def restart_browser(self):
        try:
            self.browser.quit()
        except:
            print 'failed to quit browser'
        time.sleep(1)
        self.start_browser()

    def start_browser(self):
        self.last_browser_restart_time = datetime.now()

        prefs = {}
        prefs['download.default_directory'] = os.devnull
        prefs['profile.default_content_settings.images'] = 2
        prefs['download.prompt_for_download'] = False
        chrome_options = Options()
        chrome_options.add_experimental_option( "prefs", prefs)
        self.browser = webdriver.Chrome(chrome_options=chrome_options)

        # chrome_profile = webdriver.ChromeOptions()
        # profile = {"download.default_directory": "NUL", "download.prompt_for_download": False, }
        # chrome_profile.add_experimental_option()
        # chrome_profile.add_experimental_option("prefs", profile)
        # self.driver = webdriver.Chrome(chrome_options=chrome_profile)
        # self.browser = webdriver.Chrome()
        # self.browser.implicitly_wait(page_load_timeout/2)
        self.browser.set_script_timeout(self.page_load_timeout) # seconds
        self.browser.set_page_load_timeout(self.page_load_timeout+1)

    def distill(self, link, keywords_dict):
        open_browser_duration = datetime.now() - self.last_browser_restart_time
        if open_browser_duration.total_seconds() > 120:
            self.restart_browser()
        try:
            self.browser.get(link)
            self.browser.find_elements_by_xpath('//*[@id]')
        except TimeoutException as to:
            print '*'*15
            print 'page reached timeout: ', link
            print '*'*15
        except Exception as e:
            print 'browser Failed...'

        source = self.browser.page_source.lower()[:1000000]
        visible_words = re.sub(r'\W+', ' ', source).split()

        keywords = [word for word in visible_words if word in self.keywords_dict]
        keywords_set = set()
        uncut_essence = []
        for word in keywords:
            if word not in keywords_set:
                uncut_essence.append(word)
                keywords_set.add(word)

        # shuffling according to link
        rand = Random(link)
        rand.shuffle(uncut_essence)

        return uncut_essence[:self.essence_len], uncut_essence
