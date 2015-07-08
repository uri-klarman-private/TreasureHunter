from multiprocessing import Pool, Manager
import multiprocessing
import random

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
super_dict_path = path.dirname(__file__) + '/super_dict.pkl'

class GoogleSearch:

    def __init__(self):
        self.links = []
        self.next_link_index = 0
        self.totalResults = 0

        # self.public_url = 'https://cse.google.com:443/cse/publicurl?cx=007456907743860748191:oj1who__t-g'
        self.google_url = 'https://www.googleapis.com/customsearch/v1'

        self.params = {}
        self.params['alt'] = 'json'
        # self.params['key'] = 'AIzaSyDTZfn3N86ve0VivgQYT_2yVdiBW9HoeNU' #treasure hunter CSE
        self.params['key'] = 'AIzaSyDbdrd_CyQhtDS1Km_VdblVDqun6uyyFAI' #treasure hunter 2 CSE
        #
        # self.params['cx'] = '007456907743860748191:oj1who__t-g' #treasure hunter CSE
        self.params['cx'] = '004405701384112129294:onvr3tdk4-m' #treasure hunter 2 CSE
        # self.params['sort'] = 'date-sdate:a'




    def new_search(self, words):
        self.params['start'] = 1
        include = ' '.join(set(['"' + word + '"' for word in words])) + ' -"googlelist" -"pdf"'
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
    # links_set = set()
    # links_list = []
    # with open(links_text_path, 'r') as f:
    #     lines = f.read().splitlines()
    #     for line in lines:
    #         if line not in links_set:
    #             links_set.add(line)
    #             links_list.append(line)
    #
    # with open(links_text_path, 'w') as f:
    #     f.write('\n'.join(links_list))

    with open(links_text_path, 'r') as f:
        links = f.read().splitlines()
    links_set = set(links)

    keywords = [dicts.keywords[i] for i in range(len(dicts.keywords)/2)]
    with open(super_dict_path, 'rb') as myfile:
        super_dict = pickle.load(myfile)
    keywords_popularity = sorted([(x, len(super_dict[x])) for x in keywords],key=lambda x: x[1])
    generator = gen_subsets_special(keywords, config.essence_len-3)
    skew_generator = gen_subsets_special(keywords[:25], 3)

    google = GoogleSearch()

    for i in range(2500):
        searchwords = generator.next().union(skew_generator.next())
        google.new_search(searchwords)
        links = []
        for j in range(40):
            link = google.next_link(avoid_more_searches=False)
            if not link:
                break
            elif link in links_set:
                continue
            else:
                links_set.add(link)
                links.append(link)

        if len(google.links) == 0:
            stop = False
            if stop:
                break
        with open(links_text_path, 'a') as myfile:
            myfile.write('\n' + '\n'.join(links))

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
            stripped_link = str.strip(link)
            if not stripped_link:
                continue
            links_chunk.append(stripped_link)
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


def measure_covered_clues():
    config = dictionaries.Config(1, 2, 2, 89, 10, 200)
    dicts = dictionaries.load_dictionaries(config)
    keywords = sorted([dicts.keywords[i] for i in range(len(dicts.keywords)/2)])

    super_dict = create_super_dict(keywords)
    # with open(super_dict_path, 'rb') as myfile:
    #     super_dict = pickle.load(myfile)

    # keywords_popularity = sorted([(x, len(super_dict[x])) for x in keywords],key=lambda x: x[1])

    generator = gen_subsets_special(keywords, config.essence_len-1)
    success_count = 0
    tries = 10000
    for i in range(tries):
        clue = generator.next()
        setlist = []
        for keyword in clue:
            setlist.append(super_dict[keyword])
        links = set.intersection(*setlist)
        if len(links) > 0:
            success_count += 1
    print 'success rate is: ', success_count / float(tries)



def create_super_dict(keywords):
    super_dict = {}
    for keyword in keywords:
        super_dict[keyword] = set()

    with open(mapping_path, 'rb') as myfile:
        links_essences_1_to_1 = pickle.load(myfile)

    # links_essences_1_to_1 = dict(map(clear_str_only,x) for x in links_essences_1_to_1.items())
    # for key,val in links_essences_1_to_1.items():
    #     delete = False
    #     if type(key) is frozenset:
    #         if 'pump' in key or 'quotes' in key:
    #             delete = True
    #     else:
    #         if 'pump' in key or 'quotes' in val:
    #             delete = True
    #
    #     if delete:
    #         del(links_essences_1_to_1[key])
    #
    # with open(mapping_path, 'wb') as myfile:
    #     pickle.dump(links_essences_1_to_1, myfile)

    for i, key in enumerate(links_essences_1_to_1):
        if type(key) is str:
            continue
        link = links_essences_1_to_1[key]
        for keyword in key:
            super_dict[keyword].add(link)

    with open(super_dict_path, 'wb') as myfile:
        pickle.dump(super_dict, myfile)

    return super_dict

# def clear_str_only(x):
#     if type(x) is str:
#         return str.strip(x)
#     elif type(x) is frozenset:
#         return x
#     else:
#         print 'found ', x, ' which is a ', type(x)
#         return x


if __name__ == '__main__':
    config = dictionaries.Config(1, 2, 2, 89, 10, 200)
    dicts = dictionaries.load_dictionaries(config)
    get_links_from_google_API(config, dicts)
    #
    # parallel_create_links_essences_map(17000)
    #
    # measure_covered_clues()
    # links_list = []
    # links_set = set()
    # output = []
    # remove_lines = 400000
    # with open(links_text_path, 'r') as f:
    #     lines = f.read().splitlines()
    #     print 'len(lines) is: ', len(lines)
    #     for i, line in enumerate(lines):
    #         if i < remove_lines:
    #             continue
    #         if not line:
    #             continue
    #         if line in links_set:
    #             continue
    #         links_set.add(line)
    #         links_list.append(line)
    #
    # print 'len(links_list): ', len(links_list)
    # with open(links_text_path, 'w') as f:
    #     f.write('\n'.join(links_list))