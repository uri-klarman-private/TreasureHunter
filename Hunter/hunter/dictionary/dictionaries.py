from itertools import combinations
import re
import cPickle as pickle
import itertools
import traceback
from os import path
import math
from random import shuffle, Random

from hunter.dictionary.combinations_provider import create_ordered_product, create_ordered_combinations


__author__ = 'uriklarman'
keywords_learner_resources_path = path.dirname(__file__) + '/../../../KeywordsLearner/keywordslearner/resources/'
keywords_path = keywords_learner_resources_path + 'LDA_result/topic_words'
english_words_path = keywords_learner_resources_path + 'LDA_input/written.num'

resources_path = path.dirname(__file__) + '/../resources/'
test_case_path = resources_path + '%s_%s_%s_%s/'
links_path = test_case_path + 'links.txt'
keywords_dict_path = test_case_path + 'keywords_dict.pkl'
english_dict_path = test_case_path + 'english_dict.pkl'
links_dict_path = test_case_path + 'links_dict.pkl'

last_english_line = 844587


class Dicts:
    def __init__(self, keywords_dict, english_dict, links_dict):
        self.keywords = keywords_dict
        self.english = english_dict
        self.links = links_dict


class LinksDict:
    def __init__(self, links_to_essences, combos_to_links):
        self.links_to_essences = links_to_essences
        self.combos_to_links = combos_to_links


class Config:
    def __init__(self, d, l, f, x, shuffle_keywords_seed=False, shuffle_stop=0):
        self.d = d
        self.l = l
        self.f = f
        self.x = x
        self.shuffle_keywords_seed = shuffle_keywords_seed
        if shuffle_stop < x:
            self.shuffle_stop = x
        else:
            self.shuffle_stop = shuffle_stop

        self.w = d + l + f
        self.essence_len = int(math.pow(x, float(f) / self.w))

    def params_tuple(self):
        return self.d, self.l, self.f, self.x


def create_dictionaries(config):
    keywords_dict = create_keywords_dict(config)
    if config.x > 83:
        english_dict = create_english_dict(config, keywords_dict)
    else:
        english_dict = create_english_dict(config, keywords_dict, keywords_per_word=4)

    links_dict = create_predefined_links_dictionary(config, keywords_dict)

    dicts = Dicts(keywords_dict, english_dict, links_dict)
    return dicts


def create_keywords_dict(config):
    keywords = []
    with open(keywords_path) as file:
        regex = re.compile('[^a-zA-Z]')
        for index, line in enumerate(file):
            if '#' in line:
                continue
            word = regex.sub('', line)
            if word in keywords:
                print 'word found in dict! ', word
                continue
            if len(word) <= 2:
                continue
            keywords.append(word)
    if config.shuffle_keywords_seed:
        print keywords
        keywords = keywords[:config.shuffle_stop]
        rand = Random(config.shuffle_keywords_seed)
        rand.shuffle(keywords)
        print keywords
    keywords_dict = {}
    for i in range(config.x):
        keywords_dict[i] = keywords[i]
        keywords_dict[keywords[i]] = i

    print 'keywords_dict size is: ', len(keywords_dict)
    return keywords_dict


def create_english_dict(config, keywords_dict, keywords_per_word=3):
    combinations = create_ordered_product(range(config.x), keywords_per_word)

    english_dict = {}
    with open(english_words_path) as f:
        different_words_index = 0
        for (line_number, line), combination in itertools.izip(enumerate(f), combinations):
            word = line.split(' ')[1]
            if word in english_dict:
                continue
            keywords_combination = tuple(keywords_dict[index] for index in combination)

            english_dict[word] = keywords_combination
            english_dict[keywords_combination] = word
            if line_number % 100000 == 0:
                print 'going over %s currently at: %s different_words_index: %s' %\
                      (english_words_path, line_number, different_words_index)
            if line_number >= last_english_line:
                break
            different_words_index += 1

    return english_dict


def create_predefined_links_dictionary(config, keywords_dict):
    keywords = [keywords_dict[x] for x in range(config.x)]
    num_of_links = len(keywords)**config.l

    essences = create_ordered_combinations(keywords, config.l, config.essence_len)
    links_to_essences = {}
    for link_i in xrange(num_of_links):
        links_to_essences[link_i] = essences[link_i]
        links_to_essences[essences[link_i]] = link_i

    keywords_combos = create_ordered_combinations(keywords, config.l, config.l)
    combos_to_links = {}
    for combo in keywords_combos:
        containing_essences = [links_to_essences[e] for e in essences if combo.issubset(e)]
        combos_to_links[combo] = set(containing_essences)

    return LinksDict(links_to_essences, combos_to_links)

#
# def create_links_dictionary(config, keywords_dict):
#     link_combinations = pseudo_random_combinations(range(config.x), config.l, 100000, avoid_all_combinations=True)
#     links_dict = {}
#     with open(links_path % config.params_tuple()) as f:
#         combination_i = 0
#         for line in f:
#             link = line.strip()
#             while link_combinations[combination_i][0] == link_combinations[combination_i][1]:
#                 combination_i += 1
#             keywords_combination = tuple(keywords_dict[index] for index in link_combinations[combination_i])
#             links_dict[link] = keywords_combination
#             links_dict[keywords_combination] = link
#             combination_i += 1
#     return links_dict
#
#
# def add_link_to_links_file(link_str, dicts, config):
#     with open(links_path % config.params_tuple(), 'a') as f:
#         f.write("\n" + link_str)
#     links_dict = create_links_dictionary(config, dicts.keywords)
#     save_links_dict(links_dict, config)
#     dicts.links = links_dict
#     return dicts


def save_dictionaries(dicts, config):
    with open(keywords_dict_path % config.params_tuple(), 'w') as f:
        pickle.dump(dicts.keywords, f)
    with open(english_dict_path % config.params_tuple(), 'w') as f:
        pickle.dump(dicts.english, f)
    save_links_dict(dicts.links, config)


def save_links_dict(links_dict, config):
    with open(links_dict_path % config.params_tuple(), 'w') as f:
        pickle.dump(links_dict, f)


def load_dictionaries(config):
    while True:
        try:
            with open(keywords_dict_path % config.params_tuple(), 'r') as f:
                keywords_dict = pickle.load(f)
            with open(english_dict_path % config.params_tuple(), 'r') as f:
                english_dict = pickle.load(f)
            with open(links_dict_path % config.params_tuple(), 'r') as f:
                links_dict = pickle.load(f)
            break
        except Exception as inst:
            print traceback.format_exc()
    dicts = Dicts(keywords_dict, english_dict, links_dict)
    return dicts


def create_and_save_dicts(config):
    dicts = create_dictionaries(config)
    print 'len of english keywords / 2 : ', len(dicts.english) / 2
    print 'creating dictionaries Done'
    save_dictionaries(dicts, config)
    print 'saving dictionaries Done'

    return dicts


def indexes_to_f_keywords(indexes, keywords_dict, config):
    keywords_len = len(keywords_dict) / 2
    total = 0
    for index in indexes:
        total *= config.essence_len
        total += index

    words = []
    for i in range(config.f):
        val = total % keywords_len
        words.append(keywords_dict[int(val)])
        total //= keywords_len

    return words


# def translate_5_keywords_to_indexes(five_words, num_of_words, keywords_dict, keywords_dict_len, essence_len):
#     sum = 0
#     for word in reversed(five_words):
#         sum *= keywords_dict_len
#         sum += keywords_dict[word]
#
#     reversed_deltas = []
#     for i in range(num_of_words):
#         reversed_deltas.append(int(sum % essence_len))
#         sum //= essence_len
#
#     return list(reversed(reversed_deltas))


if __name__ == '__main__':
    new_config = Config(1, 2, 3, 100)
    create_and_save_dicts(new_config)
    print 'done'
