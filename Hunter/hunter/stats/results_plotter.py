import csv
import difflib
import math
from operator import itemgetter
import shlex
import time
import subprocess
from os import listdir
import operator
from jumping_the_net import words_stats
from jumping_the_net.consistency_tester import read_str_list, write_str_list
from jumping_the_net.words_stats import load_stats
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import spline
from scipy.interpolate import interp1d
import matplotlib.ticker as ticker

__author__ = 'uriklarman'

def plot():

    # stats = load_stats('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/COPY_752_statsdata.txt_1000_0.txt.pkl')
    # stats2 = load_stats('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/COPY_750_statsdata.txt_750_0.txt.pkl')
    # stats = load_stats('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/COPY_70_statsdata.txt_101_0.txt.pkl')
    # stats = load_stats('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_stats/stats_7_101_2015-01-01 12:35:25.180845.pkl')
    # stats = load_stats('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_stats/stats_8_94_2015-01-01 14:58:30.815052.pkl')
    # stats = load_stats('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_stats/stats_8_750_2015-01-01 23:48:44.081310.pkl')
    stats = load_stats('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_stats/stats_7_750_2015-01-01 23:43:10.180217.pkl')

    values = stats.search_stats.values()
    # values += stats2.search_stats.values()

    num_links_required = []
    total_number_of_attempts = 0
    for words_search in values:
        search_end = [x for x in words_search if x[2] == 1.]
        total_number_of_attempts += max(1, len(search_end))
        start_i = 0
        for end in search_end:
            end_i = words_search[start_i:].index(end)
            num_links_required.append(end_i - start_i + 1)
            start_i = end_i + 1

    total_number_of_attempts = float(total_number_of_attempts)
    cdf = []
    for i in range(131):
        cdf.append(len([x for x in num_links_required if x <= i]) / total_number_of_attempts)

    plt.axis([0, 130, 0., 1.1])
    plt.plot(cdf, '-r')
    plt.xlabel('# of links passed to find feasible essence')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.show()


    # x = num_links_required
    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1)
    # n, bins, patches=ax.hist(x, 30)
    # ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%.2f')%(y/total_number_of_attempts)))
    # ax.set_ylabel('% of links')
    # # ax.set_autoscaley_on(False)
    # plt.ylim(ymin=0,ymax=12.3)      # the 101 / 7 stats /Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_stats/stats_7_101_2015-01-01 12:35:25.180845.pkl
    # # plt.ylim(ymin=0,ymax=13.8)    # the 752 / 7 stats /Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/COPY_752_statsdata.txt_1000_0.txt.pkl
    # plt.xlabel('# of links passed to find feasible essence')
    # plt.show()

    # plt.axis([0, 130, 0., 1.1])
    # plt.hist(num_links_required, bins=50)
    # plt.grid(True)
    # plt.show()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(num_links_required, weights=np.zeros_like(num_links_required) + 100. / total_number_of_attempts, bins= [x for x in range(0,132,2)])
    # n, bins, patches = ax.hist(num_links_required, bins=100, normed=1, cumulative=0)
    plt.axis([0, 130, 0., 100])
    plt.xlabel('# of links passed to find feasible essence')
    plt.ylabel('% of links')

    plt.show()


    # ax.set_ylim([0,100])
    # ax.set_ylim((0,10))
    # ax.set_xlim((1,20))
    # plt.ylim(ymin=0,ymax=10)
    # num_links_used = sorted([x[2] for x in stats.words_collected])
    # cdf = [0] * (num_links_used[-1] + 1)
    # for i in range(len(num_links_used)):
    #     cdf[num_links_used[i]] += 1
    # for i in range(1,len(cdf)):
    #     cdf[i] += cdf[i-1]
    # for i in range(len(cdf)):
    #     cdf[i] /= float(cdf[-1])
    #
    # cdf += [1.]*30
    #
    # plt.axis([0, 100, 0., 1.1])
    # plt.plot(cdf, '-r')
    # plt.xlabel('# of links passed to find feasible essence')
    # plt.ylabel('CDF')
    # plt.grid(True)
    # plt.show()
    #
    # num_links_used = [x[2] for x in stats.words_collected]
    # plt.axis([0.5, 100, 0, 30])
    # plt.hist(num_links_used,bins=50)
    # plt.xlabel('# of links passed to find feasible essence')
    # plt.ylabel('% of links')
    # plt.grid(True)
    # plt.show()



    uncut_essence_size = []
    percent_of_words_in_uncut_essence = []
    percent_of_words_in_essence = []
    for point_list in stats.search_stats.values():
        for point in point_list:
            uncut_essence_size.append(point[0])
            percent_of_words_in_uncut_essence.append(point[1])
            percent_of_words_in_essence.append(point[2])

    plt.xlabel('size of uncut essence')
    plt.ylabel('words in uncut essence')
    plt.plot(uncut_essence_size, percent_of_words_in_uncut_essence, 'or')
    plt.axis([0, 101, 0, 1.1])
    plt.show()

    plt.xlabel('size of uncut essence')
    plt.ylabel('words in essence')
    plt.plot(uncut_essence_size, percent_of_words_in_essence, 'ob')
    plt.axis([0, 101, 0, 1.1])
    plt.show()

    # search_stats_items = stats.search_stats.items()
    # keys_num = len(search_stats_items)
    # plot_per_key = 2
    # plt.subplot(keys_num, plot_per_key, 1)
    # current_plot = 0
    # for i in range(len(search_stats_items)):
    #     k,v = search_stats_items[i]
    #
    #     current_plot +=1
    #     plt.subplot(keys_num, plot_per_key, current_plot)
    #     plt.title('words: ' + str(k))
    #     plt.xlabel('size of uncut essence')
    #     uncut_essences_sizes = [x[0] for x in v]
    #     plt.ylabel('words in uncut essence')
    #     percent_in_uncut_essence = [x[1] for x in v]
    #     plt.plot(uncut_essences_sizes, percent_in_uncut_essence, 'or')
    #
    #     current_plot +=1
    #     plt.subplot(keys_num, plot_per_key, current_plot)
    #     plt.title('words: ' + str(k))
    #     plt.xlabel('size of uncut essence')
    #     uncut_essences_sizes = [x[0] for x in v]
    #     plt.ylabel('words in essence')
    #     percent_in_essence = [x[2] for x in v]
    #     plt.plot(uncut_essences_sizes, percent_in_essence, 'or')


lines_styles_params = {100:('-b',3,'|X|=100'), 250:('-g',1,'|X|=250'), 500:('--y',3,'|X|=500'), 750:('--r',1,'|X|=750')}
figsize=(6.5, 3)
# figsize=(9, 5.25)
# base_font_size = 12
# label_font_size = 1.5 * base_font_size
# ticks_font_size = 1.5 * base_font_size
# legend_font_size = 1.5 * base_font_size

def plot_encoding_A():
    x = np.linspace(0,1000,1000)
    essence_percent_1_1_2 = x**(2./4. - 1)
    essence_percent_1_2_5 = x**(5./8. - 1)
    essence_percent_1_3_15 = x**(15./19. - 1)

    plt.figure(figsize=figsize)
    plt.ylabel('|E|/|X|')
    plt.xlabel('|X| (Number of Keywords)')

    plt.plot(essence_percent_1_1_2, '-b', linewidth= 1, label='(D=1,L=1,F=2)')
    plt.plot(essence_percent_1_2_5, '--g', linewidth= 3, label='(D=1,L=2,F=5)')
    plt.plot(essence_percent_1_3_15, '-r', linewidth= 3, label='(D=1,L=3,F=15)')

    interesting_values = [100, 250, 500, 750, 1000]
    # for interesting_val in interesting_values:
    #     plt.plot((interesting_val, interesting_val), (0, 1), 'k-')

    plt.xticks(interesting_values)
    plt.yticks([x/10. for x in range(0,11)])

    plt.legend(frameon=False)
    plt.savefig('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_plots/plot_A.pdf', bbox_inches='tight')
    plt.show()


def plot_encoding_B():
    X_100_files = ['stats_100_1_1_1_0_tweet_1_2015-01-16 12:29:12.800681.pkl',
                   'stats_100_1_1_2_0_tweet_1_2015-01-14 19:33:38.758207.pkl',
                   'stats_101_1_1_3_0_tweet_1_2015-01-08 23:33:36.637198.pkl',
                   'stats_101_1_1_4_0_tweet_1_2015-01-08 22:53:54.671466.pkl',
                   'stats_101_1_1_5_0_tweet_1_2015-01-11 13:40:06.319823.pkl',
                   'stats_101_1_1_6_0_tweet_1_2015-01-07 17:57:18.178998.pkl',
                   'stats_101_1_1_7_0_tweet_1_2015-01-09 16:01:05.358417.pkl',
                   ]
    X_250_files = ['stats_250_1_1_1_0_tweet_1_2015-01-16 12:52:20.140513.pkl',
                   'stats_250_1_1_2_0_tweet_1_2015-01-09 20:15:49.749366.pkl',
                   'stats_250_1_1_3_0_tweet_1_2015-01-16 13:48:29.354144.pkl',
                   'stats_250_1_1_4_0_tweet_1_2015-01-16 14:19:03.835941.pkl',
                   'stats_250_1_1_5_0_tweet_1_2015-01-10 03:04:57.465499.pkl',
                   'stats_250_1_1_6_0_tweet_1_2015-01-10 12:26:16.197878.pkl',
                   'stats_250_1_1_7_0_tweet_1_2015-01-10 14:09:56.914258.pkl',
                   ]
    X_500_files = ['stats_512_1_1_1_0_tweet_1_2015-01-16 13:15:30.640383.pkl',
                   'stats_516_1_1_2_0_tweet_1_2015-01-16 19:37:33.062096.pkl',
                   'stats_513_1_1_3_0_tweet_1_2015-01-16 16:52:55.973796.pkl',
                   'stats_513_1_1_4_0_tweet_1_2015-01-16 17:43:31.358103.pkl',
                   'stats_512_1_1_5_0_tweet_1_2015-01-13 20:01:11.988187.pkl',
                   'stats_512_1_1_6_0_tweet_1_2015-01-14 23:04:05.424233.pkl',
                   'stats_512_1_1_7_0_tweet_1_2015-01-14 23:23:10.172862.pkl'
                   ]
    X_750_files = ['stats_749_1_1_1_0_tweet_1_2015-01-16 13:33:36.555494.pkl',
                   'stats_749_1_1_2_0_tweet_1_2015-01-14 20:40:46.187508.pkl',
                   'stats_749_1_1_3_0_tweet_1_2015-01-15 00:01:41.626655.pkl',
                   'stats_749_1_1_4_0_tweet_1_2015-01-15 00:27:17.069202.pkl',
                   'stats_749_1_1_6_0_tweet_1_2015-01-15 01:06:36.211099.pkl',
                   ]

    all_files = [(100,X_100_files),(250,X_250_files),(500,X_500_files),(750,X_750_files)]
    plot_encoding_B_functionality(all_files, changing_value='F', scale=[0., 8., 0, 15])

def plot_encoding_C():
    X_100_files = ['stats_101_1_1_5_0_tweet_1_2015-01-11 13:40:06.319823.pkl', #168
                   'stats_101_1_2_5_0_tweet_1_2015-01-17 18:04:50.532976.pkl', #141
                   'stats_101_1_3_5_0_tweet_1_2015-01-16 20:03:59.019098.pkl', #80
                   'stats_101_1_4_5_0_tweet_1_2015-01-17 18:37:50.403649.pkl', #123
                   'stats_101_1_5_5_0_tweet_1_2015-01-16 21:04:58.006120.pkl', #129
                   'stats_101_1_7_5_0_tweet_1_2015-01-16 21:40:37.716850.pkl', #80
                   ]
    X_250_files = ['stats_250_1_1_5_0_tweet_1_2015-01-17 19:07:56.098859.pkl', #95
                   'stats_250_1_2_5_0_tweet_1_2015-01-17 19:30:27.953824.pkl', #196
                  #'stats_250_1_2_5_0_tweet_1_2015-01-16 22:37:20.932075.pkl', #44
                   'stats_250_1_3_5_0_tweet_1_2015-01-17 20:56:34.499576.pkl', #114
                  #'stats_250_1_3_5_0_tweet_1_2015-01-16 22:51:20.132368.pkl', #96
                   'stats_250_1_4_5_0_tweet_1_2015-01-16 23:17:41.011809.pkl', #194
                   'stats_250_1_5_5_0_tweet_1_2015-01-16 23:50:34.813981.pkl', #122
                   'stats_250_1_7_5_0_tweet_1_2015-01-17 00:11:16.228140.pkl', #103
                   ]
    X_500_files = ['stats_512_1_1_5_0_tweet_1_2015-01-13 20:01:11.988187.pkl', #332
                   # 'stats_512_1_2_5_0_tweet_1_2015-01-17 00:27:11.635110.pkl', #224
                   'stats_512_1_2_5_0_tweet_1_2015-01-18 12:37:28.677255.pkl', #350
                   'stats_512_1_3_5_0_tweet_1_2015-01-18 14:37:22.196680.pkl',
                   # 'stats_512_1_3_5_0_tweet_1_2015-01-18 04:11:53.409700.pkl',
                  #'stats_512_1_3_5_0_tweet_1_2015-01-17 00:52:01.898238.pkl', #49
                   'stats_512_1_4_5_0_tweet_1_2015-01-17 01:06:41.592513.pkl', #133
                   'stats_512_1_5_5_0_tweet_1_2015-01-17 01:53:42.143698.pkl', #210
                   'stats_512_1_7_5_0_tweet_1_2015-01-17 02:59:33.753655.pkl', #48
                   ]
    X_750_files = ['stats_749_1_1_5_0_tweet_1_2015-01-18 03:40:19.725076.pkl', #75
                   'stats_749_1_2_5_0_tweet_1_2015-01-17 14:40:47.887296.pkl', #160
                   'stats_749_1_3_5_0_tweet_1_2015-01-17 15:27:06.480642.pkl', #525
                   'stats_749_1_4_5_0_tweet_1_2015-01-18 03:59:55.916915.pkl', #
                   ]

    all_files = [(100,X_100_files),(250,X_250_files),(500,X_500_files),(750,X_750_files)]
    # all_files = [(750,X_750_files)]
    plot_encoding_B_functionality(all_files, changing_value='L', scale=[0., 8., 0, 100])

def plot_encoding_B_functionality(all_files, changing_value, scale):
    plot_params = []
    for X_val, X_files in all_files:
        current_X_points = [[],[]]
        for stats_file in X_files:
            stats = words_stats.load_stats(stats_file)
            num_words = stats.L + stats.D + stats.F
            if changing_value == 'F':
                current_X_points[0].append(stats.F)
            elif changing_value == 'L':
                current_X_points[0].append(stats.L)



            # all encodings except those for ['wow', 'wow',...] and their likes
            flow = [x for x in stats.encoding_flow if x[4] >= (num_words / 2)]

            # successful_encoding_flow = [x for x in flow if x[2]]
            # num_of_encoding_attempts = len(flow)
            #
            # if len(successful_encoding_flow) >= 5:
            #     expected_links_needed_per_word = num_of_encoding_attempts / len(successful_encoding_flow)
            # else:
            #     # flow = [x for x in stats.encoding_flow if x[4] > 1]
            #     expected_links_needed_per_word = find_expected_num_of_links(stats, flow)
            expected_links_needed_per_word = min(find_expected_num_of_links(stats, flow),1000000)
            current_X_points[1].append(expected_links_needed_per_word)

        print 'current_X_points[0]: ', current_X_points[0]
        print 'current_X_points[1]: ', current_X_points[1]
        plot_params.append((current_X_points[0], current_X_points[1], X_val))

    plt.figure(figsize=figsize)
    for x_params in plot_params:
        line_properties = lines_styles_params[x_params[2]]

        x_axis_values = x_params[0]
        y_axis_values = x_params[1]

        x_narray = np.array(x_axis_values)
        y_narray = np.array(y_axis_values)
        x_line_space = np.linspace(x_narray.min(), x_narray.max(), 40)
        f_smooth = interp1d(x_narray, y_narray, kind='slinear')

        plt.plot(x_line_space, f_smooth(x_line_space), line_properties[0], linewidth= line_properties[1], label=line_properties[2])

    plt.ylabel('Expected Number of Links')
    plt.legend(loc=4, frameon=False, prop={'size':14})
    plt.axis(scale)
    if changing_value == 'F':
        plt.xlabel('F (Number of Function Words)')
        plt.savefig('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_plots/plot_B.pdf', bbox_inches='tight')
    elif changing_value == 'L':
        plt.xlabel('L (Number of Link Words)')
        plt.savefig('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_plots/plot_C.pdf', bbox_inches='tight')
    plt.show()


def find_expected_num_of_links(stats, flow):
    num_words = stats.L + stats.D + stats.F
    func_words_percent = stats.F / float(num_words)
    essence_size = math.floor(math.pow(stats.X, func_words_percent))
    sum_of_chances = 0.
    for link_search in flow:
        if link_search[5] >= link_search[4]:
            chance = 1
        elif link_search[4] > link_search[6]:
            chance = 0
        else:
            chance = min(math.pow(essence_size / link_search[7], link_search[4]), 1.)
        sum_of_chances += chance
    avg_chance = sum_of_chances / len(flow)
    expected_links_needed_per_word = 1 / avg_chance
    return expected_links_needed_per_word


def plot_encoding_D():

    # X_100_file = 'stats_100_1_1_2_0_tweet_1_2015-01-14 19:33:38.758207.pkl'
    # X_250_file = 'stats_256_1_1_2_0_tweet_1_2015-01-17 13:22:15.402834.pkl'
    # X_500_file = 'stats_512_1_1_2_0_tweet_1_2015-01-17 13:09:06.839638.pkl'
    X_100_file = 'stats_100_1_1_2_0_tweet_1_2015-01-17 21:27:54.405155.pkl'
    X_250_file = 'stats_256_1_1_2_0_tweet_1_2015-01-17 22:10:22.532923.pkl'
    X_500_file = 'stats_512_1_1_2_0_tweet_1_2015-01-17 22:56:16.653616.pkl'
    X_750_file = 'stats_749_1_1_2_0_tweet_1_2015-01-14 20:40:46.187508.pkl'

    # X_100_file = 'stats_100_1_1_2_0_tweet_1_2015-01-14 19:33:38.758207.pkl'
    # X_250_file = 'stats_256_1_1_2_0_tweet_1_2015-01-14 19:54:36.261821.pkl'
    # X_500_file = 'stats_512_1_1_2_0_tweet_1_2015-01-14 20:16:07.154431.pkl'
    # X_750_file = 'stats_729_1_1_2_0_tweet_1_2015-01-14 20:40:46.187508.pkl'

    # X_100_file = 'stats_101_1_1_5_0_tweet_1_2015-01-11 13:40:06.319823.pkl'
    # X_250_file = 'stats_256_1_1_5_0_tweet_1_2015-01-11 16:33:32.267943.pkl'
    # X_500_file = 'stats_512_1_1_5_0_tweet_1_2015-01-13 20:01:11.988187.pkl'
    # X_750_file = 'stats_750_1_1_5_0_tweet_1_2015-01-14 00:16:50.589827.pkl'
    # X_750_file = 'stats_750_1_2_4_0_tweet_1_2015-01-14 01:51:00.545645.pkl'

    all_files = [(100,X_100_file),(250,X_250_file),(500,X_500_file),(750,X_750_file)]

    plt.figure(figsize=figsize)
    for X, stats_file in all_files:
        stats = words_stats.load_stats(stats_file)

        chunks_starts = [0]
        for i in range(1,len(stats.encoding_flow)):
            if stats.encoding_flow[i][0] != stats.encoding_flow[i-1][0]:
                chunks_starts.append(i)

        chunks = []
        for i in range(0, len(chunks_starts)-1):
            start = chunks_starts[i]
            stop = chunks_starts[i+1]
            chunks.append(stats.encoding_flow[start:stop])
        chunks.append(stats.encoding_flow[chunks_starts[-1]:])

        num_words = stats.L + stats.D + stats.F
        good_chunks = [chunk for chunk in chunks if chunk[0][4] >= num_words / 2]
        num_links_required_in_successful_chunks = [x[-1][1] for x in good_chunks if x[-1][2]]
        if not num_links_required_in_successful_chunks:
            expected_num_links_required_in_good_chunks = []
            for chunk in good_chunks:
                expected_links_needed = find_expected_num_of_links(stats, chunk)
                expected_num_links_required_in_good_chunks.append(expected_links_needed)
            num_links_required_in_successful_chunks = expected_num_links_required_in_good_chunks

        total_number_of_attempts = float(len(good_chunks))
        cdf = []
        for i in range(int(max(num_links_required_in_successful_chunks)) + 30):
            cdf.append(len([x for x in num_links_required_in_successful_chunks if x <= i]) / total_number_of_attempts)

        plt.plot(cdf, lines_styles_params[X][0], linewidth=lines_styles_params[X][1], label=lines_styles_params[X][2])
    plt.axis([0, 20, 0., 1.1])
    plt.xlabel('Number of Links')
    plt.ylabel('CDF')
    plt.legend(loc='best', frameon=False)
    plt.savefig('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_plots/plot_D.pdf', bbox_inches='tight')
    plt.show()

def plot_encoding_E():
    plt.figure(figsize=figsize)

    download_times = load_download_times()
    max_time = int(math.ceil(max(download_times)))
    cdf = []
    for i in range(max_time + 120):
        cdf.append(len([x for x in download_times if x <= i]) / float(len(download_times)))
    plt.plot(cdf, '-r', linewidth= 3)

    plt.axis([0, 70, 0., 1.1])
    plt.xlabel('Seconds')
    plt.ylabel('CDF')
    plt.savefig('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_plots/plot_E.pdf', bbox_inches='tight')
    plt.show()

def time_page(url):
    """Load a single page and measure the time for that URL"""
    # Start recording time
    print "Loading %s"%url

    start = time.time()
    raw = "curl -silent -m 10 %s >> data_dump 2>&1"%url
    command = shlex.split(raw)
    proc = subprocess.Popen(raw, shell=True)
    proc.wait()
    stop = time.time()


    total_time = stop - start
    return total_time

def compute_all_download_times(path='/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_a_results/'):
    file_names = [ f for f in listdir(path)]
    times_of_all_files = []
    for i,file_name in enumerate(file_names):
        print 'starting file number: ',i, ' file name:', file_name
        stats = words_stats.load_stats(file_name, path)
        urls = [x[1] for x in stats.collected_words[1:]]

        current_file_times_sum = 0.
        for i,url in enumerate(urls):
            print 'currently at link: ', i
            download_time = time_page(url)
            current_file_times_sum += download_time
        print 'sum is: ', current_file_times_sum
        times_of_all_files.append(current_file_times_sum)

    timing_file_name = '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/timing.txt'
    with open(timing_file_name, 'w') as f:
        for timing in times_of_all_files:
            f.write('%s\n' % str(timing))

def load_download_times():
    timing_file_name = '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/timing.txt'
    with open(timing_file_name) as f:
        download_times = map(float, f)
    return download_times


def create_list_of_links_to_be_manually_inspected(path='/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_a_results/'):
    file_names = [ f for f in listdir(path)]
    for stats_file in file_names:
        stats = words_stats.load_stats(stats_file, path)
        csv_str_list = [x[1] +','+str(x[2])  for x in stats.collected_words[1:]]
        file_name = '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_a_results_csv/' + stats_file +'.csv'

        with open(file_name, 'w') as f:
            for link_line in csv_str_list:
                f.write('%s\n' % link_line)

def plot_encoding_F():
    files = ['/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/consistency/geo_japan_results_final_res_2.csv',
             '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/consistency/geo_swiss_results_final_res_2.csv',
             '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/consistency/geo_us_results_final_res.csv']
    colors = ['b','r','k']
    sizes = [1,3,2]
    country = ['AS', 'EU', 'US']
    plt.figure(figsize=figsize)
    for file,color,country,size in zip(files, colors, country, sizes):
        times= [[],[],[],[],[],[]]
        with open(file, 'r') as data:
            rows = csv.reader(data)
            for row in rows:
                for i in range(len(row)):
                    times[i].append(float(row[i]))
        times = [times[1], times[5]]
        lines_params = [('-'+color,size,country), ('--'+color,size,country +' 90%')]
        # lines_params = [('-'+color,3,country), ('-'+color,2,country +' 30%'), ('-'+color,1,country +' 50%'), ('--'+color,2,'Japan 70%'),  ('--'+color,1,country +' 90%')]
        for download_times, line in zip(times,lines_params):
            max_time = int(math.ceil(max(download_times)))
            cdf = []
            for i in range(max_time + 120):
                cdf.append(len([x for x in download_times if x <= i]) / float(len(download_times)))
            plt.plot(cdf, line[0], linewidth=line[1], label=line[2])

    plt.axis([0, 165, 0., 1.1])
    plt.xlabel('Seconds')
    plt.ylabel('CDF')
    plt.legend(loc=4, frameon=False)
    plt.savefig('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_plots/plot_F_merged_with_US_2.pdf', bbox_inches='tight')
    plt.show()

def plot_encoding_G():
    path = '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/consistency/'
    file_names = [ f for f in listdir(path) if 'links_sample' in f]
    files_content = []
    for file in file_names:
        current_file_essences = []

        with open(path+file, 'r') as f:
            for row in f:
                essence = [x.strip()[2:-1] for x in row.strip()[1:-1].split(',')]
                essence.sort()
                current_file_essences.append(essence)

        bad = [130, 259, 6, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 277, 152, 289, 290, 180, 311, 57, 187, 188, 65, 194, 66, 334, 83, 213, 344, 220, 93, 101, 232, 233, 106, 236, 251, 125]
        # bad = []
        good_essences = [current_file_essences[i] for i in range(len(current_file_essences)) if i not in bad]
        files_content.append(good_essences)
        # files_content.append(current_file_essences)

    num_files = len(file_names)
    similarities = [1.,]*num_files
    diffs = [[] for i in range(num_files)]

    for file_i in range(num_files):
        for essence_i in range(len(files_content[0])):
            score = difflib.SequenceMatcher(None, files_content[0][essence_i], files_content[file_i][essence_i]).ratio()
            similarities[file_i] += score
            if score != 1.:
                diffs[file_i].append((score, essence_i, files_content[0][essence_i], files_content[file_i][essence_i]))


    consistency = [min(1.,x / len(files_content[0])) for x in similarities]
    print consistency
    #sorted([y[0:2] for x in diffs for y in x if y[0] < 0.7])
    #print list(set([y[1] for x in diffs for y in x if y[0] < 0.7]))
    # print set([y[1] for y in sorted([y[0:2] for x in diffs for y in x if y[0] < 0.7])])

    plt.figure(figsize=figsize)
    plt.plot(range(len(consistency)), consistency, linewidth=2)
    plt.plot([0,10],[1,1], '--k', linewidth=1)
    plt.axis([0, 7, 0.8, 1.03])
    plt.xlabel('Days')
    plt.ylabel('Similarity')
    plt.savefig('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_plots/plot_G.pdf', bbox_inches='tight')
    plt.show()


def plot_encoding_H():
    path = '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/consistency/'

    files_prefix =[
                   # 'search_sample_2015-01-20 20:57:02.217038', # proxy US , sorted by date
                   # 'search_sample_2015-01-20 21:24:47.223142', # proxy US , sorted by date (same as above)
                   # 'search_sample_2015-01-20 22:13:02.335803', # no proxy , sorted by date
                   # 'search_sample_2015-01-20 22:41:38.932757', # no proxy , sorted by date (same as above)
                   # 'search_sample_2015-01-20 23:15:52.480177', # no proxy , using gl=US and uule
                   # 'search_sample_2015-01-21 00:59:06.438673', # no proxy , using gl=US and uule (same as above)
                   # 'search_sample_2015-01-20 23:38:50.065643', # proxy US       , using gl=US and uule
                   # 'search_sample_2015-01-21 00:13:45.073764', # proxy Swiss    , using gl=US and uule
                   # 'search_sample_2015-01-21 02:21:33.806955', # no proxy , using uule plumber example
                   # 'search_sample_2015-01-21 02:55:42.789773', # no proxy , using uule plumber example (same)
                   # 'search_sample_2015-01-21 04:21:28.742845', #no uule no proxy, sorted by date
                   # 'search_sample_2015-01-21 04:41:20.373373', #no uule no proxy, sorted by date
                   # 'search_sample_2015-01-21 05:11:50.321686', #no uule no proxy, sorted by date, tethering
                   # 'search_sample_2015-01-21 05:32:37.886852', #no uule no proxy, sorted by date, tethering (same)
                   # 'search_sample_2015-01-21 15:23:24.996675', #no uule no proxy, sorted by date
                   # 'search_sample_2015-01-21 16:13:11.841783', #no uule no proxy, sorted by date
                   # 'search_sample_2015-01-21 16:34:11.627657', #no uule no proxy, sorted by date
                   # 'search_sample_2015-01-21 16:57:19.106680', #no uule no proxy, sorted by date
                   # 'search_sample_2015-01-21 17:44:48.618489', # uule, tethering, no proxy, sorted by date
                   'search_sample_2015-01-21 18:26:22.422889', # uule, tethering, no proxy, sorted by date, 20 searches
                   'search_sample_2015-01-21 19:01:06.327492', # uule, tethering, no proxy, sorted by date, 20 searches
                   'search_sample_2015-01-21 19:40:58.077797', # uule, tethering, no proxy, sorted by date, 20 searches
                   'search_sample_2015-01-21 20:11:38.796374', # uule, tethering, no proxy, sorted by date, 20 searches
                   'search_sample_2015-01-21 20:37:45.072952', # uule, tethering, no proxy, sorted by date, 20 searches
                   'search_sample_2015-01-21 23:10:33.255295', # uule, no proxy, sorted by date, 20 searches
                   'search_sample_2015-01-21 23:58:51.596121', # uule, no proxy, sorted by date, 20 searches
                   'search_sample_2015-01-22 00:25:57.283941', # uule, no proxy, sorted by date, 20 searches
                  ]

    # &uule=w+CAIQICIeQ2hpY2FnbyxJbGxpbm9pcyxVbml0ZWQgU3RhdGVz


    samples_names = []
    for prefix in files_prefix:
        chunks_file_names = [ f for f in listdir(path) if prefix in f]
        samples_names.append(chunks_file_names)

    samples_list = []
    for sample_i in range(len(samples_names)):
        current_sample = []
        for chunk_i in range(len(samples_names[sample_i])):
            if chunk_i in [2,18,7,5]: continue
            chunk_data = read_str_list(path + samples_names[sample_i][chunk_i])
            current_sample.append(chunk_data)
        samples_list.append(current_sample)

    merged_samples_list = []
    for i in range(0,len(samples_list),2):
        merged_sample = []
        for chunk_1,chunk_2 in zip(samples_list[i], samples_list[i+1]):
            merged_chunk = (set(chunk_1).union(set(chunk_2)))
            merged_sample.append(merged_chunk)

        merged_samples_list.append(merged_sample)

    used_samples_list = merged_samples_list
    num_chunks = 20
    num_links_per_chunk = 200
    first_sample = used_samples_list[0]

    consistency = []
    diffs = []
    for sample_i,sample in enumerate(used_samples_list):
        sample_diffs = []
        diffs.append(sample_diffs)
        sample_score = 0.
        for chunk_i,chunk in enumerate(sample):
            chunk_diffs = []
            sample_diffs.append(chunk_diffs)
            # score = difflib.SequenceMatcher(None, sorted(chunk), sorted(first_sample[chunk_i])).ratio()
            score = len(chunk.intersection(first_sample[chunk_i])) / float(len(chunk))
            sample_score += score
            chunk_diffs.append(score)
            # chunk_diffs.append([link_i for link_i in range(len(chunk)) if chunk[link_i] not in first_sample[chunk_i]])

        current_consistency = sample_score/len(first_sample)
        consistency.append(current_consistency)

    print consistency

    plt.figure(figsize=figsize)
    plt.plot(range(1, len(consistency)+1), consistency)
    plt.axis([1, 7, 0., 1.])
    plt.xlabel('Days')
    plt.ylabel('Similarity')
    plt.savefig('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_plots/plot_H.pdf', bbox_inches='tight')
    plt.show()

def plot_encoding_H_new():
    path = '/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/consistency_search_new/'
    files_prefix =[
                   # 'sample_2015-01-22 23:32:18.848653', # home
                   # 'sample_2015-01-22 23:16:30.259386', # home
                   # 'sample_2015-01-22 23:55:35.644074', # home
                   # 'sample_2015-01-23 00:17:38.530574', # home
                   # 'sample_2015-01-22 22:24:31.252866', # home
                   # 'sample_2015-01-22 22:02:59.522143', # home
                   # 'sample_2015-01-22 18:36:11.969142', # B&N
                   # 'sample_2015-01-22 18:51:54.992366', # B&N
                   # 'sample_2015-01-22 18:19:49.477887', # B&N
                   # 'sample_2015-01-23 02:41:33.733844', # home
                   # 'sample_2015-01-22 20:44:55.410591', # home
                   'sample_2015-01-23 19:55:32.758853', # home
                   'sample_2015-01-23 19:41:38.854782', # home
                   'sample_2015-01-23 20:09:28.682545', # home
                   'sample_2015-01-23 20:28:56.173240', # home
                   'sample_2015-01-23 20:47:09.915023', # home
                   'sample_2015-01-23 17:19:29.124031', # home
                   'sample_2015-01-23 21:04:10.798871', # home
                   'sample_2015-01-23 21:20:49.003497', # home
                   'sample_2015-01-23 21:38:19.934710', # home
                   'sample_2015-01-23 22:06:54.244999', # home
                   'sample_2015-01-23 17:35:23.937545', # home
                    ]

    num_samples = len(files_prefix)
    samples_names = []

    for prefix in files_prefix:
        chunks_file_names = [ f for f in listdir(path) if prefix in f]
        samples_names.append(chunks_file_names)

    # bad = [9,11,65,126,130,152,158,164,212,223]
    bad = [11, 16, 36, 44, 53, 75, 112, 115, 117, 123, 153, 158, 168, 194, 199, 205, 208, 216, 225, 254, 260, 265, 270, 285, 295, 297]
    # bad = []
    chunk_ids = []
    filtered_samples_names = [[] for i in range(num_samples)]
    for chunk_i in range(300):
        current_index_names = []
        for i,prefix in enumerate(files_prefix):
            chunk_file_name = prefix+'_chunk_'+str(chunk_i)
            if chunk_file_name in samples_names[i]:
                current_index_names.append(chunk_file_name)

        if chunk_i in bad:
            print 'chunk ', chunk_i, ' in bad'
            continue
        elif len(current_index_names) == num_samples:
            chunk_ids.append(chunk_i)
            for i in range(num_samples):
                filtered_samples_names[i].append(current_index_names[i])
        else:
            print 'removing chunk: ',chunk_i, 'found only: ', current_index_names

    samples_list = []
    for sample_i in range(len(filtered_samples_names)):
        current_sample = []
        for chunk_i in range(len(filtered_samples_names[sample_i])):
            chunk_data = read_str_list(path + filtered_samples_names[sample_i][chunk_i])
            current_sample.append(chunk_data)
        samples_list.append(current_sample)
    print 'sample size is: ', len(samples_list[0])
    results = []
    all_suspects = []
    # best is now 0
    for first_sample in [samples_list[0]]:
        num_links = sum([len(x) for x in first_sample])
        max_shift = 1
        consistency_scores_per_sample = []
        for sample_i in range(len(samples_list)):
            sample_inconsistency_scores, sample_suspect = compare_search_samples(first_sample, samples_list[sample_i], max_shift, chunk_ids)
            all_suspects.append(sample_suspect)
            sample_consistency_scores = [1 - (float(x) / num_links) for x in sample_inconsistency_scores]
            consistency_scores_per_sample.append(sample_consistency_scores)

        # print consistency_scores_per_sample

        consistency_scores_by_shift = []
        for shift in range(max_shift+1):
            consistency_scores_by_shift.append([x[shift] for x in consistency_scores_per_sample])

        print consistency_scores_by_shift
        results.append(consistency_scores_by_shift)

    # avg,min consistency:
    print [(sum(x[-1])/len(x[-1]), min(x[-1])) for x in results]

    # finding best first sample :  [x[-1] for x in results]

    # finding bad : sorted(list(set([y[1] for x in all_suspects for y in x if y[0]>=3])))
    
    plt.figure(figsize=figsize)
    for shift,shift_consistency in enumerate(consistency_scores_by_shift):
        plt.plot(range(len(shift_consistency)), shift_consistency, label='Max Shift=' + str(shift))
    plt.plot([0,10],[1,1], '--k', linewidth=1)
    # plt.axis([1, len(shift_consistency), 0.8, 1.03])
    plt.axis([0, 7, 0.8, 1.03])
    plt.xlabel('Days')
    plt.ylabel('Similarity')
    # plt.legend(frameon=False, loc=4, prop={'size':13})
    plt.legend(frameon=False, loc='best')
    plt.savefig('/Users/uriklarman/Development/PycharmProjects/no_git/jumping_the_net/resources/a_plots/plot_H_new.pdf', bbox_inches='tight')
    plt.show()


# test_1.text & test_2.text
# 1. l , the lat one, is missing    - add (1,1,1)
# 2. b is replaced with x           - add (1,1,1)
# 3. c & d switched                 - add (2,0,0)
# 4. f & h switched                 - add (2,2,0)
# expected result                   -     (6,4,2)
def compare_search_samples(original_sample, compared_sample, max_shift, chunk_ids):
    shifts = range(max_shift+1)
    sample_mismatches = []
    for shift in shifts:
        shift_mismatches = []
        sample_mismatches.append(shift_mismatches)
        for chunk_i in range(len(original_sample)):
            chunk_id = chunk_ids[chunk_i]
            compared_chunk = sorted(compared_sample[chunk_i])
            original_chunk = sorted(original_sample[chunk_i])
            for link_i in range(len(original_chunk)):
                range_start = max(0, link_i-shift)
                range_stop = link_i + shift +1
                link_range = compared_chunk[range_start:range_stop]
                original_link = original_chunk[link_i]
                if original_link not in link_range:
                    # print 'miss orig sample, chunk, link: ', chunk_i, ' ', link_i,  'not found in sample ', sample_i
                    shift_mismatches.append((chunk_id,link_i,original_link))

    results = [len(x) for x in sample_mismatches]
    chunks = [ x[0] for x in sample_mismatches[-1]]
    unique_chunks =list(set(chunks))
    suspects = [(len([x for x in chunks if x ==unique]),unique) for unique in unique_chunks]
    return results, suspects


if __name__ == '__main__':
    # compute_all_download_times()

    # stats = words_stats.load_stats('stats_250_1_3_5_0_tweet_1_2015-01-17 20:56:34.499576.pkl')
    # print len(stats.encoding_flow)

    # plot_encoding_A()
    # plot_encoding_B()
    # plot_encoding_C()
    # plot_encoding_D()
    # plot_encoding_E()
    # plot_encoding_F()
    # plot_encoding_G()
    plot_encoding_H_new()

    # create_list_of_links_to_be_manually_inspected()
    pass