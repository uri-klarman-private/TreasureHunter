import time
import traceback
from bs4 import BeautifulSoup
import gzip
import re
import StringIO
import sys
import urllib2
import urllib
import urlparse
from datetime import datetime,timedelta
import requests
from selenium import webdriver
from hunter.dictionary.dictionaries import resources_path


time_between_searches = 20

# Url to use for searches
# Q_URL = "http://www.google.com/search?hl=en&lr=lang_en&q=%s&btnG=Google+Search"
CONTINUED_SEARCH_URL = "https://www.google.com"
QUERY_URL_PART_1 = 'https://www.google.com/search?q='
# QUERY_URL_PART_2 = '&lr=lang_en&cr=countryUS&hl=en&source=lnt&tbs=cdr:1,cd_max:1/1/2010,lr:lang_1en,sbd:1&filter=0' # sort by date
QUERY_URL_PART_2 = '&lr=lang_en&cr=countryUS&hl=en&source=lnt&uule=w+CAIQICIeQ2hpY2FnbyxJbGxpbm9pcyxVbml0ZWQgU3RhdGVz&gl=US&filter=0' # sort by date with uule
QUERY_URL_PART_2_NO_FILTER = '&lr=lang_en&cr=countryUS&hl=en&source=lnt&uule=w+CAIQICIeQ2hpY2FnbyxJbGxpbm9pcyxVbml0ZWQgU3RhdGVz&gl=US' # sort by date with uule

# uule example
# QUERY_URL_PART_1 = 'https://www.google.com/search?hl=en&gl=us&q='
# QUERY_URL_PART_2 = '&tbs=cdr:1,cd_max:1/1/2010,lr:lang_1en,sbd:1&filter=0&uule=w+CAIQICINVW5pdGVkIFN0YXRlcw'


# a = 'https://www.google.com/search?hl=en&lr=lang_en&cr=countryUS&q=%22bugs%22&btnG=Google+Search&gws_rd=ssl'
# a = 'https://www.google.com/search?hl=en&lr=lang_en&cr=countryUS&q="bugs"&btnG=Google+Search&gws_rd=ssl'
#
# a = 'https://www.google.com/search?q=%22bugs%22&lr=lang_en&cr=countryUS&hl=en&source=lnt&tbs=lr%3Alang_1en%2Cctr%3AcountryUS%2Ccdr%3A1%2Ccd_min%3A%2Ccd_max%3A1%2F1%2F2010&tbm='
# a = 'https://www.google.com/search?q=%s&lr=lang_en&cr=countryUS&hl=en&source=lnt&tbs=lr%3Alang_1en%2Cctr%3AcountryUS%2Ccdr%3A1%2Ccd_min%3A%2Ccd_max%3A1%2F1%2F2010&tbm='
#
# a = 'https://www.google.com/search?q=%22bugs%22&lr=lang_en&cr=countryUS&hl=en&source=lnt&tbs=lr%3Alang_1en%2Cctr%3AcountryUS%2Ccdr%3A1%2Ccd_min%3A%2Ccd_max%3A1%2F1%2F2010&tbm='
# a = 'https://www.google.com/search?q=%22bla%22+%22bli%22&hl=en&biw=1440&bih=753&source=lnt&tbs=cdr%3A1%2Ccd_min%3A%2Ccd_max%3A7%2F27%2F2010&tbm='
#
# a = 'https://www.google.com/search?q=%22bla%22+%22bli%22&hl=en&biw=1440&bih=753&source=lnt&tbs=cdr%3A1%2Ccd_min%3A%2Ccd_max%3A1%2F1%2F2010&tbm='

# https://www.google.com/search?q=%22blu%22+%22bli%22+%22bla%22+-%22corpus%22+-%22dictionary%22+-%22glossary%22+-%22lexicon%22+-%22ISSUU%22+-%22pdf%22+-%22archive%22&lr=lang_en&hl=en&tbs=cdr:1,cd_max:1/1/2010,lr:lang_1en,sbd:1&filter=0&biw=1050&bih=709
# https://www.google.com/search?q=%22blu%22+%22bli%22+%22bla%22+-%22corpus%22+-%22dictionary%22+-%22glossary%22+-%22lexicon%22+-%22ISSUU%22+-%22pdf%22+-%22archive%22&lr=lang_en&hl=en&tbs=cdr:1,cd_max:1/1/2010,lr:lang_1en,sbd:1

parameters = {'lr=':'lang_en', # restricts results to documents in a specific language
              'hl=':'lang_en', # interface language. used just in case, suggested even if using 'lr'
              'source=':'web', # web,hp (homepage) and lnt . not sure of their effect
              'tbs=': 'cdr%3A1%2Ccd_min%3A%2Ccd_max%3A1%2F1%2F2010', # dates see below examples
              'tbm=': '', # to search for apps/books/Images/recepies/etc... explanation here: https://stenevang.wordpress.com/2013/02/22/google-search-url-request-parameters/
              'biw=': '1440', #optimizing to screen size (width)
              'bih=' : '800', #optimizing to screen size (height)
              'filter=' : 0, # turns off automatic filtering. the same effect as reaching the last page and clicking on "repeat the search with the omitted results included"
              'tbas=' : 0, #sort by relevancy
              }
# &tbs=cdr%3A1%2Ccd_min%3A%2Ccd_max%3A7%2F27%2F2010&tbm=   27 7 2010
# &tbs=cdr%3A1%2Ccd_min%3A%2Ccd_max%3A1%2F1%2F2010&tbm=    1  1 2010
# &tbs=cdr%3A1%2Ccd_min%3A9%2F9%2F1999%2Ccd_max%3A7%2F27%2F2010&tbm= 9.9.1999-2.27.2010


class Search:

    def __init__(self, page_load_timeout=7):
        self.page_load_timeout = page_load_timeout
        self.prev_search_time = datetime.now()
        self.last_browser_restart_time = datetime.now()
        self.restart_browser()

    def restart_browser(self):
        while True:
            try:
                self.browser.quit()
            except:
                print 'failed to quit browser'
            time.sleep(1)
            try:
                self.start_browser()
            except:
                print 'failed to start browser'
                continue
            break

    def start_browser(self):
        self.last_browser_restart_time = datetime.now()
        self.browser = webdriver.Chrome()
        # self.browser.implicitly_wait(page_load_timeout/2)
        self.browser.set_script_timeout(self.page_load_timeout) # seconds
        self.browser.set_page_load_timeout(self.page_load_timeout+1)

    def wait_till_safe(self):
        now = datetime.now()
        delta = now - self.prev_search_time
        time_to_sleep = time_between_searches - delta.total_seconds()
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
        self.prev_search_time = now

    def continuing_search(self, url):
        print 'continuing_search() given url: ', url
        self.wait_till_safe()
        return self.__search_by_url(url)


    def new_search(self, words_list, do_filter):
        search_phrase = ' '.join(set(['"' + word + '"' for word in words_list]))
        search_phrase += ' -"corpus" -"dictionary" -"glossary" -"lexicon" -"ISSUU" -"archive" -"pdf"'
        # Build the request URL
        query_words_str = urllib.quote_plus(search_phrase)
        self.wait_till_safe()
        if do_filter:
            search_url = QUERY_URL_PART_1 + query_words_str + QUERY_URL_PART_2_NO_FILTER
        else:
            search_url = QUERY_URL_PART_1 + query_words_str + QUERY_URL_PART_2

        return self.__search_by_url(search_url)

    def __search_by_url(self, search_url):
        links_list, next_url = ([], '')
        for i in range(5):
            try:
                # if (datetime.now() - self.last_browser_restart_time).total_seconds() > 3600:
                #     self.restart_browser()
                links_list, next_url = self.__do_search_by_url(search_url)
                if links_list:
                    break
                else:
                    print 'No links were found in this try. going to retry...'
            except Exception as inst:
                print traceback.format_exc()
                print 'Search failed... going to retry...'

        return links_list, next_url

    def __do_search_by_url(self, search_url):
        """ Return a list of the first 10 URLs returned by a google search for
        'string'
        """

        print 'Received the following url: ', search_url

        links_list = []

        self.browser.get(search_url)
        do_get_again = False

        if do_get_again:
            self.browser.get(search_url)

        self.browser.find_elements_by_xpath('//*[@id]')
        source = self.browser.page_source
        soup = BeautifulSoup(source)

        next_url = ''
        if soup.find(id='pnnext', href=True) is not None:
            next_url = CONTINUED_SEARCH_URL + soup.find(id='pnnext')['href']
        anchors = soup.findAll('a', href=True)


        for a in anchors:
            try:
                link = a['href']
            except KeyError:
                # Not a link
                continue

            # Get rid of all the local google crap
            if re.search("google", link, re.IGNORECASE):
                #had google in it, skip it
                continue

            # Links seem to have some junk on them, remove for urlparse sake
            if link.startswith('/url?q='):
                link = ''.join(link.split('/url?q=', 1))

            # Now try URL parse
            pieces = urlparse.urlparse(link, 'http')

            # Clean off whatever that other google crap is
            link = link.split('&sa=', 1)[0]

            if ('google' in pieces.netloc) or (not pieces.netloc):
                continue

            # Add it to our output list
            links_list.append(link)

        # ues id  = "pnnext" and get href to next one
        bad_links = ['https://www.youtube.com/', 'https://www.blogger.com/?tab=wj']
        links_list = [x for x in links_list if x not in bad_links]
        return links_list, next_url

if __name__ == '__main__':
    engine = Search()
    links_list, next_url = engine.new_search(['bla', 'bli', 'blu'], False)
    print links_list
    for i in range(100):
        links_list, next_url = engine.continuing_search(next_url)
        print links_list

    print 'done'