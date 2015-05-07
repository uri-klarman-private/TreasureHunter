from math import pow
import itertools
import random

__author__ = 'uriklarman'

SEED = 1609


def random_product(*args, **kwds):
    pools = map(tuple, args) * kwds.get('repeat', 1)
    return tuple(random.choice(pool) for pool in pools)


def create_pseudo_random_combinations(values, tuple_size, result_limit=False, avoid_all_combinations=False):
    random.seed(SEED)
    if not result_limit:
        result_limit = int(pow(len(values),tuple_size))

    if avoid_all_combinations:
        combinations = []
        combinations_set = set()
        while len(combinations_set) < result_limit:
            combo = random_product(values, repeat=tuple_size)
            if combo not in combinations_set:
                combinations.append(combo)
                combinations_set.add(combo)
        return combinations
    else:

        combinations = [x for x in itertools.product(values, repeat=tuple_size)]
        random.shuffle(combinations)
        return combinations[:result_limit]


# returns an iterable, which only allocate values when they are needed
def create_ordered_combinations(values, tuple_size):
    return itertools.product(values, repeat=tuple_size)

if __name__ == '__main__':
    a = create_pseudo_random_combinations(range(100),3,result_limit=100000,avoid_all_combinations=True)
    b = create_pseudo_random_combinations(range(100),3,result_limit=100000,avoid_all_combinations=True)
    print 'done!: ', len(a), a[:5]
    print 'done!: ', len(b), b[:5]
