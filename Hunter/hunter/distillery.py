from datetime import datetime
from random import Random

from selenium.common.exceptions import TimeoutException
from hunter.dictionary.combinations_provider import SEED


__author__ = 'uriklarman'

from selenium import webdriver
import re
import time

class Distillery:

    def __init__(self, essence_len, keywords_dict, page_load_timeout=10):
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
        self.browser = webdriver.Firefox()
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

        # # sorting and then shuffling, in order to keep consistency
        # uncut_essence.sort()
        # rand = Random(SEED)
        # rand.shuffle(uncut_essence)

        return uncut_essence[:self.essence_len], uncut_essence
