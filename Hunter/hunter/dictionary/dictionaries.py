import re
import cPickle as pickle
import itertools
import traceback

from hunter.dictionary.combinations_provider import load_triplets, create_arbitrary_sized_combinations_iterator


__author__ = 'uriklarman'

end_chain_word = 'done'

def create_dictionaries(keywords_path, english_words_path, links_path, X, L, start, links_only, keywords_dict):
    if not links_only:
        keywords_dict = create_keywords_dict(keywords_path, start, X)

        triplets_up_to_X = load_triplets(X)
        english_dict = map_english_words_to_keywords(keywords_dict, english_words_path, triplets_up_to_X)

    link_combinations = create_arbitrary_sized_combinations_iterator(L, X)
    links_dict = map_links_to_keywords(keywords_dict, links_path, link_combinations)

    if not links_only:
        return keywords_dict, english_dict, links_dict
    else:
        return {}, {}, links_dict


def create_keywords_dict(keywords_path, start, x):
    stop = start + x
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

def map_english_words_to_keywords(keywords_dict, english_words_path, combinations):
    new_dict = {}
    with open(english_words_path) as file:
        different_words_index = 0
        for line_number, line in enumerate(file):
            word = line.split(' ')[1]
            if word in new_dict:
                continue
            if (len(combinations[0]) == 2):
                keywords_combination = (keywords_dict[combinations[different_words_index][0]],
                                        keywords_dict[combinations[different_words_index][1]])
            elif (len(combinations[0]) == 3):
                keywords_combination = (keywords_dict[combinations[different_words_index][0]],
                                    keywords_dict[combinations[different_words_index][1]],
                                    keywords_dict[combinations[different_words_index][2]])
            new_dict[word] = keywords_combination
            new_dict[keywords_combination] = word
            if line_number % 100000 == 0:
                print 'going over file ' + english_words_path + ' currently at line: ', line_number, ' different_words_index: ', different_words_index
            if line_number >= 844587:
                break
            different_words_index += 1

    return new_dict

def map_links_to_keywords(keywords_dict, links_path, combinations_iter):
    links_dict = {}
    with open(links_path) as file:
        for line,combination in itertools.izip(file,combinations_iter):
            link = line.strip()
            keywords_combination = [0]*len(combination)
            for i,num in enumerate(combination):
                keywords_combination[i] = keywords_dict[combination[i]]
            keywords_combination = tuple(keywords_combination)
            links_dict[link] = keywords_combination
            links_dict[keywords_combination] = link
    return links_dict
    # new_dict = {}
    # with open(links_path) as file:
    #     for index, line in enumerate(file):
    #         word = line.strip()
    #         keywords_combination = (keywords_dict[combinations[index][0]], keywords_dict[combinations[index][1]])
    #         new_dict[word] = keywords_combination
    #         new_dict[keywords_combination] = word
    #
    # return new_dict

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

def add_link_to_links_file(link_str, keywords_dict, X, L):
    with open('resources/links.txt.txt', 'a') as f:
        f.write("\n" +link_str)
    keywords_dict, english_dict, links_dict = create_and_save_dicts(X, L, links_only=True, keywords_dict=keywords_dict)
    return links_dict

def save_dictionaries(keywords_dict, english_dict, links_dict, X, L, links_only):
    if not links_only:
        with open('resources/dictionaries_pkl/keywords_dict_%d_%d.pkl'%(X,L), 'w') as f:
            pickle.dump(keywords_dict, f)
        with open('resources/dictionaries_pkl/english_dict.pkl', 'w') as f:
            pickle.dump(english_dict, f)

    with open('resources/dictionaries_pkl/links_dict_%d_%d.pkl'%(X,max(L,3)), 'w') as f:
            pickle.dump(links_dict, f)

def load_dictionaries(X, L):
    while True:
        try:
            with open('resources/dictionaries_pkl/keywords_dict_%d_%d.pkl'%(X,L), 'r') as f:
                keywords_dict = pickle.load(f)
            with open('resources/dictionaries_pkl/english_dict.pkl', 'r') as f:
                english_dict = pickle.load(f)
            with open('resources/dictionaries_pkl/links_dict_%d_%d.pkl'%(X,max(L,3)), 'r') as f:
                links_dict = pickle.load(f)
            break
        except Exception as inst:
            print traceback.format_exc()

    return keywords_dict, english_dict, links_dict

def create_and_save_dicts(X, L, dict_first_word_i=0, links_only=False, keywords_dict=None):
    keywords_dict, english_dict, links_dict = create_dictionaries(
        '/Users/uriklarman/Development/PycharmProjects/keywords_learning/pickled/topic_dict_words.pkl',
        'resources/written.num', 'resources/links.txt.txt', X, L, dict_first_word_i, links_only, keywords_dict)
    print 'len of english keywords / 2 : ', len(english_dict) / 2
    print 'creating dictionaries Done'
    save_dictionaries(keywords_dict, english_dict, links_dict, X, L, links_only)
    print 'saving dictionaries Done'

    return keywords_dict, english_dict, links_dict

# def read_word_count():
#     with open('resources/pickled_files/word_count_dict.pkl', 'r') as f:
#         return pickle.load(f)

if __name__ == '__main__':
    X=101
    L=1
    create_and_save_dicts(X,L)
    # keywords_dict, english_dict, links_dict = load_dictionaries(X,L)
    # print 'done'

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
