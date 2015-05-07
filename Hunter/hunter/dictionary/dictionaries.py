import re
import cPickle as pickle
import itertools
import traceback

from hunter.dictionary.combinations_provider import create_pseudo_random_combinations, create_ordered_combinations


__author__ = 'uriklarman'
keywords_learner_path = '../../../KeywordsLearner/keywordslearner/'
keywords_path = keywords_learner_path + 'resources/LDA_result/topic_words.pkl'
english_words_path = keywords_learner_path + 'resources/LDA_input/written.num'
links_path = '../resources/links.txt'
dicts_pkl_path = '../resources/dictionaries_pkl/'
keywords_dict_path = dicts_pkl_path + 'keywords_dict.pkl'
english_dict_path = dicts_pkl_path + 'english_dict.pkl'
links_dict_path = dicts_pkl_path + 'links_dict.pkl'

last_english_line = 844587


def create_dictionaries(X, L, start):
    keywords_dict = create_keywords_dict(start, X)
    english_dict = create_english_dict(keywords_dict)
    links_dict = create_links_dictionary(X, L, keywords_dict)

    return keywords_dict, english_dict, links_dict


def create_keywords_dict(start, X):
    stop = start + X
    keywords_dict = {}
    with open(keywords_path) as file:
        next_word_i = 0
        regex = re.compile('[^a-zA-Z]')
        for index, line in enumerate(file):
            if index < start or index >= stop:
                continue
            if '#' in line:
                stop += 1
                continue
            word = regex.sub('', line)
            if word in keywords_dict:
                print 'word found in dict! ', word
                stop += 1
                continue
            if len(word) <= 2:
                stop += 1
                continue
            keywords_dict[word] = next_word_i
            keywords_dict[next_word_i] = word
            next_word_i += 1

    print 'keywords_dict size is: ', len(keywords_dict)
    return keywords_dict


def create_english_dict(keywords_dict, keywords_per_word=3):
    combinations = create_ordered_combinations(range(X), keywords_per_word)

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
                print 'going over ', english_words_path, ' currently at: ', line_number, ' different_words_index: ', different_words_index
            if line_number >= last_english_line:
                break
            different_words_index += 1

    return english_dict


def create_links_dictionary(X, L, keywords_dict):
    link_combinations = create_pseudo_random_combinations(range(X), L, result_limit=100000, avoid_all_combinations=True)
    links_dict = {}
    with open(links_path) as f:
        for line, combination in itertools.izip(f,link_combinations):
            link = line.strip()
            keywords_combination = tuple(keywords_dict[index] for index in combination)
            links_dict[link] = keywords_combination
            links_dict[keywords_combination] = link
    return links_dict


def add_link_to_links_file(link_str, keywords_dict, X, L):
    with open('resources/links.txt.txt', 'a') as f:
        f.write("\n" +link_str)
    links_dict = create_links_dictionary(X,L,keywords_dict)
    save_links_dict(links_dict)
    return links_dict


def save_dictionaries(keywords_dict, english_dict, links_dict):
    with open(keywords_dict_path, 'w') as f:
        pickle.dump(keywords_dict, f)
    with open(english_dict_path, 'w') as f:
        pickle.dump(english_dict, f)
    save_links_dict(links_dict)


def save_links_dict(links_dict):
    with open(links_dict_path, 'w') as f:
        pickle.dump(links_dict, f)


def load_dictionaries():
    while True:
        try:
            with open(keywords_dict_path, 'r') as f:
                keywords_dict = pickle.load(f)
            with open(english_dict_path, 'r') as f:
                english_dict = pickle.load(f)
            with open(links_dict_path, 'r') as f:
                links_dict = pickle.load(f)
            break
        except Exception as inst:
            print traceback.format_exc()

    return keywords_dict, english_dict, links_dict


def create_and_save_dicts(X, L, dict_first_word_i=0):
    keywords_dict, english_dict, links_dict = create_dictionaries(X,L,dict_first_word_i)
    print 'len of english keywords / 2 : ', len(english_dict) / 2
    print 'creating dictionaries Done'
    save_dictionaries(keywords_dict, english_dict, links_dict)
    print 'saving dictionaries Done'

    return keywords_dict, english_dict, links_dict


def translate_indexes_to_F_keywords(indexes, keywords_dict, essence_len, F):
    keywords_len = len(keywords_dict) / 2
    sum = 0
    for index in indexes:
        sum *= essence_len
        sum += index

    words = []
    for i in range(F):
        val = sum % keywords_len
        words.append(keywords_dict[int(val)])
        sum //= keywords_len

    return words


def translate_5_keywords_to_indexes(five_words, num_of_words, keywords_dict, keywords_dict_len, essence_len):
    sum = 0
    for word in reversed(five_words):
        sum *= keywords_dict_len
        sum += keywords_dict[word]

    reversed_deltas = []
    for i in range(num_of_words):
        reversed_deltas.append(int(sum % essence_len))
        sum //= essence_len

    return list(reversed(reversed_deltas))


if __name__ == '__main__':
    X=100
    L=3
    create_and_save_dicts(X,L)
    keywords_dict, english_dict, links_dict = load_dictionaries()
    print 'done'

    # with open('resources/written_keywords.num') as file:
    #     words = []
    #     regex = re.compile('[^a-zA-Z]')
    #     for index, line in enumerate(file):
    #         word = regex.sub('', line.split()[1]).lower()
    #         words.append(word)
    #
    # words_set = set()
    #
    # unique_list = []
    # for word in words:
    #     if word not in words_set:
    #         words_set.add(word)
    #         unique_list.append(word)
    # with open('resources/written_keywords_set.num', 'w') as file:
    #     for item in unique_list:
    #         file.write("%s\n" % item)
    #
    # word_count = read_word_count()
    # sorted_word_count = sorted(word_count.items(), key=operator.itemgetter(1), reverse=True)
    # for word in sorted_word_count:
    #     print word
    #
    #
    #
    #
    #
    # main(1500, 100)
