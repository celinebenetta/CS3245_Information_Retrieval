#!/usr/bin/python3
import re
import nltk
import sys
import getopt

import os
from nltk.tokenize import word_tokenize
from nltk import stem
from postlist import *
import pickle
from collections import OrderedDict
import math
import heapq

stemmer = stem.PorterStemmer()

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def get_term(text):
    """
    Pre-process text (Tokenize, Stemming, Case Holding)
    """
    result = []
    tokens = word_tokenize(text)
    for token in tokens:
        term = stemmer.stem(token)
        term = term.lower()
        result.append(term)
    return result


def run_search(dictionary_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    
    with open(dictionary_file, 'rb') as f:
        in_memory_dictionary = pickle.load(f)
        full_list_docIds = pickle.load(f)
        final_calculated_normalised_length = pickle.load(f)

    N = full_list_docIds.df

    posting_list_file = open(postings_file, 'rb')

    with open(queries_file, 'r') as file:
        queries = file.readlines()

    results = open(results_file, "w")

    for query in queries:
        tokens = get_term(query)
        cosine_without_normalisation = {} # docId: second vector, where second vector is a dict {mappingid: 1 + logtf term query value}
        curr_query_term_freq = {} # maps mappingid to [term freq in entire query, df in index] (for first vector - query)
        curr_query_term_freq_mapping = {} # maps term to number, where number = mappingid

        current_counter = 0
        
        for token in tokens:
            if(token in in_memory_dictionary):
                seek_val = in_memory_dictionary[token][1]
                posting_list_file.seek(seek_val)
                posting_list = pickle.load(posting_list_file)

                if (token in curr_query_term_freq_mapping):
                    mappingid = curr_query_term_freq_mapping[token]
                    curr_query_term_freq[mappingid][0] += 1
                elif (token not in curr_query_term_freq_mapping):
                    query_term_df = posting_list.df
                    curr_query_term_freq_mapping[token] = current_counter
                    mappingid = current_counter
                    current_counter += 1
                    curr_query_term_freq[mappingid] = [1, query_term_df]
                
                    # calculation of first (query) vector in dot product(for 'cosine_without_normalisation')
                    curr = posting_list.head

                    while(curr is not None):
                        currDocId = curr.data
                        if (currDocId not in cosine_without_normalisation):
                            cosine_without_normalisation[currDocId] = {}
                        
                        cosine_without_normalisation[currDocId][mappingid] = 1 + math.log10(curr.tf)
                        curr = curr.next

        # if no matching documents, return early and continue to next query
        if (len(cosine_without_normalisation) == 0):
            results.write('\n')
            continue

        # processing curr_query_term_freq to calculate tf-idf for each unique term in query
        for key, value in curr_query_term_freq.items():
            tf = 1 + math.log10(value[0])
            idf = math.log10(N/value[1])
            tf_idf = tf * idf
            # update value of each key to tf_idf value
            curr_query_term_freq[key] = tf_idf

        # start calculating cosine similarity for each document
        normalised_query_length = 0
        for key, value in curr_query_term_freq.items():
            normalised_query_length += value**2
        normalised_query_length = math.sqrt(normalised_query_length)

        for key, value in cosine_without_normalisation.items():
            counter = 0
            for key2, value2 in value.items(): # doing dot product before normalising
                counter += curr_query_term_freq[key2] * value2 # query val * doc val for common terms between query and doc
            
            # divide by the normalising length in 'final_calculated_normalised_length' (for doc vec length)
            counter /= final_calculated_normalised_length[key] # key = docId
            
            # divide by the normalising length, normalised_query_length (for query vec length)
            counter /= normalised_query_length
            
            # take normalised counter value and replace it with value in 'cosine_without_normalisation'
            cosine_without_normalisation[key] = counter
        
        # take top k (10 most relevant (less if there are fewer than ten documents that have matching stems to the query) docIDs in response to the query))
        heap = [(-value, key) for key, value in cosine_without_normalisation.items()]
        largest = heapq.nsmallest(10, heap)
            
        query_write_output = [key for value, key in largest]

        # write to results (output file)
        results.write(str(query_write_output[0]))

        for docId in query_write_output[1:]:
            results.write(' ')
            results.write(str(docId))

        if (query != queries[-1]):
            results.write('\n')
        
    results.close()

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
