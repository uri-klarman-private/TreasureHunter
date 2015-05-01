import os
import pickle
import re
import datetime
from time import sleep
from gensim.models import LdaModel


__author__ = 'uriklarman'
from gensim import corpora, models

regex = re.compile("[^a-zA-Z']")

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

num_topics = 2000
num_wet_files = 5

def create_lda_model():
    print_time('about to create all docs from chunks')
    start_time = datetime.datetime.now()
    print('start time: ', start_time)
    create_all_docs()
    end_time = datetime.datetime.now()
    print('end time: ', end_time, '    total time is: ', end_time - start_time)


    print_time('about to load all docs')
    all_docs = load_all_docs()
    print_time('about to load english words')
    with open('english_full_list') as f:
        english_words = f.read().splitlines()

    good_english_words = set(english_words[75:21000])
    del english_words
    print_time('about to remove all stop-words and unknown words')
    texts = []
    for i,doc in enumerate(all_docs):
        filtered_doc = [word for word in doc if word in good_english_words]
        texts.append(filtered_doc)
        if i % 5000 == 0:
            print('Finished doc: ', i)

    print_time('about to release memory of all_docs and english_words')
    del all_docs
    del good_english_words

    print_time('about to save texts')
    with open('pickled/texts.pkl', mode='wb') as f:
        pickle.dump(texts, f)

    print_time('about to load texts')
    with open('pickled/texts.pkl', mode='rb') as f:
        texts = pickle.load(f)


    print_time('about to create dictionary')
    dictionary = corpora.Dictionary(texts)
    keys = dictionary.keys()
    print('dict size before filter: ', len(keys))
    dictionary.filter_extremes(keep_n=150000)
    dictionary.filter_extremes(no_below=750, no_above=0.1)
    keys = dictionary.keys()
    print('dict size after filter: ', len(keys))
    dictionary.save('chunks.dict')
    dictionary.save_as_text('chunks.txtdict')

    print_time('about to create corpus')
    corpus = [dictionary.doc2bow(text) for text in texts]

    print_time('about to save corpus as mm file')
    corpora.MmCorpus.serialize('corpus.mm', corpus)

    print_time('about to load dictionary file')
    dictionary = corpora.Dictionary.load('chunks.dict')

    print_time('about to load corpus as mm file')
    corpus = corpora.MmCorpus('corpus.mm')

    print_time('about to start LDA model')
    lda = LdaModel(corpus, id2word=dictionary, num_topics=num_topics)
    print_time('finished LDA model')

    print_time('about to save ldaModel')
    lda.save('pickled/LdaModel')

    print_time('about to load ldaModel')
    lda = LdaModel.load('pickled/LdaModel')

    print_time('about to find topics')
    topics = lda.show_topics(num_topics=num_topics, num_words=10000, log=True, formatted=False)

    print_time('about to save topics')
    with open('pickled/topics.pkl', mode='wb') as f:
        pickle.dump(topics, f)

def print_time(msg):
    print(datetime.datetime.now(), ': ',msg)

def create_all_docs():
    all_docs = []
    wet_files_path = './resources/wet_files'
    print(os.path.dirname(os.path.realpath(__file__)))
    chunks = [filename for filename in os.listdir(wet_files_path) if '.wet' in filename][:num_wet_files]
    print(chunks)
    for chunk in chunks:
        chunk_path = wet_files_path + '/' + chunk
        print('Starting chunk: ', chunk_path)
        all_docs += docs_from_chunk(chunk_path)

    print('Finished going over all chunks. saving...')
    with open('./resources/pickled/all_docs.pkl', mode='wb') as f:
        pickle.dump(all_docs, f)


def docs_from_chunk(chunk_path):
    with open(chunk_path) as f:
        lines = f.read().splitlines()
        indices = [i for i, x in enumerate(lines) if x == "WARC-Type: conversion"]
        docs = []
        for doc_num,i in enumerate(indices):
            start = lines.index('',i) + 1
            stop = lines.index('',start)
            docs.append(create_doc(lines[start:stop]))
            # print(datetime.datetime.now(), 'finished ', chunk_path, ' doc number: ',doc_num)


        return docs


def create_doc(doc_lines):
    doc = []
    for line in doc_lines:
        line_words = regex.sub(' ', line).lower().split()
        doc += line_words

    return doc


def load_all_docs():
    with open('pickled/all_docs.pkl', mode='rb') as f:
        all_docs = pickle.load(f)
        return all_docs

# def create_english_full_list():
#     english_full_list = []
#     s = set()
#     with open('written.num') as f:
#         for line in f:
#             word = line.split()[1].lower()
#             if word not in s:
#                 s.add(word)
#                 english_full_list.append(word)
#
#     with open('english_full_list', mode='wt', encoding='utf-8') as f:
#         f.write('\n'.join(english_full_list))
#
#     print('done')

def find_words_from_lda_model():

    with open('pickled/topics.pkl', mode='rb') as f:
        topics = pickle.load(f)
    # topics = [[tuple[1] for tuple in topic[:250]] for topic in topics]
    filtered_topics = []
    for topic in topics:
        temp_topic = [tuple for tuple in topic if tuple[0] >= 0.0001]
        filtered_topics.append(temp_topic)
    del topics

    words2docs = {}
    # dictionary = corpora.Dictionary.load('chunks.dict')
    # words = list(dictionary.values())
    # for word in words:
    #     words2docs[word] = []
    for i,topic in enumerate(filtered_topics):
        for tuple in topic:
            word = tuple[1]
            if word not in words2docs:
                words2docs[word] = []
            words2docs[word].append(i)

    unknown = 0
    good = 1
    bad =2
    topics_classification = [unknown]*num_topics

    # good_words = set([key for key in words2docs.keys() if len(words2docs[key]) < 5])
    # print('good_words size is: ', len(good_words))
    dict_word_sets = []
    for i,topic in enumerate(filtered_topics):
        if topics_classification[i] == unknown:
            good_words_in_topic = [tuple for tuple in topic if tuple[0] >= 0.01]
            # good_words_in_topic = [word for word in topic if word in good_words]
            print('len(good_words_in_topic): ', len(good_words_in_topic))
            if len(good_words_in_topic) >= 5:
                dict_word_sets.append([i,good_words_in_topic[:10]])
                topics_classification[i] = good
                for tuple in good_words_in_topic:
                    word = tuple[1]
                    for bad_topic in words2docs[word]:
                        topics_classification[bad_topic] = bad

    return dict_word_sets



if __name__ == '__main__':
    create_all_docs()
    # dict_word_sets = find_words_from_lda_model()
    # with open('pickled/dict_word_sets.pkl', mode='wb') as f:
    #     pickle.dump(dict_word_sets, f)
    # topic_dict_words = []
    # for word_set in dict_word_sets:
    #     for tuple in word_set[1]:
    #         topic_dict_words.append(tuple[1])
    # with open('pickled/topic_dict_words.pkl', mode='wt', encoding='utf-8') as f:
    #     f.write('\n'.join(topic_dict_words))
    #
    #
    # with open('pickled/topic_dict_words.pkl') as f:
    #     topic_dict_words = f.read().splitlines()
    # with open('pickled/dict_word_sets.pkl', mode='rb') as f:
    #     dict_word_sets = pickle.load(f)

    print('Done')