import re
from hunter.dictionary import dictionaries
from hunter.distillery import Distillery
from hunter.search.search import Search
from hunter.treasure_concealer import tweets_path

__author__ = 'uriklarman'


def conceal_sentence(tweet_file, config):
    dicts = dictionaries.load_dictionaries(config)
    print 'keywords (x) = ', config.x
    print 'Essence len = ', config.essence_len
    distillery = Distillery(config.essence_len, dicts.keywords)
    search_engine = Search()
    raw_data_words = open(tweets_path + tweet_file).read().split()
    data_words = [keyword for word in raw_data_words for keyword in dicts.english["".join(c for c in word.lower() if c not in ('!', '.', ':', ',', '?', '"', '-'))]]
    sentence = 'guitar is hard'

    while data_words:
        conceal_step(data_words, sentence, keyword, search_engine, distillery, dicts)


def conceal_step(data_words, sentence, keyword, search_engine, distillery, dicts):
    links_list, next_url = search_engine.new_search([data_words[0], keyword, sentence], do_filter=False)
    while True:
        for link in links_list:
            link_is_candidate, s_i, k_i, next_sentence = lookup_sentence_and_keywords(link, keyword, sentence, distillery, config)
            if link_is_candidate:
                google_found_link, l_i = search_for_link_by_sentence(next_sentence, link, search_engine)
                if google_found_link:
                    next_keyword = compute_keyword(s_i, k_i, l_i, dicts)
                    data_words.pop(0)
                    return next_sentence, next_keyword

        links_list, next_url = search_engine.continuing_search(next_url)


def lookup_sentence_and_keywords(link, keyword, sentence, distillery, config):
    sentence_head = sentence.split()[0]
    essence, uncut_essence, essence_indexes, all_content = distillery.distill(link, True)
    uncut_len = len(uncut_essence)
    keyword_here = keyword in essence
    sentence_head_here = sentence_head in essence
    sentence_here = sentence in all_content
    if sentence_head_here and sentence_here:
        sentence_indexes = [m.start() for m in re.finditer(sentence, all_content)]
        s_head_i = essence_indexes[essence.index(sentence_head)]
        s_head_points_to_sentence = s_head_i in sentence_indexes
    else:
        s_head_points_to_sentence = False
    print '*'*10
    print 'uncut_len: ', uncut_len
    print 'keyword_here: ', keyword_here
    print 'sentence_head_here: ', sentence_head_here
    print 'sentence_here: ', sentence_here
    print 's_head_points_to_sentence: ', s_head_points_to_sentence
    if keyword_here and s_head_points_to_sentence:
        link_is_candidate = True
        s_i = essence.index(sentence[0])
        k_i = essence.index(keyword)
        k_index_in_all_content = all_content.index(keyword)
        next_sentence = all_content[k_index_in_all_content:k_index_in_all_content + config.essence_len]
        return link_is_candidate, s_i, k_i, next_sentence
    else:
        return False, -1, -1, ''


def search_for_link_by_sentence(sentence, link, search_engine, max_link_i):
    links_list, next_url = search_engine.new_search(sentence, do_filter=False)
    possible_links = links_list
    while len(possible_links) < max_link_i:
        links_list, next_url = search_engine.continuing_search(next_url)
        possible_links += links_list
        possible_links = possible_links[:max_link_i]

    if link in possible_links:
        return True, possible_links.index(link)
    else:
        return False, -1

def compute_keyword(s_i, k_i, l_i, dicts):
    key = s_i
    key *= 9
    key += k_i
    key *= 9
    key += l_i

    return dicts.keywords[key]

if __name__ == '__main__':
    tweet_file = 'tweet_CO_09.txt'
    config = dictionaries.Config(x=800, sentence_len=3, essence_len=33, link_len=8)
    dictionaries.create_and_save_dicts(config)
    conceal_sentence(tweet_file, config)
    print 'done'