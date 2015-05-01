import cPickle as pickle

__author__ = 'uriklarman'

def save(obj, name):
    with open('resources/pickled_files/'+name+'.pkl', 'wb') as f:
        pickle.dump(obj, f)

def read(name):
    with open('resources/pickled_files/'+name+'.pkl', 'rb') as f:
        obj = pickle.load(f)
    return obj

def read_data(filename):
    list = []
    with open('resources/'+filename) as file:
        for line in enumerate(file):
            word = line.strip().lower()
            list.append(word)

    return list