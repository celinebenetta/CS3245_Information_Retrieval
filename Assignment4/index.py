#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import math

import pickle
import time

from collections import OrderedDict, Counter

from nltk.tokenize import word_tokenize
from nltk import stem
from nltk.corpus import stopwords

stop_words = stopwords.words('english')

import importlib
import pip

sys.setrecursionlimit(50000)

def install_package(package):
    try:
        importlib.import_module(package)
    except ImportError:
        pip.main(['install', package])

install_package('pandas')

import pandas as pd

stemmer = stem.PorterStemmer()

def encode_varbyte(n):
    bytes_needed = math.ceil(n.bit_length() / 7)
    result = bytearray()
    for i in range(bytes_needed):
        byte = n & 0x7F
        n >>= 7
        if i != bytes_needed - 1:
            byte |= 0x80
        result.append(byte)
    return bytes(result)

def decode_varbyte(encoded):
    value = 0
    shift = 0
    for byte in encoded:
        value |= (byte & 0x7F) << shift
        if byte & 0x80 == 0:
            break
        shift += 7
    return value

def compress_index(index):
  for key, value in index.items():
    new_value = []
    for each_tuple in value:
        positional_indexes = each_tuple[2]
        counter_position = positional_indexes[0]
        encoded_array = [encode_varbyte(positional_indexes[0])]
        for i in range(1, len(positional_indexes)):
            real_position = positional_indexes[i]
            offset = real_position - counter_position
            counter_position = real_position
            encoded_array.append(encode_varbyte(offset))
        encoded_tuple = tuple(encoded_array)
        new_each_tuple = (each_tuple[0], each_tuple[1], encoded_tuple)
        new_value.append(new_each_tuple)
    new_value = tuple(new_value)
    index[key] = new_value
      
# python3 index2.py -i dataset.csv -d dictionary_file4 -p postings_file4

def usage():
    print("usage: " + sys.argv[0] + " -i dataset-file -d dictionary-file -p postings-file")

def get_term(text):
    """
    Pre-process text (Tokenize, Stemming, Case Holding)
    """
    result = []
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if not word in stop_words]
    for token in tokens:
        term = stemmer.stem(token)
        term = term.lower()
        result.append(term)
    return result

def preprocess_text(text_to_process):
    text_to_process = text_to_process.replace('\n', ' ')
    text_to_process = ''.join(char for char in text_to_process if char.isalnum() or char.isspace())
    return text_to_process

def update_index(index, docID, tokens):
    """
    Add token to index, calculate length of doc
    """

    positional_index = 1

    for token in tokens:
      init_tf = 1
      if (token not in index):
          # Add term to index
          index[token] = [[docID, init_tf, [positional_index]]]
      else:
          # Update index
          last_seen_docId = index[token][-1][0]
          if (last_seen_docId == docID): #docId already exists in posting list
            postlist = index[token][-1]
            postlist[1] += 1 # update tf
            postlist[2].append(positional_index)
          else: #docId is new in posting list
            index[token].append([docID, init_tf, [positional_index]])

      positional_index += 1

def update_doc_vector(doc_vector, docID, terms):
    if docID not in doc_vector:
        doc_vector[docID] = Counter(terms)
    else:
        doc_vector[docID] += Counter(terms)

def build_index(in_file, out_dict, out_postings):
    """
    build index from corpus given in the input file,
    then output the dictionary file and postings file
    """
    print('indexing...')
    startTime = time.time()
    
    data = pd.read_csv(in_file)
    data = data.sort_values('document_id')

    rows_left = len(data)
    
    index = {}
    doc_vector = {}

    # number of unique docIDs     
    N = len(data['document_id'].unique())
    
    ##ZONES AND FIELDS
    # note: court name processing is only 'to_lower'
    courts_most_impt = ["SG Court of Appeal", "SG Privy Council", "UK House of Lords", "UK Supreme Court",
                    "High Court of Australia", "CA Supreme Court"]

    courts_less_impt = ["SG High Court", "Singapore International Commercial Court", "HK High Court",
                    "HK Court of First Instance", "UK Crown Court", "UK Court of Appeal", "UK High Court", "Federal Court of Australia",
                    "NSW Court of Appeal", "NSW Court of Criminal Appeal", "NSW Supreme Court"] #but still more important than those not even listed
    
    #court_mappings = score of 2 if it is under courts_most_impt, score of 1 if it is under courts_less_impt, score of 0 otherwise
    zones_and_fields_dict = {} #maps docId to tuple of 1. dict of word in title to tf
                                                       #2. court name (lowercase)
                                                       #3. date posted tuple of 3 values (yyyy, mm, dd)
    court_name_to_docId_mapping = {} #maps court name to docId
    court_mapping = {} # maps name of court to a special id
    court_score_mapping = {} # maps special id to court importance score
    court_counter_for_mapping = 1
    for court in courts_most_impt:
        court = court.lower()
        court_mapping[court] = court_counter_for_mapping
        court_score_mapping[court_counter_for_mapping] = 2
        court_counter_for_mapping += 1
    for court in courts_less_impt:
        court = court.lower()
        court_mapping[court] = court_counter_for_mapping
        court_score_mapping[court_counter_for_mapping] = 1
        court_counter_for_mapping += 1
    
    for idx, row in data.iterrows():
        docID = row['document_id']
        title = row['title']
        court = row['court']
        date_posted = row['date_posted']
        extracted_date = date_posted[:10]
        
        ###court_name_to_docId_mapping
        if court in courts_less_impt or court in courts_most_impt:
            if court.lower() not in court_name_to_docId_mapping:
                court_name_to_docId_mapping[court.lower()] = [docID]
            else:
                court_name_to_docId_mapping[court.lower()].append(docID)
        ###
        
        processed_title = preprocess_text(title)
        processed_title_tokens = get_term(processed_title)
        title_array = [] #not keeping track of tf, but unique words that appear
        for word in processed_title_tokens:
            if word not in title_array:
                title_array.append(word)
        title_tuple = tuple(title_array)
        zones_and_fields_dict[docID] = (title_tuple, court.lower(), extracted_date)
 
        #preprocess text:
        text_to_process = row['content']
        text_to_process = preprocess_text(text_to_process) #processing done
        
        tokens = get_term(text_to_process)
        update_index(index, docID, tokens)
        update_doc_vector(doc_vector, docID, tokens)

        # progress checking
        rows_left -= 1
        print('finished processing docID = {}, rows left = {}'.format(docID, rows_left))

    # calculate_weight(index)

    index = OrderedDict(sorted(index.items()))
    compress_index(index)
    
    print('finished indexing')

    postlist_file = open(out_postings, 'wb')
    seek_value_count = 0

    output_dict = {} # dictionary with mapping of word to [df, pickle seek value count]

    for key, value in index.items():
        temp_item_posting_list = value
        output_dict[key] = [len(temp_item_posting_list), seek_value_count]
        pickle.dump(temp_item_posting_list, postlist_file, protocol = 4)
        seek_value_count = postlist_file.tell()

    print('finished dumping post file')

    # postlist_file contains posting list dumped
    with open(out_dict, "wb") as index_file:
        pickle.dump(output_dict, index_file, protocol = 4)
        pickle.dump(N, index_file, protocol = 4)
        pickle.dump(zones_and_fields_dict, index_file, protocol = 4)
        pickle.dump(court_mapping, index_file, protocol = 4)
        pickle.dump(court_score_mapping, index_file, protocol = 4)

    with open('docvec.txt', "wb") as docvec_file:
        pickle.dump(doc_vector, docvec_file, protocol=4)
    
    print('done')
    print ("Execution Time:" + str(time.time() - startTime) + "s")

input_file = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input file
        input_file = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_file == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_file, output_file_dictionary, output_file_postings)