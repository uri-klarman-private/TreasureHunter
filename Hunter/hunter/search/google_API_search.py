from multiprocessing import Pool, Queue
import multiprocessing
from googleapiclient.sample_tools import init
import itertools
import requests
from files_handler import save,read

__author__ = 'uriklarman'
import json
import urllib

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


    def next_link(self, avoid_more_searches=False):
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
        print '*'*30
        print '*'*30
        print 'search: ', self.params['q']
        print 'Total search results are: ', self.totalResults
        print '*'*30
        print '*'*30
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

def search_combinations(seed_words, total_links_wanted, search_parallel_factor, combin_factor=2, first_chunk=0):
    combinations = list(itertools.combinations(seed_words,r=combin_factor))
    links_per_combination = total_links_wanted / len(combinations) + 1

    # use 20 chunks of 5%, but at least 50 combinations per chunk
    chunk_size = max(len(combinations) / 20, 30)
    combinations_chunks = list(chunks(combinations,chunk_size))

    print 'About to start searches'
    print '-'*25
    print 'Number of searches required: ', len(combinations)
    print 'Number of searches chunks: ', len(combinations_chunks)
    print 'First chunk to be searched: ', first_chunk
    print '-'*25

    __search_combinations_chunks(links_per_combination, combinations_chunks, first_chunk, search_parallel_factor)
    chunks_list = read_links_from_disk(len(combinations_chunks))

    # Notice that this is a list of chunks. each chunk is a list of results. each result is a list of links received
    # from a specific combination.
    return chunks_list

def __search_combinations_chunks(links_per_combination, combinations_chunks, first_chunk, search_parallel_factor):
    manager = multiprocessing.Manager()
    search_engines = manager.Queue(search_parallel_factor)
    # search_engines = Queue(search_parallel_factor)
    for i in range(search_parallel_factor):
        search_engines.put(GoogleSearch())

    pool = Pool(search_parallel_factor)
    links = []
    for i,chunk in enumerate(combinations_chunks):
        if i < first_chunk:
            print 'Google search passing chunk: ', i
        else:
            print 'Google search starting chunk: ', i
            process_params = [(combination, links_per_combination, search_engines) for combination in chunk]
            links = pool.map(search_single_combination, process_params)
            print 'Google search finished chunk: ', i
            save(links,'links_chunk_'+str(i))

    pool.close()

    return links

def search_single_combination((combination, links_per_combination, search_engines)):
    engine = None
    try:
        links = []
        engine = search_engines.get()
        engine.new_search(combination)
        for i in range(links_per_combination):
            link = engine.next_link()
            if link == None:
                break
            else:
                links.append(link)

        return links
    finally:
        if engine != None:
            search_engines.put(engine)


def read_links_from_disk(num_of_chunks):
    chunks_list = []
    for i in range(num_of_chunks):
        chunks_list.append(read('links_chunk_'+str(i)))
    return chunks_list

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]



def test_basic_search_functionality():
    google = GoogleSearch()
    word_sets = [['done', 'store'], ['paper', 'blue', 'can', 'happy']]

    for set in word_sets:
        google.new_search(set)
        for i in range(20):
            link = google.next_link()
            print link

    print 'All done!'

def test_parallel_search():
    seed_words = ['average', 'build', 'crack', 'drone', 'elephant', 'fresh', 'groom']
    total_links_wanted = 1000
    search_parallel_factor = 10
    combin_factor=3
    first_chunk=2
    chunks_list = search_combinations(seed_words, total_links_wanted, search_parallel_factor, combin_factor, first_chunk)
    links_list = [link for chunk in chunks_list for combination in chunk for link in combination]
    print len(links_list)
    print len(set(links_list))
    print 'Done'
if __name__ == '__main__':
    test_parallel_search()