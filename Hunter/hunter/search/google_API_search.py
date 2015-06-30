from multiprocessing import Pool, Queue
import multiprocessing
from googleapiclient.sample_tools import init
import itertools
import requests
# from files_handler import save,read
from hunter.dictionary import dictionaries
from hunter.dictionary.combinations_provider import gen_subsets_special
from hunter.distillery import Distillery
import cPickle as pickle

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


def search_api(searchwords):
    links = ['http://www.o-cinema.org/event/dear-white-people/',
    'http://www.pbs.org/wgbh/americanexperience/features/primary-resources/jfk-diem/?flavour=mobile',
    'https://circ.ahajournals.org/site/misc/about.xhtml',
    'https://r-e-p-l-i-c-a.bandcamp.com/',
    'http://www.thecrimson.com/article/2015/3/26/around-town-iced-coffee/?page=2',
    'https://www.pinterest.com/y2kvictim/%E5%87%B6/',
    'http://www.beardstclair.com/blog-category/estate-planning.html',
    'http://intlschool.org/itk-pre-11-16-11/?currentPage=98',
    'http://www.hollywoodreporter.com/news/billboard-music-awards-2015-winners-795707',
    'http://blog.ocbeerblog.com/2014/07/25/forging-a-brewhouse-barley-forge-in-costa-mesa/',
    'http://www.firstchineseherbs.com/products-page/bulk-herbs-y/yellowdock-root/',
    'http://www.medialifemagazine.com:8080/news2002/may02/may27/4_thurs/news7thursday.html',
    'http://boutierwinery.com/aobhexpressi/lg-health-express-our-nurse-practitioners-will-se-matovina.html',
    'http://www.purpose.com/',
    'http://thejudyroom.com/ep/index.html',
    'http://wiki.apache.org/db-derby/ReplicationWriteup']
    return links

def create_links_dictionary_with_API():
    get_links_from_google_API()
    # process_links_to_essences(config, dicts)


def get_links_from_google_API(config, dicts):
    keywords = [dicts.keywords[i] for i in range(len(dicts.keywords)/2)]
    generator = gen_subsets_special(keywords, config.essence_len)

    google = GoogleSearch()

    for i in range(10000):
        searchwords = generator.next()
        google.new_search(searchwords)
        if len(google.links) == 0:
            searchwords = generator.next()
            google.new_search(searchwords)
            if len(google.links) == 0:
                break
        with open('/Users/uriklarman/GitHub/TreasureHunter/Hunter/hunter/search/links.txt', 'a') as myfile:
            myfile.write('\n' + '\n'.join(google.links))

        google.links = []

def process_links_to_essences(config, dicts):
    distillery = Distillery(config.essence_len, dicts.keywords)

    links_essences_1_to_1 = {}
    with open(...) as f:
        for line_i, link in enumerate(f):

            if link in links_essences_1_to_1:
                continue

            essence, uncut = distillery.distill(link, dicts.keywords)
            essence = frozenset(essence)

            if len(essence) < config.essence_len:
                continue

            if essence in links_essences_1_to_1:
                continue

            links_essences_1_to_1[link] = essence
            links_essences_1_to_1[essence] = link

            if line_i % 1000 == 0:
                print 'line_i: ', line_i
                with open('/Users/uriklarman/GitHub/TreasureHunter/Hunter/hunter/search/essences.pkl', 'a') as myfile:
                    pickle.dump(links_essences_1_to_1)


if __name__ == '__main__':
    config = dictionaries.Config(1, 2, 2, 89, 10, 200)
    dicts = dictionaries.load_dictionaries(config)

    # create_links_dictionary_with_API()
    process_links_to_essences()
