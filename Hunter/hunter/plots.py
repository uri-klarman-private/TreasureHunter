import math
import os
import random
from scipy.misc import comb
from hunter.stats.words_stats import load_stats
from hunter.treasure_concealer import final_stats_dir_path, chances, tweets_path


__author__ = 'uriklarman'
import matplotlib.pyplot as plt
import numpy as np

figures_dir = '/Users/uriklarman/Papers/shadownet-paper/sigcomm16/figures/'
figsize=(6.5, 3)
styles = {0:('-b',3), 1:('-g',3), 2:('-r',3), 3:('--b',3), 4:('--g',3), 5:('--r',3), 6:('-b',1), 7:('-g',1)}
max_ue = 100


def role_of_e():
    plt.figure(figsize=figsize)
    c = 5
    e_values = [5,7,9,11,13,15]

    for i, e in enumerate(e_values):
        ue, expected = compute_data_points(e, int(c))
        plt.plot(ue, expected, styles[i][0], linewidth=styles[i][1], label='(|E|=%d)' % e)

    plt.ylabel('Expected Number of of Webpages')
    plt.xlabel('|UE|')
    plt.legend(frameon=False)
    plt.axis([0, max_ue, 0, 100])
    plt.savefig(figures_dir + 'param_E.eps', bbox_inches='tight')
    plt.show()


def role_of_c():
    plt.figure(figsize=figsize)
    e = 9
    c_values = [3, 4, 5, 6, 7, 8, 9]

    for i, c in enumerate(c_values):
        ue, expected = compute_data_points(e, int(c))
        plt.plot(ue, expected, styles[i][0], linewidth=styles[i][1], label='(|C|=%d)' % c)

    plt.ylabel('Expected Number of Webpages')
    plt.xlabel('|UE|')
    plt.legend(frameon=False)
    plt.axis([0, max_ue, 0, 100])
    plt.savefig(figures_dir + 'param_C.eps', bbox_inches='tight')
    plt.show()


def role_of_f():
    plt.figure(figsize=figsize)
    max_ue = 100
    f_values = [2.,3.,4.,5.]
    d = 1
    l = 2
    k = 250
    for i, f in enumerate(f_values):
        c = d + l + f
        e = int(math.floor(k**(f / c)))
        ue, expected = compute_data_points(e, int(c))
        plt.plot(ue, expected, styles[i][0], linewidth=styles[i][1], label='(F=%d)' % f)

    plt.ylabel('Expected Number of Webpages')
    plt.xlabel('|UE|')
    plt.legend(frameon=False)
    plt.axis([0, max_ue, 0, 100])
    plt.savefig(figures_dir + 'param_F.eps', bbox_inches='tight')
    plt.show()


def role_of_l():
    plt.figure(figsize=figsize)
    l_values = [1., 2., 3.]
    d = 1
    f = 2
    k = 250
    for i, l in enumerate(l_values):
        c = d + l + f
        e = int(math.floor(k**(f / c)))
        ue, expected = compute_data_points(e, int(c))
        plt.plot(ue, expected, styles[i][0], linewidth=styles[i][1], label='(L=%d)' % l)

    plt.ylabel('Expected Number of Webpages')
    plt.xlabel('|UE|')
    plt.legend(frameon=False)
    plt.axis([0, max_ue, 0, 100])
    plt.savefig(figures_dir + 'param_L.eps', bbox_inches='tight')
    plt.show()


def role_of_d():
    plt.figure(figsize=figsize)
    d_values = [1., 2., 3.]
    l = 1
    f = 2
    k = 250
    for i, d in enumerate(d_values):
        c = d + l + f
        e = int(math.floor(k**(f / c)))
        ue, expected = compute_data_points(e, int(c))
        plt.plot(ue, expected, styles[i][0], linewidth=styles[i][1], label='(d=%d)' % d)

    plt.ylabel('Expected Number of Webpages')
    plt.xlabel('|UE|')
    plt.legend(frameon=False)
    plt.axis([0, max_ue, 0, 100])
    plt.savefig(figures_dir + 'param_D.eps', bbox_inches='tight')
    plt.show()


def role_of_k():
    pass


def compute_data_points(e, c):
    ue = np.linspace(c, max_ue, max_ue - c + 1)
    num_chosen = [x for x in range(c, e)] + [e]*(max_ue - e + 1)

    all_comb = comb(ue, num_chosen)
    good_comb = comb([x-c for x in ue], [x-c for x in num_chosen])
    expected = all_comb / good_comb

    return ue, expected

def performance_figures():
    __performance_figures(5)
    # __performance_figures(4)


def __performance_figures(clue_size):

    all_files = os.listdir(final_stats_dir_path)[1:]
    runs = []
    # run_deltas = []
    for filename in all_files:
        run_stats = load_stats(filename, final_stats_dir_path)
        print filename
        print run_stats.encoding_flow[-1]
        runs.append(run_stats)

    clues_seq = []
    for run_stats in runs:
        all_5_keywords_steps = [x for x in run_stats.encoding_flow if x[4] == clue_size]
        new_clue = [all_5_keywords_steps[0]]
        for i in range(1, len(all_5_keywords_steps)):
            if all_5_keywords_steps[i][0] == all_5_keywords_steps[i-1][0]:
                new_clue.append(all_5_keywords_steps[i])
            else:
                clues_seq.append(new_clue)
                new_clue = [all_5_keywords_steps[i]]

        clues_seq.append(new_clue)

    clues_seq_chances = []
    for clue_seq in clues_seq:
        clue_seq_chance = [float(chances(x)) for x in clue_seq]
        clues_seq_chances.append(clue_seq_chance)

    needed_iterations_per_clue = []
    num_clues = 600
    tries_per_clue = 1000
    random.seed(1609)
    for clue_i in range(num_clues):
        clue_seq_chance = random.choice(clues_seq_chances)
        needed_i = tries_per_clue
        for i in range(1, tries_per_clue):
            thresh = random.choice(clue_seq_chance)
            val = random.random()
            if val <= thresh:
                needed_i = i
                break
        needed_iterations_per_clue.append(needed_i)

    sorted_steps = sorted(needed_iterations_per_clue)
    max_steps = int(math.ceil(max(sorted_steps)))
    cdf = []
    for i in range(max_steps + 2):
        cdf.append(len([x for x in needed_iterations_per_clue if x <= i]) / float(len(needed_iterations_per_clue)))
    # for i in range(24):
    # cdf.append(len([x for x in hours if x <= i]) / float(len(hours)))

    plt.axis([0, 600, 0., 1.])
    plt.plot(cdf, '-r')
    plt.xlabel('Number of Webpages considered prior to finding feasible Webpage')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.savefig(figures_dir + 'performance_%s.eps' % clue_size, bbox_inches='tight')
    plt.show()
    print 'done'

def compression_performance():
    compression_ratios = []

    all_files = os.listdir(tweets_path)
    for tweet_file in all_files:
        raw_data_words = open(tweets_path + tweet_file).read().split()
        compression_ratios.append(5. / len(raw_data_words))

    sorted_vals = sorted(compression_ratios)
    rev_sorted_vals = list(reversed(sorted_vals))
    num_vals = float(len(rev_sorted_vals))
    unique_vals = list(reversed(sorted(list(set(sorted_vals)))))
    cdf= [(num_vals - rev_sorted_vals.index(x)) / num_vals for x in unique_vals]
    # for i, val in enumerate(sorted_vals):
    #     cdf.append(len([x for x in compression_ratios if x <= i]) / float(len(needed_iterations_per_clue)))
    # for i in range(24):
    # cdf.append(len([x for x in hours if x <= i]) / float(len(hours)))

    unique_vals.append(0)
    cdf.append(0)

    plt.axis([0, 1.1, 0., 1.])
    plt.plot(list(reversed(unique_vals)), list(reversed(cdf)), '-r')
    plt.xlabel('# of Webpages considered prior to finding feasible Webpage')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.savefig(figures_dir + 'performance_compression.eps', bbox_inches='tight')
    plt.show()
    print 'done'

if __name__ == '__main__':
    role_of_d()
    role_of_e()
    role_of_f()
    role_of_k()
    role_of_l()
    role_of_c()