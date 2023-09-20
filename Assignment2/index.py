#!/usr/bin/python3
import re
import shutil
import nltk
import sys
import getopt

from postlist import *

import os
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import stem
import pickle
from collections import OrderedDict

sys.setrecursionlimit(40000)


### Notes:
#sample block dictionary: {"hello:[1,2,3], "bye":[2,3,4]} --> {"bye":[2,3,4],"hello":[1,2,3]}
#sample in memory dictionary: {"hello":(docfreq, pointer to the dictionary stored on hard disk)}

### python3 index.py -i /Users/felibunbun/nltk_data/corpora/reuters/training -d dictionary-file.txt -p postings-file.txt

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

stemmer = stem.PorterStemmer()

def preprocess_text(text):
    """
    Remove punctuations from original documents
    """
    text = re.sub(r'[^\w\s]', '', text)
    return text

def get_term(text):
    """
    Pre-process text (Tokenize, Stemming, Case Holding)
    """
    text = preprocess_text(text)
    tokens = []
    sentence_tokens = sent_tokenize(text)
    for i in range(len(sentence_tokens)):
        temp = word_tokenize(sentence_tokens[i])
        for j in range(len(temp)):
            tokens.append(temp[j])

    result = []
    for token in tokens:
        term = stemmer.stem(token)
        term = term.lower()
        result.append(term)
        
    return result

def build_index(input_directory, output_file_dictionary, output_file_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    # This is an empty method
    # Pls implement your code in below
    
    ### 1. Looping through doc_files from input_directory to create block dictionary files stored under 'blockPath' directory.
    threshold_term = 15000 #50
    num_block_files_count = 0;
    os.mkdir('blockPath')
    doc_files_in_order = sorted(map(int, os.listdir(input_directory)))

    filename_count = 0
    while (filename_count < len(doc_files_in_order)):
        num_block_files_count += 1
        block_dictionary = {}
        while (len(block_dictionary) < threshold_term and filename_count < len(doc_files_in_order)):
            filename = doc_files_in_order[filename_count]
            f = os.path.join(input_directory, str(filename))
            temp_file = open(f)
            temp_text = temp_file.read()
            curr_docID = filename
            tokenized_text = get_term(temp_text)
            num_tokens = len(tokenized_text)

            for i in range (num_tokens):
                curr_token = tokenized_text[i]
                if (curr_token not in block_dictionary):
                    temp_postings = PostingList()
                    temp_postings.addNode(curr_docID)
                    block_dictionary[curr_token] = temp_postings
                else: #curr_token in dictionary    
                    block_dictionary[curr_token].addNode(curr_docID)
            
            filename_count += 1
            
        #after exiting inner while loop, one block_dictionary is done
        block_dictionary = OrderedDict(sorted(block_dictionary.items()))
            
        #open new file connection and store block_dictionary with id = num_block_files_count
        temp_block_dict = 'blockPath' + '/' + str(num_block_files_count) + '.pickle'
        with open(temp_block_dict, "ab") as f:
            for item in block_dictionary.items():
                pickle.dump(item, f)
    
    ### 2. Perform merging bit by bit: Writing the confirmed entries (known by cut_off_temp) into a pickled object in file (1 for every iteration).
    ### Each such file is stored under 'temp' directory
    #perform merging bit by bit in memory and construction of output_file_dictionary
    os.mkdir('temp')
    temp_path_file_count = 0
    temp_loaded_dict_in_memory = {}
    cut_off_temp = False
    total_num_blocks = num_block_files_count #starting from index 1
    flag_checked_at_least_one_doc = True
    tell_values = [0] * (total_num_blocks + 1) #contains tell values so we can seek in the next iteration
    while (flag_checked_at_least_one_doc):
        temp_path_file_count += 1
        flag_checked_at_least_one_doc = False
        for block_num in range (1, total_num_blocks + 1):
            curr_iter_block_path = 'blockPath' + '/' + str(block_num) + '.pickle'
            with open (curr_iter_block_path, "rb") as pickled_file:
                try:
                    start = tell_values[block_num]
                    pickled_file.seek(start)
                    for i in range(300): #3
                        temp_retrieval = pickle.load(pickled_file) #(term, posting list)
                        if (i == 0):
                            flag_checked_at_least_one_doc = True
                        temp_key = temp_retrieval[0]
                        if (i == 0 and cut_off_temp == False):
                                cut_off_temp = temp_key
                        else:
                            if (temp_key < cut_off_temp):
                                cut_off_temp = temp_key
                        temp_value_array = temp_retrieval[1]
                        if (temp_key in temp_loaded_dict_in_memory):
                            #start from the first index, if any
                            temp_loaded_dict_in_memory[temp_key] = mergeLists(temp_value_array.head, temp_loaded_dict_in_memory[temp_key].head) 
                        else: #new key in temp_loaded_dict_in_memory
                            temp_loaded_dict_in_memory[temp_key] = temp_value_array   
                    tell_values[block_num] = pickled_file.tell()
                    pickled_file.close()
                except EOFError:
                    tell_values[block_num] = pickled_file.tell()
                    pickled_file.close()
                    
        #write in-memory dictionary into hard disk until cut_off is found:
        temp_loaded_dict_in_memory = OrderedDict(sorted(temp_loaded_dict_in_memory.items()))
        temp_output_file_postings = 'temp/' + str(temp_path_file_count)
        f = open(temp_output_file_postings, "wb")
        if (cut_off_temp == False): #wont go into next iteration of while loop
            if (len(temp_loaded_dict_in_memory) > 0):
                # for item in temp_loaded_dict_in_memory.items():
                pickle.dump(temp_loaded_dict_in_memory, f)
        else:
            if (len(temp_loaded_dict_in_memory) == 0):
                #checked jic
                cut_off_temp = False
                continue
            else:
                dumping_dict = {} #created so construction of in memory dictionary will be easier, dunnid pickle.load each entry once and can dump away easier too
                for key, value in temp_loaded_dict_in_memory.items():
                    if (key == cut_off_temp): #check if curr key == cut_off_temp
                        dumping_dict[key] = value
                        break
                    else:
                        dumping_dict[key] = value
                #re-ensure dumping_dict is sorted
                dumping_dict = OrderedDict(sorted(dumping_dict.items()))
                pickle.dump(dumping_dict, f)
                last_key = list(temp_loaded_dict_in_memory.keys())[-1]
                #resetting temp_loaded_dict_in_memory for next iteration
                if (last_key == cut_off_temp):
                    #reset temp_loaded_dict_in_memory to empty
                    temp_loaded_dict_in_memory = {}
                else:
                    #keep only the terms after cut_off_temp onwards
                    for k in list(temp_loaded_dict_in_memory.keys()):
                        if (k != cut_off_temp):
                            del temp_loaded_dict_in_memory[k]
                        else: # k == cut_off_temp
                            #delete cut_off_temp now and break out of for loop
                            del temp_loaded_dict_in_memory[cut_off_temp]
                            break
                    

        f.close()
        
        #reset value for next iteration
        cut_off_temp = False
    
    ### 3. Now create the in_memory_dictionary that is eventually stored in 'output_file_dictionary'. in_memory_dict = {"term1":(docfreq1, seekvalue1), "term2":(docfreq2, seekvalue2), etc.}
    ### Simultaneously write final posting list one by one (as pickled object) into 'output_file_postings'
    
    in_memory_dictionary = {}
    
    #load (now sorted) pickled files from 'temp' directory part by part to construct in_memory_dictionary
    
    hard_disk_dictionary_path = 'temp'
    seek_value_count = 0
    ordered_hard_disk_dictionary_path_files = sorted(map(int, os.listdir(hard_disk_dictionary_path)))
    
    f = open(output_file_postings, "ab") #simultaneously write final posting list into output_file_postings entry by entry
    
    for filename in ordered_hard_disk_dictionary_path_files:
        file_path = 'temp/' + str(filename)
        with open (file_path, "rb") as pickled_file:
            try:
                temp_dict_retrieval = pickle.load(pickled_file)
                for key, value in temp_dict_retrieval.items():
                    temp_key = key
                    temp_value_array = value
                    temp_item_posting_list = value
                    temp_item_posting_list.addSkipPointer()
                    in_memory_dictionary[temp_key] = [temp_value_array.length, seek_value_count]
                    pickle.dump(temp_item_posting_list, f)
                    seek_value_count = f.tell()
            except EOFError:
                    pass

    #write in_memory_dictionary to output_file_dictionary to load into search.py
     
    full_doc_ids = PostingList()
    for i in range(len(doc_files_in_order)):
        full_doc_ids.addNode(doc_files_in_order[i])



    with open(output_file_dictionary, "wb") as f:
        pickle.dump(in_memory_dictionary, f)
        pickle.dump(full_doc_ids, f)
    

    ### 4. Before terminating, remove all temporarily created directories
    shutil.rmtree('blockPath')
    shutil.rmtree('temp')

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
