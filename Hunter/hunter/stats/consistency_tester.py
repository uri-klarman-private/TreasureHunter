import itertools
import random
from datetime import datetime

import marcel_search as search
from distillery import Distillery
from hunter.dictionary import dictionaries as dicts


__author__ = 'uriklarman'

search_keywords_file_name = '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/consistency_search_new/search_keywords'
links_to_sample_file_name = '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/consistency/links_to_sample'

# search_sample params:
num_keywords = 3
num_combinations = 300
num_links_per_combo = 10

num_links_in_sample = 350

X=100
D,L,F = 1,1,2
E=10

def write_str_list(file_name, str_list):
    with open(file_name, 'w') as f:
        for item in str_list[:-1]:
            f.write('%s\n' % item)
        f.write(str_list[-1])


def read_str_list(file_name):
    str_list = [line.strip() for line in open(file_name)]
    return str_list


def create_search_keywords():
    keywords_dict, english_dict, links_dict = dicts.load_dictionaries()
    keywords = [keywords_dict[i] for i in range(X)]
    keywords_combos = list(itertools.combinations(keywords,r=3))
    random.shuffle(keywords_combos)
    with open(search_keywords_file_name, 'w') as f:
        for i in range(num_combinations):
            f.write(' '.join(keywords_combos[i]))
            if i != num_combinations-1:
                f.write('\n')

def create_links_to_sample():
    keywords_dict, english_dict, links_dict = dicts.load_dictionaries()
    links = [x for x in links_dict.values() if isinstance(x, str)][:num_links_in_sample]
    write_str_list(links_to_sample_file_name, links)



def sample_search():
    time_stamp = str(datetime.now())
    sample_file_name = '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/consistency_search_new/sample_' + time_stamp

    keywords_combos_str = read_str_list(search_keywords_file_name)
    keywords_combos = [x.split() for x in keywords_combos_str]

    search_engine = search.MarcelSearch(page_load_timeout=10)
    for i,combo in enumerate(keywords_combos):
        print 'starting combo ', i, ' : ', combo
        current_search_links, next_url = search_engine.new_search(combo)
        if len(current_search_links) != 10:
            print 'links.txt are missing from page - will not sample'
        else :
            write_str_list(sample_file_name + '_chunk_' + str(i),current_search_links[:num_links_per_combo])

        # while len(current_search_links) < num_links_per_combo:
        #     links_list, next_url = search_engine.continuing_search(next_url)
        #     current_search_links += links_list
        #     if not links_list:
        #         break

def sample_links_essences():
    time_stamp = str(datetime.now())
    sample_file_name = '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/consistency/links_sample_' + time_stamp

    keywords_dict, english_dict, links_dict = dicts.load_dictionaries()
    distillery = Distillery(essence_len=E, keywords_dict=keywords_dict)

    all_links = read_str_list(links_to_sample_file_name)
    links = all_links[:num_links_in_sample]
    essences = []
    for i,link in enumerate(links):
        print ('starting link: %d , %s')%(i,link)
        for j in range(3):
            try:
                essence, uncut_essence = distillery.distill(link, keywords_dict)
                break
            except:
                print 'Distillery failed for the %s time. restarting browser...'% j
                distillery.restart_browser()
        essences.append(essence)

    with open(sample_file_name, 'w') as f:
        for essence in essences[:-1]:
            f.write('%s\n' % essence)
        f.write('%s' % essences[-1])

def split_old_files():
    old_file_names = ['search_sample_2015-01-15 19:17:26.864043',
                      'search_sample_2015-01-18 01:04:44.608701',
                      'search_sample_2015-01-19 01:32:35.639474',
                      ]
    path = '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/consistency/'
    for old_file in old_file_names:
        full_name = path + old_file
        search_results = read_str_list(full_name)
        for chunk_i in range(15):
            chunk = search_results[200*chunk_i:200*(chunk_i + 1)]
            write_str_list(full_name+'_chunk_'+str(chunk_i), chunk)

    print 'done'



if __name__ == '__main__':
    sample_search()
    # sample_links_essences()
    pass