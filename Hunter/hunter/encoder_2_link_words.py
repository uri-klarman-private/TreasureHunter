import itertools
import sys
from datetime import datetime
import math

from jumping_the_net.words_stats import WordsStats
import marcel_search as search
from distillery import Distillery
from hunter.dictionary import dictionaries as dicts


__author__ = 'uriklarman'

keywords_dict = {}
english_dict = {}
links_dict = {}
tries = 10

def encode(file_path, i, x):
    global keywords_dict, english_dict, links_dict
    keywords_dict, english_dict, links_dict = dicts.load_dictionaries()
    stats = WordsStats(file_path, i, x)
    # search = bing_search.BingSearch()
    keywords_len = len(keywords_dict)/2
    essence_len = int(math.pow(keywords_len, 5.0/8))
    print 'keywords (X) = ', keywords_len
    print 'Essence len = ', essence_len
    distillery = Distillery(essence_len, keywords_dict)
    reversed_data = turn_data_to_reversed_important_words(file_path, english_dict)
    reversed_data.insert(0, keywords_dict[keywords_len-1])

    # resources - index 0
    # function - index 1-5
    # link - index 6-7
    words = [keywords_dict[keywords_len-1]]*8
    eight_indexes = [0]*8

    prev_search_time = datetime.now()
    try:
        for word_index, data_word in enumerate(reversed_data):
            words[0] = data_word

            for search_i in range(tries):
                if search_i == 0:
                    links_list, prev_search_time, next_url = search.new_search(words, prev_search_time)
                else:
                    links_list, prev_search_time, next_url = search.continuing_search(next_url,prev_search_time)

                for link_index, link in enumerate(links_list):
                    print 'link: ', link
                    essence, unique_keywords = distillery.distill(link, keywords_dict)
                    stats.update_keywords_stats(essence,unique_keywords,words)
                    link_found = set(words).issubset(set(essence))
                    link_could_be_found = set(words).issubset(set(unique_keywords))
                    print('link_could_be_found: ', link_could_be_found)

                    found_words = []
                    not_found_words = []
                    for x in set(words):
                        if x in essence:
                            found_words.append(x)
                        else:
                            not_found_words.append(x)

                    print '-'*30
                    print 'word number: ', word_index
                    print 'search number: ', search_i
                    print 'link number: ', link_index
                    print 'link: ', link
                    print 'searching for words: ', words
                    print 'essence len: ', len(essence)
                    print 'essence: ', essence
                    print 'link_found: ', link_found
                    print 'found_words: ', found_words
                    print 'not_found_words: ', not_found_words
                    print '-'*30

                    if link_found:
                        break
                if link_found:
                    break

            # for search_i in range(tries):
            #     links_list = search.new_search(words)
            #     if not links_list:
            #         break
            #
            #     for link_index, link in enumerate(links_list):
            #         essence = distillery.distill(link, keywords_dict)
            #         update_word_count(word_count, essence)
            #         link_found = set(words).issubset(set(essence))
            #
            #         print '-'*30
            #         print 'word number: ', word_index
            #         print 'search number: ', search_i
            #         print 'link number: ', link_index
            #         print 'searching for words: ', words
            #         print 'essence len: ', len(essence)
            #         print 'essence: ', essence
            #         print 'link_found: ', link_found
            #         print '-'*30
            #
            #         if link_found:
            #             break
            #     if link_found:
            #         break

            if not link_found:
                raise 'Where is the reinforcement?! Abort! Abort!!'

            # find the 8 indexes of words in the page's essence, and translate them to 5 words
            for i, word in enumerate(words):
                eight_indexes[i] = essence.index(word)

            function_words = dicts.translate_8_indexes_to_5_keywords(eight_indexes,keywords_dict,keywords_len,essence_len)
            for index,function_word in enumerate(function_words):
                words[index+1] = function_word

            # translate the link into 2 words
            if link not in links_dict:
                links_dict = dicts.add_link_to_links_file(link,keywords_dict)
            words[6] = links_dict[link][0]
            words[7] = links_dict[link][1]
    except Exception:
        t, v, tb = sys.exc_info()
        distillery.browser.close()
        raise t, v, tb

    print '*'*30
    print 'final words are:'
    print words
    print '*'*30
    return words

def decode(words):
    distillery = Distillery()
    data = []
    important_words_dict, general_dict, links_dict = dicts.load_dictionaries()
    while True:
        data.append(words[0])
        if set(words[1:]).issubset(set([dicts.end_chain_word])):
            return data
        indexes = dicts.translate_5_important_words_to_8_indexes(words[1:6])
        link = links_dict[(words[6], words[7])]
        essence = distillery.distill(link,important_words_dict)
        new_words=[0]*len(indexes)
        for i in range(len(indexes)):
            new_words[i] = essence[indexes[i]]

        words = new_words

    return data

def turn_data_to_reversed_important_words(file_path, english_dict):
    data_words = open(file_path).read().split()
    important_words = [english_dict[word.lower()] for word in data_words]
    return list(itertools.chain.from_iterable(important_words))[::-1]


if __name__ == '__main__':
    # dicts.main(1500, 256)
    # encode('resources/data.txt', 1500, 256)
    dicts.create_and_save_dicts(300, 100)
    encode('resources/data.txt', 300, 100)