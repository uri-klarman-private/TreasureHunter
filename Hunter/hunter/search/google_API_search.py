from multiprocessing import Pool, Manager
import multiprocessing

import requests

from hunter.dictionary import dictionaries
from hunter.dictionary.combinations_provider import gen_subsets_special
from hunter.distillery import Distillery
import cPickle as pickle
from os import path

import json


__author__ = 'uriklarman'

links_text_path = path.dirname(__file__) + '/links.txt'
mapping_path = path.dirname(__file__) + '/essences.pickel'

class GoogleSearch:

    def __init__(self):
        self.links = []
        self.next_link_index = 0
        self.totalResults = 0

        # self.public_url = 'https://cse.google.com:443/cse/publicurl?cx=007456907743860748191:oj1who__t-g'
        self.google_url = 'https://www.googleapis.com/customsearch/v1'

        self.params = {}
        self.params['alt'] = 'json'
        self.params['key'] = 'AIzaSyDTZfn3N86ve0VivgQYT_2yVdiBW9HoeNU'
        self.params['cx'] = '007456907743860748191:oj1who__t-g'
        # self.params['sort'] = 'date-sdate:a'


    def new_search(self, words):
        self.params['start'] = 1
        include = ' '.join(set(['"' + word + '"' for word in words]))
        self.params['q'] = include
        res = self.execute_search()
        return res


    def next_link(self, avoid_more_searches=True):
        if self.next_link_index >= len(self.links):
            if avoid_more_searches:
                return False
            any_links_found = self.execute_search()
            if not any_links_found:
                return False

        link = self.links[self.next_link_index]
        self.next_link_index += 1
        return link

    def execute_search(self):
        if self.params['start'] == 0:
            return False

        resp = requests.get(url=self.google_url, params=self.params)
        data = json.loads(resp.text)

        if 'searchInformation' not in data:
            print 'No results'
            return False
        self.totalResults = int(data['searchInformation']['totalResults'])
        print 'search: ', self.params['q'], ' Total search results are: ', self.totalResults
        if self.totalResults == 0:
            return False

        self.links = [item['link'] for item in data['items']]

        if len(self.links) == 0:
            return False

        if 'nextPage' in data['queries']:
            self.params['start'] = data['queries']['nextPage'][0]['startIndex']
        else:
            self.params['start'] = 0
        self.next_link_index = 0

        return True


def get_links_from_google_API(config, dicts):
    links_set = set()
    # links_list = []
    with open(links_text_path, 'r') as f:
        for line_i, link in enumerate(f):
            if link not in links_set:
                links_set.add(link)
    #             links_list.append(link)
    # with open(links_text_path, 'w') as f:
    #     for link in links_list:
    #         f.write(link)

    keywords = [dicts.keywords[i] for i in range(len(dicts.keywords)/2)]
    generator = gen_subsets_special(keywords, config.essence_len)

    google = GoogleSearch()

    for i in range(10000):
        searchwords = generator.next()
        google.new_search(searchwords)
        links = []
        for i in range(20):
            link = google.next_link(avoid_more_searches=False)
            if not link:
                break
            elif link in links_set:
                continue
            else:
                links_set.add(link)
                links.append(link)

        if len(links) == 0:
            break
        with open(links_text_path, 'a') as myfile:
            myfile.write('\n' + '\n'.join(google.links))

threads = 10
def parallel_create_links_essences_map(first_line):
    in_queue = multiprocessing.Queue(threads)
    out_queue = multiprocessing.Queue(threads)

    out_queue_to_dict_job = multiprocessing.Process(target=out_queue_to_dict, args=(out_queue,))
    out_queue_to_dict_job.start()

    jobs = []
    for i in range(threads):
        p = multiprocessing.Process(target=in_queue_to_out_queu, args=(in_queue, out_queue))
        jobs.append(p)
        p.start()

    links_to_in_queue(in_queue, first_line, threads)


def links_to_in_queue(in_queue, first_line, threads):
    with open(links_text_path, 'r') as f:
        links_chunk = []
        for line_i, link in enumerate(f):
            if line_i < first_line:
                continue
            links_chunk.append(link)
            if line_i % 100 == 0:
                in_queue.put(links_chunk)
                links_chunk = []
                print 'line_i: ', line_i

    print 'finished all ', line_i, 'lines in links.txt'
    for i in range(threads):
        in_queue.put(None)



def in_queue_to_out_queu(in_queue, out_queue):
    config = dictionaries.Config(1, 2, 2, 89, 10, 200)
    dicts = dictionaries.load_dictionaries(config)
    distillery = Distillery(config.essence_len, dicts.keywords)

    while True:
        links = in_queue.get()
        if links is None:
            out_queue.put((None, None))
            break
        for link in links:
            try:
                essence, uncut = distillery.distill(link)
                essence = frozenset(essence)
                out_queue.put((link, essence))
            except:
                print 'distillery failed! Skipping link: ', link
                distillery.restart_browser()
                continue


def out_queue_to_dict(out_queue):
    config = dictionaries.Config(1, 2, 2, 89, 10, 200)
    with open(mapping_path, 'rb') as myfile:
        links_essences_1_to_1 = pickle.load(myfile)
    nones_found = 0
    while nones_found < threads:
        link, essence = out_queue.get()

        if link is None:
            nones_found += 1
        else:
            if len(essence) < config.essence_len:
                continue
            if link in links_essences_1_to_1:
                continue
            if essence in links_essences_1_to_1:
                continue
            else:
                links_essences_1_to_1[link] = essence
                links_essences_1_to_1[essence] = link
                if len(links_essences_1_to_1) % 100 == 0:
                    with open(mapping_path, 'wb') as myfile:
                        pickle.dump(links_essences_1_to_1, myfile)

    with open(mapping_path, 'wb') as myfile:
        pickle.dump(links_essences_1_to_1, myfile)

if __name__ == '__main__':
    config = dictionaries.Config(1, 2, 2, 89, 10, 200)
    dicts = dictionaries.load_dictionaries(config)
    get_links_from_google_API(config, dicts)

    # parallel_create_links_essences_map(3839)
