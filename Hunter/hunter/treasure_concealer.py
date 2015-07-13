from datetime import timedelta, datetime
import sys
import traceback
from time import sleep
import os
import signal
import random
import math
import itertools

from hunter.dictionary import dictionaries
from hunter.dictionary.dictionaries import resources_path
from hunter.search.search import Search
from hunter.stats.words_stats import WordsStats, print_stats, stats_dir_path, load_stats
from hunter.distillery import Distillery
from matplotlib import pyplot as plt

__author__ = 'uriklarman'

forward_threshold = 600
sidestep_threshold = 10000
link_words_threshold = 100
max_essence_size = 20
tweets_path = dictionaries.resources_path + 'tweets/'
final_stats_dir_path = resources_path + 'final_stats/'


def timeout_handler(signum, frame):
    print('distillery timed out with signal', signum)
    raise RuntimeError("distillery timed out")


def distill_link(link, distillery, dicts):
    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(15)
        essence, uncut_essence = distillery.distill(link)
        signal.alarm(0)
        return True, essence, uncut_essence

    except RuntimeError as r:
        signal.alarm(0)
        print(traceback.format_exc())
        distillery.restart_browser()
    except BaseException as b:
        signal.alarm(0)
        print(traceback.format_exc())
        print 'Failed to distill - some other error!!!. trying again...'
        distillery.restart_browser()
    return False, [], []


def find_link(words, link_i, search_engine, distillery, dicts, threshold, filter_search, stats):
    links_list, next_url = search_engine.new_search(words, filter_search)
    link_found = False
    while True:
        for link in links_list:
            if 'pdf' in link or 'github' in link:
                continue
            link_i += 1
            distill_success, essence, uncut_essence = distill_link(link, distillery, dicts)
            link_found = distill_success and len(uncut_essence) <= max_essence_size and set(words).issubset(set(essence))
            stats.update(link_i, link, words, threshold, essence, uncut_essence)
            if link_found or link_i >= threshold:
                return link_found, link_i, link, essence

        if next_url:
            try:
                links_list, next_url = search_engine.continuing_search(next_url)
            except Exception as inst:
                print "Could not continue search. given next_url: '%s'" % next_url
                print(traceback.format_exc())
                return link_found, link_i, link, essence
        else:
            print "Could not continue search. given next_url: '%s'" % next_url
            return link_found, link_i, link, essence


def find_link_and_link_words(words, search_engine, distillery, dicts, stats, threshold, filter_search):
    link_i = 0
    while link_i < forward_threshold:
        link_found, link_i, link, essence = find_link(words, link_i, search_engine, distillery, dicts, threshold, filter_search, stats)
        if link_found:
            for link_words in itertools.combinations(words, config.l):
                link_words_match_link = match_link_words_to_link(link, link_words, search_engine)
                if link_words_match_link:
                    return True, essence, link_words, link
    return False, [], [], ''


def match_link_words_to_link(link, link_words, search_engine):
    tries = 0
    links_list, next_url = search_engine.new_search(link_words, do_filter=True)
    while tries < link_words_threshold:
        if link in links_list:
            return True
        else:
            tries += len(links_list)
            links_list, next_url = search_engine.continuing_search(next_url)
    return False


def conceal_step(data_words, words, search_engine, distillery, dicts, stats):
    forward_link_found, essence, link_words, link = find_link_and_link_words(words, search_engine, distillery, dicts, stats, forward_threshold, True)
    if forward_link_found:
        next_words = [data_words.pop()]
        next_words += link_words
        next_words += dictionaries.indexes_to_f_keywords([essence.index(w) for w in words], dicts.keywords, config)
    else:
        sidestep_link_found, essence, link_words, link = find_link_and_link_words(words[1:], search_engine, distillery, dicts, stats, sidestep_threshold, False)
        if sidestep_link_found:
            next_words = [words[0]]
            next_words += link_words
            next_words += dictionaries.indexes_to_f_keywords([essence.index(w) for w in words], dicts.keywords, config)
        else:
            print 'oh boy... No link was found for side stepping.'

    return next_words, link


def conceal(tweet_file, config, endword_index=False):
    dicts = dictionaries.load_dictionaries(config)
    print 'keywords (x) = ', config.x
    print 'Essence len = ', config.essence_len
    distillery = Distillery(config.essence_len, dicts.keywords)
    search_engine = Search()
    raw_data_words = open(tweets_path + tweet_file).read().split()
    data_words = [keyword for word in raw_data_words for keyword in dicts.english["".join(c for c in word.lower() if c not in ('!', '.', ':', ',', '?', '"', '-'))]]

    if endword_index:
        words = [dicts.keywords[endword_index]] * config.w
    else:
        words = [dicts.keywords[config.x - 1]] * config.w

    collected_words = [(words, '')]
    stats = WordsStats(config, tweet_file, collected_words)

    while True:
        try:
            words, link = conceal_step(data_words, words, search_engine, distillery, dicts, stats)
            collected_words.append((words, link))
            if not data_words:
                break

        except Exception:
            print(traceback.format_exc())
            t, v, tb = sys.exc_info()
            # raise t, v, tb

    print "collected words are: %s" % collected_words
    return collected_words


def print_stats_and_stuff():
    all_files = os.listdir(final_stats_dir_path)

    runs = []
    for filename in all_files:
        run_stats = load_stats(filename, final_stats_dir_path)
        print filename
        print run_stats.encoding_flow[-1]
        runs.append(run_stats)

    run_deltas = []
    for run in runs:

        times = [datetime.strptime(x[-1], '%Y-%m-%d %H:%M:%S.%f') for x in run.encoding_flow]
        deltas = [timedelta(seconds=0)]
        deltas += [times[i] - times[i-1] for i in range(1, len(run.encoding_flow))]
        threshold = timedelta(seconds=60)
        large_deltas_i = [i for i in range(len(deltas)) if deltas[i] > threshold]

        change_steps = [i for i in range(len(run.encoding_flow)-1) if run.encoding_flow[i][0] != run.encoding_flow[i+1][0]]
        forward_steps = [i for i in change_steps if run.encoding_flow[i][3] == 'forward']
        tmp_forwrd = [0] + forward_steps
        forward_deltas = [times[tmp_forwrd[i]] - times[tmp_forwrd[i-1]] for i in range(1, len(tmp_forwrd))]

        fwd_delta_without_large_deltas = []
        for step_i in range(len(forward_steps)):
            step = forward_steps[step_i]
            if step_i == 0:
                prev_step = 0
            else:
                prev_step = forward_steps[step_i-1]
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
    #     cdf.append(len([x for x in hours if x <= i]) / float(len(hours)))

    # plt.axis([0, 24, 0., 1.1])
    plt.plot(cdf, '-r')
    plt.xlabel('Hours')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.show()
    print 'done'

    steps_times = []
    for run in run_deltas:
        steps_times += [x.total_seconds()/60.0 for x in run]

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
    tweet_file = 'tweet_CO_09.txt'
    config = dictionaries.Config(1, 2, 2, 89, 10, 200)
    # dictionaries.create_and_save_dicts(config)
    conceal(tweet_file, config)
    print 'done'
