#!/usr/bin/python3
import re
import nltk
import sys
import getopt

import os
import pickle
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import stem
import math
from postlist import *

# python3 search.py -d dictionary-file.txt -p postings-file.txt -q file-of-queries.txt -o output-file-of-results

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

stemmer = stem.PorterStemmer()
def get_tokens(query):
    return word_tokenize(query)

class MismatchExcept(Exception):
    pass

def shunting_yard(tokens):
    #go through once to check for 'ANDNOT' case:
    updated_tokens = []
    counter = 0
    while(counter < len(tokens)):
        if (tokens[counter] == 'AND' and tokens[counter + 1] == 'NOT'):
            updated_tokens.append('ANDNOT')
            counter += 2
        else:
            updated_tokens.append(tokens[counter])
            counter += 1
    tokens = updated_tokens
            
    precedence = {'(': 0, ')': 0, 'OR': 1, 'AND': 2, 'ANDNOT': 2, 'NOT': 3}
    output = []
    operator_stack = []

    try:    
        for token in tokens:   
            if (token == '('):
                operator_stack.append(token)
        
            elif (token == ')'):
                current_operator = operator_stack.pop()
                while (current_operator != '('):
                    if(not operator_stack):
                        raise MismatchExcept
                    output.append(current_operator)
                    current_operator = operator_stack.pop()
 
            elif (token in precedence):
                while (operator_stack and precedence[operator_stack[-1]] >= precedence[token]):
                    output.append(operator_stack.pop())              
                operator_stack.append(token)
        
            else:
                output.append(token)
 
        while (operator_stack):
            current_operator = operator_stack.pop()
            if(current_operator == '('):
                raise MismatchExcept
            output.append(current_operator)
    
        ### CHECK FOR NOT NOT consecutive tokens:
        updated_output = []
        counter = 0
        while(counter < len(output)):
            if (output[counter] == 'NOT' and output[counter + 1] == 'NOT'):
                counter += 2
                continue
            else:
                updated_output.append(output[counter])
                counter += 1
        
        return updated_output
    
    except MismatchExcept:
        print("Mismatch parantheses!")


def or_query(first, second, in_memory_dictionary, p):
    #type either list (posting list) or term    
    if (type(first) != PostingList):
        seek_value_first = in_memory_dictionary[first][1]
        p.seek(seek_value_first)
        first = pickle.load(p)
    if (type(second) != PostingList):
        seek_value_second = in_memory_dictionary[second][1]
        p.seek(seek_value_second)
        second = pickle.load(p)

    # special cases:
    if (first.head == None):
        return second
    elif (second.head == None):
        return first
    

    pointer1 = first.head
    pointer2 = second.head

    ans = PostingList()
    
    while (pointer1 is not None and pointer2 is not None):
        value1 = pointer1.data
        value2 = pointer2.data
        if (value1 < value2):
            ans.addNode(value1)
            pointer1 = pointer1.next
        elif (value2 < value1):
            ans.addNode(value2)
            pointer2 = pointer2.next
        elif (value1 == value2):
            ans.addNode(value1)
            pointer1 = pointer1.next
            pointer2 = pointer2.next
            

    if(pointer1 is None):
        while(pointer2 is not None):
            ans.addNode(pointer2.data)
            pointer2 = pointer2.next
    if(pointer2 is None):
        while(pointer1 is not None):
            ans.addNode(pointer1.data)
            pointer1 = pointer1.next
    
    return ans
        
        
def and_query(first, second, in_memory_dictionary, p):
    if (type(first) != PostingList):
        seek_value_first = in_memory_dictionary[first][1]
        p.seek(seek_value_first)
        first = pickle.load(p)
    if (type(second) != PostingList):
        seek_value_second = in_memory_dictionary[second][1]
        p.seek(seek_value_second)
        second = pickle.load(p)


    # special cases:
    if (first.head == None or second.head == None):
        return PostingList()

    pointer1 = first.head
    pointer2 = second.head
    
    ans = PostingList()

    while (pointer1 is not None and pointer2 is not None):
        value1 = pointer1.data
        value2 = pointer2.data
        if (value2 < value1):
            if (pointer2.next is not None and pointer2.next.data <= value1):
                    pointer2 = pointer2.next
                    value2 = pointer2.data
            elif (pointer2.next == None): #already at last
                break
            else:
                pointer2 = pointer2.next
                value2 = pointer2.data
                
        elif (value1 < value2):
            if (pointer1.skip is not None and pointer1.skip.data <= value2):      
                    pointer1 = pointer1.skip
                    value1 = pointer1.data
            elif (pointer1.next == None): #already at last
                break
            else:
                pointer1 = pointer1.next
                value1 = pointer1.data
        
        elif (value2 == value1):
            ans.addNode(value1)
            pointer1 = pointer1.next
            pointer2 = pointer2.next

    return ans

def andnot_query(first, second, in_memory_dictionary, p):
    if (type(first) != PostingList):
        seek_value_first = in_memory_dictionary[first][1]
        p.seek(seek_value_first)
        first = pickle.load(p)
    if (type(second) != PostingList):
        seek_value_second = in_memory_dictionary[second][1]
        p.seek(seek_value_second)
        second = pickle.load(p)
    # special cases:
    if (first.head == None):
        return PostingList()
    elif (second.head == None):
        return first
    
    ## perform and_not query:
    pointer1 = first.head
    pointer2 = second.head
    
    ans = PostingList()
    
    while (pointer1 is not None and pointer2 is not None):
        value1 = pointer1.data
        value2 = pointer2.data
        if (value1 < value2):
            ans.addNode(value1)
            pointer1 = pointer1.next
        elif (value2 == value1): #cannot be value1
            pointer2 = pointer2.next
            pointer1 = pointer1.next
        elif (value2 < value1):
            if (pointer2.next is not None and pointer2.next.data <= value1):
                    pointer2 = pointer2.skip
            else:
                pointer2 = pointer2.next
                value2 = pointer2.data
    
    while(pointer1 is not None):
        ans.addNode(pointer1.data)
        pointer1 = pointer1.next
    return ans

def not_query(only, in_memory_dictionary, p, full_list_docIds):
    if (type(only) != PostingList):
        seek_value_only = in_memory_dictionary[only][1]
        p.seek(seek_value_only)
        only = pickle.load(p)
    
    if (only.head == None):
        return full_list_docIds
    else:
        return andnot_query(full_list_docIds, only, in_memory_dictionary, p)

def preprocess_text(text):
    """
    Remove punctuations from original query
    """
    text = re.sub(r'[^\w\s]', '', text)
    return text

def get_term(text):
    """
    Pre-process text (Tokenize, Stemming, Case Holding)
    """
    result = []
    operators = ['AND', 'OR', 'NOT']
    tokens = word_tokenize(text)
    for token in tokens:
        if(token not in operators):
            term = stemmer.stem(token)
            term = term.lower()
        else:
            term = token
        result.append(term)
    return result

def process_query(query, in_memory_dictionary, postings_file, full_list_docIds):
        operators = ['OR', 'AND', 'ANDNOT', 'NOT']

        tokens = get_term(query)
        if (len(tokens) == 1):
            seek_val = in_memory_dictionary[tokens[0]][1]
            postings_file.seek(seek_val)
            ans = pickle.load(postings_file)
            return ans
        postfix_arr = shunting_yard(tokens)
        process_stack = []
        while (len(postfix_arr) > 0):
            ele = postfix_arr.pop(0)
            if ele not in operators:
                process_stack.append(ele)
            else:
                if ele == 'OR':
                    second = process_stack.pop()
                    first = process_stack.pop()
                    temp_post_list = or_query(first, second, in_memory_dictionary, postings_file)
                    process_stack.append(temp_post_list)
                elif ele == 'AND':
                    second = process_stack.pop()
                    first = process_stack.pop()
                    temp_post_list = and_query(first, second, in_memory_dictionary, postings_file)
                    process_stack.append(temp_post_list)
                elif ele == 'ANDNOT':
                    second = process_stack.pop()
                    first = process_stack.pop()
                    temp_post_list = andnot_query(first, second, in_memory_dictionary, postings_file)
                    process_stack.append(temp_post_list)
                elif ele == 'NOT':
                    only = process_stack.pop()
                    temp_post_list = not_query(only, in_memory_dictionary, postings_file, full_list_docIds)
                    process_stack.append(temp_post_list)
                else:
                    raise KeyError("something went wrong, please check again")
        
        if (len(process_stack) != 1):
            raise RuntimeError("something went wrong, len(process_stack) != 1")
        else:
            result = process_stack.pop() 
            return result

def print_docIDs(postlist):
    """
    Output docIDs that satisfy each query.
    Each docID is separated by space.
    """
    res = ''
    a = postlist.head
    while(a is not None):
        res += str(a.data) + ' '
        a = a.next
    return res.strip()
        
def run_search(dictionary_file, postings_file, file_of_queries, output_file_of_results):
    # This is an empty method
    # Pls implement your code in below
    print('running search on the queries...')
    in_memory_dictionary = {}
    with open(dictionary_file, 'rb') as f:
        in_memory_dictionary = pickle.load(f)
        full_list_docIds = pickle.load(f)

    
    file = open(file_of_queries, 'r')
    queries = file.readlines() 

    f = open(output_file_of_results, "w")
    p = open(postings_file, 'rb')
    for query in queries:
        #process and evaluation of postfix array
        result_of_query = process_query(query, in_memory_dictionary, p, full_list_docIds) #list
        if (type(result_of_query) == str):
            write_result = result_of_query
        write_result = print_docIDs(result_of_query)
        f.write(write_result)
        f.write('\n')
        
    f.close()

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
