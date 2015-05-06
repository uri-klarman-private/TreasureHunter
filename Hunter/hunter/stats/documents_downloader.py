from datetime import datetime
import random
import re
from time import sleep
import traceback
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from jumping_the_net.distillery import Distillery
from google_search import GoogleSearch

__author__ = 'uriklarman'

dest_path = '/Users/uriklarman/Development/PycharmProjects/keywords_learning/documents/'

def find_links(docs_num):
    english_words = read_all_english_words()
    # prev_search_time = datetime.now()
    links_set = set()
    search = GoogleSearch()

    while len(links_set) < docs_num:
        print 'len(links_set) is: ', len(links_set)
        num_of_words = random.randint(3,5)
        words = [english_words[random.randrange(10000)] for i in range(num_of_words)]
        # links_list, prev_search_time, next_url = search.new_search(words, prev_search_time)
        if not search.new_search(words):
            continue
        for i in range(10):
            link = search.next_link(avoid_more_searches=True)
            if not link:
                break
            if link not in links_set:
                with open('/Users/uriklarman/Development/PycharmProjects/keywords_learning/links.txt', 'a') as f:
                    f.write(link + '\n')
                links_set.add(link)
                if len(links_set) == docs_num:
                    break

        # print str(prev_search_time) + ', links_number = ', len(links_set)

def download_documents(links, start, stop, essence_len, exceptions_num, exceptions_period):
    english_words = set(read_all_english_words())
    browser = webdriver.Firefox()
    browser.set_script_timeout(3) # seconds
    browser.set_page_load_timeout(3)

    exceptions_times = []
    regex = re.compile('[^a-zA-Z\']')


    for i in range(start, stop, 1):
        link = links[i]
        print 'link[', i,'] = ', link
        try:
            browser.get(link)
            browser.find_elements_by_xpath('//*[@id]')
        except TimeoutException as to:
            print '*'*15, '\npage reached timeout: ', link, '\n', '*'*15
        except Exception as e:
            print '*'*30 + '\nbrowser threw Exception!!! leaving doc number: ', i
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            print ''.join('!! ' + line for line in lines)
            exceptions_times.append(datetime.now())
            if too_many_exceptions(exceptions_times, exceptions_num, exceptions_period):
                print('Too many Exceptions!!!')
                print exceptions_times
                break
            else:
                continue

        source = browser.page_source
        source = source
        raw_doc = regex.sub(' ', source).split()
        doc = [x for x in raw_doc if x in english_words]
        save_doc(doc[:essence_len], i)



def too_many_exceptions(exceptions_times, exceptions_num, exceptions_period):
    now = datetime.now()
    relevant_exceptions = [x for x in exceptions_times if (now - x).total_seconds() <= exceptions_period]
    return len(relevant_exceptions) >= exceptions_num

def save_doc(doc, i):
    with open('/Users/uriklarman/Development/PycharmProjects/keywords_learning/documents/doc_' + str(i), 'w') as f:
        f.write('\n'.join(doc))

def read_all_english_words():
    with open('/Users/uriklarman/Development/PycharmProjects/keywords_learning/english_full_list.txt') as f:
        english_words = f.read().splitlines()
    return english_words

def read_all_links():
    with open('/Users/uriklarman/Development/PycharmProjects/keywords_learning/links.txt') as f:
        links = f.read().splitlines()
    return links

if __name__ == '__main__':
    # docs_num=92500
    # find_links(docs_num)

    raw_links = read_all_links()
    unique_links = []
    for link in raw_links:
        if link not in unique_links:
            unique_links.append(link)
    start = 0
    stop = len(unique_links)
    essence_len=10000
    exceptions_num = 5
    exceptions_period = 5
    download_documents(unique_links, start, stop, essence_len, exceptions_num, exceptions_period)

    # t0 = datetime.now()
    # sleep(1)
    # t1 = datetime.now()
    # print too_many_exceptions([t0, t1], 1, 1)
