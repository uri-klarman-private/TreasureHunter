import sys
import math

from search.search import Search
from hunter.dictionary.dictionaries import create_and_save_dicts, load_dictionaries

from stats.words_stats import WordsStats
from distillery import Distillery


__author__ = 'uriklarman'

def search_for_words(search_engine, distillery, keywords_dict, stats, collected_words, words, used_link, used_link_number):
    links_list, next_url = find_starting_links_list(search_engine, words, used_link, used_link_number)
    traceback_threshold = 20
    link_i = 0
    link_found = False
    while True:
        for link in links_list:
            if used_link == link:
                continue

            link_i += 1
            print '-' * 30
            print 'link: ', link
            print 'link_i: ', link_i
            print 'searching for words: ', words

            essence, uncut_essence = [],[]
            for i in range(3):
                try:
                    essence, uncut_essence = distillery.distill(link, keywords_dict)
                    break
                except:
                    print 'Distillery failed for the ', i, ' time. restarting browser...'
                    distillery.restart_browser()

            link_found = set(words).issubset(set(essence))
            words_in_uncut_essence = set(words).issubset(set(uncut_essence))
            found_words = []
            not_found_words = []
            for x in set(words):
                if x in essence:
                    found_words.append(x)
                else:
                    not_found_words.append(x)

            print 'link_found: ', link_found
            print 'words_in_uncut_essence: ', words_in_uncut_essence
            print 'essence len: ', len(essence)
            print 'essence: ', essence
            print 'uncut essence len: ', len(uncut_essence)
            print 'uncut essence: ', uncut_essence
            print 'found_words: ', found_words
            print 'not_found_words: ', not_found_words
            print '-' * 30

            stats.update(link_i, words, traceback_threshold, essence, uncut_essence, collected_words)

            if link_found or link_i >= traceback_threshold:
                break
        if link_found or link_i >= traceback_threshold:
            break

        do_backtrace = False
        if not next_url:
            do_backtrace = True
        else:
            try:
                links_list, next_url = search_engine.continuing_search(next_url)
            except Exception as inst:
                do_backtrace = True

        if do_backtrace:
            print '!'*30
            print "Could not continue search. given next_url: '%s'"%(next_url)
            print 'going to back trace!'
            print '!'*30
            link_found, link_i, link, essence = (False,0,'',[])
            break

    return link_found, link_i, link, essence

def find_starting_links_list(search_engine, words, used_link, used_link_number):
    # create first list of links.txt
    links_list, next_url = search_engine.new_search(words)

    # if no links.txt found
    if not links_list:
        return links_list, next_url

    # if this is a traceback move, pass over first used_link_number links.txt
    if used_link:
        used_links_list = links_list
        while (len(used_links_list) < used_link_number) and links_list:
            links_list, next_url = search_engine.continuing_search(next_url)
            used_links_list += links_list

        links_list = used_links_list[used_link_number+1:]

    return links_list, next_url

def encode(tweet_file, X, D, L, F, dict_first_word_i=0, endword_index=False):
    groups = []
    keywords_dict, english_dict, links_dict = load_dictionaries()

    keywords_len = len(keywords_dict) / 2
    essence_len = int(math.pow(keywords_len, float(F) / (D+L+F)))
    print 'keywords (X) = ', keywords_len
    print 'Essence len = ', essence_len
    distillery = Distillery(essence_len, keywords_dict)
    search_engine = Search()
    raw_data_words = open(tweet_file).read().split()
    data_words = []
    for word in raw_data_words:
        for keyword in english_dict[word.lower()]:
            data_words.append(keyword)
    end_word =keywords_dict[keywords_len - 1]
    if endword_index:
        end_word = keywords_dict[endword_index]
    words = [end_word] * (D+L+F)
    collected_words = [(words, '', 0)]
    stats = WordsStats(X, D, L, F, dict_first_word_i, tweet_file, collected_words,groups)

    try:
        while data_words:
            used_link = None
            used_link_number = -1
            while (True):
                link_found, link_i, link, essence = search_for_words(search_engine, distillery, keywords_dict, stats, collected_words, words, used_link, used_link_number)
                if link_found:
                    break
                else:
                    print '!'*30
                    print 'Backtracking steps!!!!!'
                    print 'Failed words: ', words
                    words, used_link, used_link_number = collected_words.pop()
                    words = collected_words[-1][0]
                    stats.update_collected_words(collected_words, groups)
                    print 'Stepping back to words: ', words
                    print '!'*30

            words_indexes = []
            for word in words:
                words_indexes.append(essence.index(word))

            words = [data_words.pop()]

            if link not in links_dict:
                links_dict = dicts.add_link_to_links_file(link, keywords_dict, X, L)
            link_words = links_dict[link][::-1]
            for i in range(L):
                words.append(link_words[i])
            if len(link_words) > L:
                groups.append(link_words[L:])

            function_words = dicts.translate_indexes_to_F_keywords(words_indexes, keywords_dict, essence_len, F)
            for function_word in function_words:
                words.append(function_word)

            collected_words.append((words, link, link_i))
            stats.update_collected_words(collected_words, groups)
            print ('collected_words len: ', len(collected_words))

    except Exception:
        t, v, tb = sys.exc_info()
        distillery.browser.close()
        raise t, v, tb

    print '*' * 30
    print 'final words are:'
    print words
    print 'collected words are:'
    print collected_words
    print 'groups are:'
    print groups
    print '*' * 30

    return collected_words, groups


# def decode(words, groups):
#     distillery = Distillery()
#     data = []
#     keywords_dict, general_dict, links_dict = dicts.load_dictionaries()
#     while True:
#         if words == [keywords_dict[-1]]*len(words):
#             break
#         data.append(words[0])
#         indexes = dicts.translate_5_keywords_to_indexes(words[1:6],len(words),keywords_dict,len(keywords_dict)/2,(len(keywords_dict)/2)**(5/len(words)))
#         indexes = dicts.translate_5_important_words_to_7_indexes(words[1:6])
#         link_words = words[6:0]
#         link = links_dict[link_words]
#         essence = distillery.distill(link,keywords_dict)
#         new_words = [0] * len(indexes)
#         for i in range(len(indexes)):
#             new_words[i] = essence[indexes[i]]
#         words = new_words
#
#     return data


if __name__ == '__main__':
    tweet_file = 'resources/tweet_1.txt'
    X,D,L,F = 100,1,3,3
    endword_index = 32
    # create_and_save_dicts(X,L)
    encode(tweet_file,X,D,L,F, endword_index=endword_index)