from sys import getsizeof
from math import pow,ceil
import itertools

__author__ = 'uriklarman'
from numpy import median, average
import cPickle as pickle

def compute_all_combinations(tuple_size, x):
    combinations = compute_unsorted_combinations(tuple_size, x)
    sorted_list = sorted(combinations, key= lambda tuple: tuple[1])
    sorted_list_without_sum = [t[0] for t in sorted_list]
    return sorted_list_without_sum

def compute_unsorted_combinations(tuple_size, x):
    combinations = []
    count = 0
    max_number = int(ceil(pow(1000000, 1.0/tuple_size)))
    for i1 in range(max_number):
        for i2 in range(max_number):
            if tuple_size == 2:
                combinations.append(((i1,i2), i1+i2))
                count+=1
                if count >= 1000000:
                    return combinations
            elif tuple_size == 3:
                for i3 in range(max_number):
                    combinations.append(((i1,i2,i3), i1+i2+i3))
                    count+=1
                    if count >= 1000000:
                        return combinations

def create_arbitrary_sized_combinations_iterator(L, X):
    L = max(3,L)
    all_combinations = itertools.product(xrange(X),repeat=L)
    return all_combinations

def load_couples(x=10000):
        with open('resources/pickled_files/combinations_10000_keys_2.pkl', 'r') as f:
            couples = pickle.load(f)
        if x != 10000:
            couples = [c for c in couples if c[0]< x and c[1] < x]

        return couples


def load_triplets(x=10000):
    with open('resources/pickled_files/combinations_10000_keys_3.pkl', 'r') as f:
        triplets = pickle.load(f)
    if x != 10000:
        triplets = [t for t in triplets if t[0]< x and t[1] < x and t[2] < x]

    return triplets

if __name__ == '__main__':
    comb = create_arbitrary_sized_combinations_iterator(L=4,X=101)
    for i,item in enumerate(comb):
        print 'i: ', i, ' item: ', item
    print len(comb)

    print '1'
    couples = compute_all_combinations(2,10000)
    print '2'
    with open('resources/pickled_files/combinations_10000_keys_2.pkl', 'w') as f:
        pickle.dump(couples, f)
    print '3'
    triplets = compute_all_combinations(3,10000)
    print '4'
    with open('resources/pickled_files/combinations_10000_keys_3.pkl', 'w') as f:
        pickle.dump(triplets, f)
    print '5'

    couples = load_couples(10000)
    print len(couples)

    triplets = load_triplets(10000)
    print len(triplets)

    # couples_range = 10000
    # compute_all_couples(x)

    # a = (578,9002)
    # print getsizeof(a)
    # b = []
    # for i in range(1000):
    #     b.append(((i, 10000-i), 10000))
    # print getsizeof(b)
    # couples = compute_all_couples(x)
    # couples_without_avg = [x[0] for x in couples]
    # with open('resources/pickled_files/combinations_1000_keys_2.pkl', 'w') as f:
    #     pickle.dump(couples_without_avg, f)
    # print couples_without_avg[:100]
    # print len(couples_without_avg)
    # print couples[:100]
    # print len(couples)
    #
    # c2 = load_couples()
    # print c2[:100]
    # print len(c2)