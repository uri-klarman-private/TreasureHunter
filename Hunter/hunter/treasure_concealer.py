from datetime import timedelta, datetime
import sys
import traceback
from time import sleep
import os
import signal
import random
import math
import decimal

from hunter.dictionary import dictionaries
from hunter.dictionary.dictionaries import resources_path
from search.search import Search
from stats.words_stats import WordsStats, print_stats, stats_dir_path, load_stats
from distillery import Distillery
from matplotlib import pyplot as plt

__author__ = 'uriklarman'

sidestep_threshold = 600
tweets_path = dictionaries.resources_path + 'tweets/'
final_stats_dir_path = resources_path + 'final_stats/'


def timeout_handler(signum, frame):
    print('distillery timed out with signal', signum)
    raise RuntimeError("distillery timed out")


def find_link(words, search_engine, distillery, dicts, stats, threshold=10000):
    links_list, next_url = search_engine.new_search(words, words[0] != words[1])
    link_i = 0
    link_found = False
    while link_i < threshold:
        for link in links_list:

            if 'pdf' in link or 'datalounge' in link or 'github' in link or 'ufdc.ufl.edu' in link:
                continue

            link_i += 1
            while True:
                try:
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(15)
                    essence, uncut_essence = distillery.distill(link)
                    signal.alarm(0)
                    break

                except RuntimeError as r:
                    signal.alarm(0)
                    print(traceback.format_exc())
                    print 'Failed to distill (RuntimeError). trying again...'
                    link = "http://google.com"
                    distillery.restart_browser()
                except BaseException as b:
                    signal.alarm(0)
                    print(traceback.format_exc())
                    print 'Failed to distill - some other error!!!. trying again...'
                    link = "http://google.com"
                    continue_loop = True
                    if not continue_loop:
                        break
                    distillery.restart_browser()

            # link_found = set(words).issubset(set(essence)) and 4 <= len(essence) <= 18
            link_found = set(words).issubset(set(essence)) #and 9 <= len(essence)
            stats.update(link_i, link, link_found, words, threshold, essence, uncut_essence)

            if link_found or link_i >= threshold:
                break
        if link_found or link_i >= threshold:
            break

        if next_url:
            stop_trying = False
            try:
                sleep(1)
                links_list, next_url = search_engine.continuing_search(next_url)
            except Exception as inst:
                print(traceback.format_exc())
                stop_trying = True
        else:
            stop_trying = True

        if stop_trying:
            print '!' * 30
            print "Could not continue search. given next_url: '%s'" % (next_url)
            print '!' * 30
            link_found, link_i, link, essence = (False, 0, '', [])
            break

    return link_found, link, essence


def conceal_step(data_words, words, first_link_word, insert_link_word_in_d, choose_new_link_word, search_engine,
                 distillery, dicts, stats):
    if insert_link_word_in_d:
        data_words.insert(words, 0)
        words[0] = first_link_word

    link_found, link, essence = find_link(words, search_engine, distillery, dicts, stats, sidestep_threshold)

    if link_found:
        next_words = [data_words.pop()]
    else:
        # save D-word for next attempt, and copy L1-word into D-word
        next_words = [words[0]]
        words[0] = words[1]

        sidestep_found, link, essence = find_link(words, search_engine, distillery, dicts, stats)
        if not sidestep_found:
            print 'oh boy... No link was found for side stepping.'

    if link not in dicts.links:
        dictionaries.add_link_to_links_file(link, first_link_word, choose_new_link_word, words, essence, dicts, config)

    link_words = dicts.links[link]
    first_link_word = link_words[0]
    next_words += link_words[1:]
    next_words += dictionaries.indexes_to_f_keywords([essence.index(w) for w in words], dicts.keywords, config)

    return next_words, link, first_link_word


def conceal(tweet_file, config, endword_index=False):
    dicts = dictionaries.load_dictionaries(config)
    print 'keywords (x) = ', config.x
    print 'Essence len = ', config.essence_len
    distillery = Distillery(config.essence_len, dicts.keywords)
    search_engine = Search()
    raw_data_words = open(tweets_path + tweet_file).read().split()
    data_words = [keyword for word in raw_data_words for keyword in
                  dicts.english["".join(c for c in word.lower() if c not in ('!', '.', ':', ',', '?', '"', '-'))]]

    if endword_index:
        words = [dicts.keywords[endword_index]] * config.w
    else:
        words = [dicts.keywords[config.x - 1]] * config.w

    collected_words = [(words, '', '')]
    stats = WordsStats(config, tweet_file, collected_words)

    try:
        while True:

            # Avoid inserting 3rd link word in data
            # iteration_type = len(collected_words) % 10
            iteration_type = 1

            if iteration_type == 0:
                insert_link_word_in_d = True
                choose_new_link_word = False
            elif iteration_type == 1:
                first_link_word = 'This string is ignored'
                insert_link_word_in_d = False
                choose_new_link_word = True
            else:
                insert_link_word_in_d = False
                choose_new_link_word = False


            words, link, first_link_word = conceal_step(data_words, words, first_link_word, insert_link_word_in_d,
                                                        choose_new_link_word, search_engine, distillery, dicts, stats)
            collected_words.append((words, link, first_link_word,))
            if not data_words:
                break

    except Exception:
        print(traceback.format_exc())
        t, v, tb = sys.exc_info()
        # distillery.browser.close()
        raise t, v, tb

    print "collected words are: %s" % collected_words
    return collected_words


# def can_we_find_links_in_google():
#     config = dictionaries.Config(1, 2, 2, 89, 10, 200)
#     dicts = dictionaries.load_dictionaries(config)
#     distillery = Distillery(config.essence_len, dicts.keywords)
#     search_engine = Search()
#
#     total = 0
#     false_positives = 0
#     link_found = False
#
#     for key, value in dicts.links.iteritems():
#         links_list, next_url = search_engine.new_search(key, do_filter=False)
#
#         while not link_found:
#             for link in links_list:
#                 if link == value:
#                     pass
#         print key, value


def chances(x):
    if x[4] != x[6]:
        return 0.
    else:
        dlf = 5
        subgroup = 9
        uncut = x[7]

        chance_enum = decimal.Decimal(math.factorial(uncut-dlf) * math.factorial(subgroup))
        chance_denum = decimal.Decimal(math.factorial(uncut) * math.factorial(subgroup-dlf))

        chance = chance_enum / chance_denum

        return chance

def print_stats_and_stuff():

    # all_files = os.listdir(final_stats_dir_path)
    runs = []
    run_deltas = []
    # for filename in all_files:
    #     run_stats = load_stats(filename, final_stats_dir_path)
    #     print filename
    #     print run_stats.encoding_flow[-1]
    #     runs.append(run_stats)

    # filename = 'stats_1_2_2_243_1_tweet_CO_01.txt_2015-08-11 12:42:10.388835.pkl'
    # filename = 'stats_1_2_2_243_1_tweet_CO_01.txt_2015-08-11 14:57:23.195323.pkl'
    # filename = 'stats_1_2_2_243_1_tweet_CO_01.txt_2015-08-11 15:30:40.787954.pkl'
    # filename = 'stats_1_2_2_3000_1_tweet_CO_01.txt_2015-08-11 15:52:17.508493.pkl'
    # filename = 'stats_1_2_2_2800_1_tweet_CO_01.txt_2015-08-11 16:08:03.856888.pkl'
    # filename = 'stats_1_2_2_243_0_tweet_CO_01.txt_2015-08-11 23:36:51.564624.pkl'
    # filename = 'stats_1_2_2_243_2_tweet_CO_01.txt_2015-08-12 17:27:03.263540.pkl'
    # filename = 'stats_1_2_2_243_0_tweet_CO_01.txt_2015-08-12 18:04:57.329819.pkl'
    filename = 'stats_1_2_2_243_0_tweet_CO_01.txt_2015-08-13 01_09_10.304473.pkl'



    run_stats = load_stats(filename, stats_dir_path)
    words = set.union(*[set(x[10]) for x in run_stats.encoding_flow])
    uncut_essences = [x[12] for x in run_stats.encoding_flow]
    found_dict = {}
    for uncut in uncut_essences:
        for keyword in uncut:
            # if keyword in words:
            #     continue
            if keyword not in found_dict:
                found_dict[keyword] = 0
            found_dict[keyword] += 1

    found_words = []
    for k,v in found_dict.iteritems():
        found_words.append((k, v))

    found_words = sorted(found_words, key=lambda x: x[1])
    a = [(x, x[0] in words) for x in found_words]
    print a

    all_5_keywords_steps = [x for x in run_stats.encoding_flow if x[4] == 5]
    decimal_chance = [chances(x) for x in all_5_keywords_steps]
    chance = [float(x) for x in decimal_chance]
    #### THIS IS WRONG: need to break it according to each different Clue,
    #### or bad clues takes the focus

    steps_per_keyword = []

    chance_multiplyed = []

    for j in range(int(math.ceil(1000/sum(chance)))):
        chance_multiplyed += chance

    for i in range(100):
        random.shuffle(chance_multiplyed)
        chance_sum = 0.
        i = 0
        while chance_sum < 1.:
            chance_sum += chance_multiplyed[i]
            i += 1
        steps_per_keyword.append(i)



    sorted_steps = sorted(steps_per_keyword)
    max_steps = int(math.ceil(max(sorted_steps)))
    cdf = []
    for i in range(max_steps + 2):
        cdf.append(len([x for x in steps_per_keyword if x <= i]) / float(len(steps_per_keyword)))
    # for i in range(24):
    # cdf.append(len([x for x in hours if x <= i]) / float(len(hours)))

    plt.axis([0, 600, 0., 1.1])
    plt.plot(cdf, '-r')
    plt.xlabel('Steps')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.show()
    print 'done'


    # n, bins, patches = plt.hist(expected_steps, 50, normed=0, facecolor='g', alpha=0.75)
    # stub = range(10)
    # stub += (range(3,7))
    # stub += (range(4,6))
    # n, bins, patches = plt.hist(stub, 10, facecolor='g', alpha=0.75)
    # n, bins, patches = plt.hist(expected_steps, 20, facecolor='g', alpha=0.75)


    # plt.xlabel('Smarts')
    # plt.ylabel('Probability')
    # plt.title('Histogram of IQ')
    # plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    # plt.axis([0, 1000, 0, 500])
    # plt.grid(True)
    # plt.show()

    # [[x[:9] for x in run_stats.encoding_flow if x[2]] for run_stats in runs]
    for run in runs:

        times = [datetime.strptime(x[-1], '%Y-%m-%d %H:%M:%S.%f') for x in run.encoding_flow]
        deltas = [timedelta(seconds=0)]
        deltas += [times[i] - times[i - 1] for i in range(1, len(run.encoding_flow))]
        threshold = timedelta(seconds=60)
        large_deltas_i = [i for i in range(len(deltas)) if deltas[i] > threshold]

        change_steps = [i for i in range(len(run.encoding_flow) - 1) if
                        run.encoding_flow[i][0] != run.encoding_flow[i + 1][0]]
        forward_steps = [i for i in change_steps if run.encoding_flow[i][3] == 'forward']
        tmp_forwrd = [0] + forward_steps
        forward_deltas = [times[tmp_forwrd[i]] - times[tmp_forwrd[i - 1]] for i in range(1, len(tmp_forwrd))]

        fwd_delta_without_large_deltas = []
        for step_i in range(len(forward_steps)):
            step = forward_steps[step_i]
            if step_i == 0:
                prev_step = 0
            else:
                prev_step = forward_steps[step_i - 1]
            relevant_large_deltas_i = [i for i in large_deltas_i if i > prev_step and i <= step]
            time_to_reduce = timedelta(seconds=0)
            for relevant_i in relevant_large_deltas_i:
                time_to_reduce += deltas[relevant_i]

            fwd_delta_without_large_deltas.append(forward_deltas[step_i] - time_to_reduce)

        run_deltas.append(fwd_delta_without_large_deltas)

    run_sums = [sum(x, timedelta()) for x in run_deltas]

    hours = [x.total_seconds() / 3600.0 for x in run_sums]
    sorted_hours = sorted(hours)
    print sorted_hours

    max_time = int(math.ceil(max(sorted_hours)))
    cdf = []
    for i in range(max_time + 2):
        cdf.append(len([x for x in hours if x <= i]) / float(len(hours)))
    # for i in range(24):
    # cdf.append(len([x for x in hours if x <= i]) / float(len(hours)))

    # plt.axis([0, 24, 0., 1.1])
    plt.plot(cdf, '-r')
    plt.xlabel('Hours')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.show()
    print 'done'

    steps_times = []
    for run in run_deltas:
        steps_times += [x.total_seconds() / 60.0 for x in run]

    max_time = int(math.ceil(max(steps_times)))
    cdf = []
    for i in range(max_time + 120):
        cdf.append(len([x for x in steps_times if x <= i]) / float(len(steps_times)))

    # plt.axis([0, 24, 0., 1.1])
    plt.plot(cdf, '-r')
    plt.xlabel('Minutes')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    # print_stats_and_stuff()

    # can_we_find_links_in_google()

    tweet_file = 'tweet_CO_01.txt'
    config = dictionaries.Config(1, 2, 2, 243)
    # config = dictionaries.Config(1, 2, 2, 2800, shuffle_keywords_seed=1)
    dictionaries.create_and_save_dicts(config)
    conceal(tweet_file, config)
    print 'done'
