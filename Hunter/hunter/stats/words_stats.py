from datetime import datetime

__author__ = 'uriklarman'
import cPickle as pickle

stats_dir_path = '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_stats/'

class WordsStats:
    def __init__(self, X, D, L, F, dict_first_word_i, tweet_file, collected_words, groups):
        self.X = X
        self.D = D
        self.L = L
        self.F = F
        self.dict_first_word_i = dict_first_word_i
        self.tweet_file = tweet_file
        self.filename = 'stats_%d_%d_%d_%d_%d_%s_%s.pkl'%(X, D, L, F, dict_first_word_i, tweet_file, str(datetime.now()))
        print 'stats file name is: ', self.filename

        self.uncut_essence_keywords_count = {}
        self.searches_count_per_keyword = {}

        self.encoding_flow = []
        self.collected_words = collected_words
        self.collected_words_flow = []

        self.groups = groups
        self.groups_flow = []


    def update(self, link_i, words, traceback_threshold, essence, uncut_essence, collected_words):
        self.update_encoding_flow(link_i, words, traceback_threshold, essence, uncut_essence, collected_words)
        self.update_keywords_stats(words, uncut_essence)
        self.save_stats()

    def update_encoding_flow(self, link_i, words, traceback_threshold, essence, uncut_essence, collected_words):
        words_set = set(words)
        essence_set = set(essence)
        uncut_essence_set = set(uncut_essence)

        link_found = words_set.issubset(essence_set)
        num_words_in_essence = len(words_set.intersection(essence_set))

        words_in_uncut_essence = words_set.issubset(uncut_essence_set)
        num_words_in_uncut_essence = len(words_set.intersection(uncut_essence_set))

        do_traceback = (not link_found) and (link_i == traceback_threshold)
        encoding_flow_item = [len(collected_words)-1, link_i, link_found, do_traceback, len(words_set), num_words_in_essence, num_words_in_uncut_essence, len(uncut_essence), words]
        print 'encoding_flow_item:'
        print encoding_flow_item
        self.encoding_flow.append(encoding_flow_item)
        # if link_found or do_traceback:
        #     highlight_item = [len(collected_words)-1, link_i, link_found, do_traceback, words]
        #     print 'highlight_item:'
        #     print highlight_item
        #     self.encoding_highlight.append(highlight_item)

    def update_keywords_stats(self, words, uncut_essence):
        for word in uncut_essence:
            if word not in self.uncut_essence_keywords_count:
                self.uncut_essence_keywords_count[word] = 0
            self.uncut_essence_keywords_count[word] += 1

        for word in set(words):
            if word not in self.searches_count_per_keyword:
                self.searches_count_per_keyword[word] = 0
            self.searches_count_per_keyword[word] += 1

    def save_stats(self):
        with open(stats_dir_path + self.filename, 'w') as f:
            pickle.dump(self, f)

    def update_collected_words(self, collected_words, groups):
        self.collected_words_flow.append(collected_words[:])
        self.groups_flow.append(groups[:])
        self.save_stats()

def load_stats(file_path, path=None):
    if not path:
        path = stats_dir_path
    with open(path + file_path, 'r') as f:
            stats = pickle.load(f)
    return stats


# def __str__(self):
    #     string = '*'*30
    #     string += '\n' + self.filename + '\n'
    #     string += 'Percentage (word, essence, unique_keywords): \n'
    #     percentage_list = [pair for pair in self.searches_count_per_keyword.items()]
    #     percentage_list.sort(key=lambda tup: tup[1][2], reverse=True)
    #     for x in percentage_list:
    #         string += x[0] + ': ' + "{:3.4f}".format(x[1][2]) + ' (%d)'%(x[1][1])  + '  ,  ' + "{:1.5f}".format(x[1][4]) + ' (%d)'%(x[1][1]) +'\n'
    #
    #     string += '\n\nEssence appearances: \n'
    #     essence_list = [pair for pair in self.essence_word_count.items()]
    #     essence_list.sort(key=lambda tup: tup[1], reverse=True)
    #     for x in essence_list:
    #         string += x[0] + '   :   ' + str(x[1]) + '\n'
    #
    #     string += '\n\nunique_keywords appearances: \n'
    #     unique_list = [pair for pair in self.uncut_essence_keywords_count.items()]
    #     unique_list.sort(key=lambda tup: tup[1], reverse=True)
    #     for x in unique_list:
    #         string += x[0] + '   :   ' + str(x[1]) + '\n'
    #
    #     return string

