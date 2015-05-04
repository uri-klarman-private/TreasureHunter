import cPickle as pickle

__author__ = 'uriklarman'

def save_pickle(obj, name):
    with open('resources/'+name+'.pkl', 'wb') as f:
        pickle.dump(obj, f)

def read_pickle(name):
    with open('resources/'+name+'.pkl', 'rb') as f:
        obj = pickle.load(f)
    return obj

def read_text_file(name):
    list = []
    with open('resources/'+name) as file:
        for line in enumerate(file):
            word = line.strip().lower()
            list.append(word)

    return list