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

stemmer = stem.PorterStemmer()

sys.setrecursionlimit(40000)

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

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

def update_index(index, docID, tokens, eachDocId_length_for_normalisation):
    """
    Add token to index, calculate length of doc
    """

    for token in tokens:
        if(token not in index):
            # Add term to index
            plist = PostingList()
            plist.addNode(docID)
            index[token] = plist
        else:
            # Update index
            index[token].addNode(docID)
        
        # for search's docid length normalisation
        if (token not in eachDocId_length_for_normalisation):
            eachDocId_length_for_normalisation[token] = 1
        else:
            eachDocId_length_for_normalisation[token] += 1

def calculate_normalised_length(eachDocId_length_for_normalisation):
    temp = 0
    for key, value in eachDocId_length_for_normalisation.items():
        temp += (1 + math.log10(value))**2

    return math.sqrt(temp)

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    
    index = {} # dictionary with mapping of word to posting list
    N = {} # dictionary with mapping of docID to document length
    final_calculated_normalised_length = {}


    for filename in os.listdir(in_dir):
        eachDocId_length_for_normalisation = {} # e.g. now we working on doc 6, "car insurance auto insurance" --> this would give {car: 1, insurance: 2, auto: 1}
        f = os.path.join(in_dir, filename)
        file = open(f)
        text = file.read()

        docID = int(filename)            
        tokens = get_term(text)
 
        update_index(index, docID, tokens, eachDocId_length_for_normalisation)

        # calculate final_calculated_normalised_length for current docId
        final_calculated_normalised_length[docID] = calculate_normalised_length(eachDocId_length_for_normalisation)

    postlist_file = open(out_postings, 'wb')
    seek_value_count = 0

    output_dict = {} # dictionary with mapping of word to [df, pickle seek value count]

    index = OrderedDict(sorted(index.items()))
    for key, value in index.items():
        temp_item_posting_list = value
        output_dict[key] = [temp_item_posting_list.df, seek_value_count]
        pickle.dump(temp_item_posting_list, postlist_file)
        seek_value_count = postlist_file.tell()

    full_doc_ids = PostingList()
    doc_files_in_order = sorted(map(int, os.listdir(in_dir)))

    for i in range(len(doc_files_in_order)):
        full_doc_ids.addNode(doc_files_in_order[i])

    # postlist_file contains posting list dumped
    with open(out_dict, "wb") as index_file:
        pickle.dump(output_dict, index_file)
        pickle.dump(full_doc_ids, index_file)
        pickle.dump(final_calculated_normalised_length, index_file)

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
