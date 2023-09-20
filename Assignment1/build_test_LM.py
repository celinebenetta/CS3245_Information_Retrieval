#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import nltk
import sys
import getopt

import math
from collections import Counter

def preprocess(string):
    """
    Preprocess strings to remove characters that may not 
    particularly be useful in predicting the label.
    Transform all letters to lowercase.
    """
    # Retain only alphabets characters
    string = "".join(re.split("[^a-zA-Z ]*", string))
    # Remove extra spaces
    string = re.sub(' +', ' ', string)
    # Remove leading and trailing spaces
    string = string.strip()
    # Convert to lowercase
    string = string.lower()

    return string

def ngram(line, n = 4):
    """
    Split string into ngrams (characters).
    Add start and end token.
    """
    chunks, chunk_size = len(line), n
    res = {}
    for i in range(chunks):
        # Check if substring is the start of the input line
        if(res == {}):
            
            sub = '<s>' + line[i:i+chunk_size-1]
            if (sub not in res):
                res[sub] = 1
            else:
                res[sub] += 1
        else:
            sub = line[i:i+chunk_size]
            if(len(sub) < n - 1):
                break
            if len(sub) == n - 1:
                sub = sub + '</s>'
            if (sub not in res):
                res[sub] = 1
            else:
                res[sub] += 1 
    return res

def update_LM(LM, label, string):
    """
    Identify label(s) within LM. 
    If it doesn't exist, make a new LM for the label.
    Otherwise, update count of ngrams in LM.
    """
    # Preprocess string
    string = preprocess(string)

    # Update label's LM
    res = ngram(string)
    if(label not in LM):
        LM[label] = res
    else:
        LM[label] = dict(Counter(LM[label]) + Counter(res))
    
    # Keep track of all ngram
    for n in list(res):
        if(n not in LM['comb']):
            LM['comb'].append(n)
        else:
            continue
    
    return LM

def nsmoothing(LM, n = 1):
    """
    Combine all observed ngram from other labels' LM.
    Add n-smoothing.
    """
    # Get all labels
    labels = list(LM)
    labels.remove('comb')
    
    # Get all ngrams observed
    comb = set(LM['comb'])

    for label in labels:
        # Add n-smoothing
        for value in LM[label]:
            LM[label][value] += n

        # Add observed ngrams from other labels' LM
        additions = comb - set(LM[label])
        for addition in additions:
            LM[label][addition] = 1

def prob(LM):
    """
    Transform count to probabilities ngram.
    """
    # Get all labels
    labels = list(LM)
    labels.remove('comb')

    for label in labels:
        total = sum(LM[label].values())
        for value in LM[label]:
            LM[label][value] /= total

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print("building language models...")
    
    # Open in_file
    file = open(in_file, encoding='utf8')
    lines = file.readlines()

    # Base LM
    LM = {'comb':[]}
    for line in lines:
        # Split label and string
        msg = line.split(' ', 1)
        label, string = msg[0], msg[1]

        # Add info from new sentence to LM
        update_LM(LM, label, string)

    # Add 1-Smoothing
    nsmoothing(LM)

    # Probability N-gram
    prob(LM)

    return LM

def calc_prob(LM, label, ngrams):
    """
    Calculate the probability of input line 
    for different labels.
    """
    prob = 0
    for n_gram in ngrams:
        if(n_gram in LM[label]):
            prob += math.log(LM[label][n_gram])
    return prob

def predict(LM, line, res):
    """
    Choose the most likely label the input line(s) belong to.
    """
    ngrams = ngram(line)
    
    # Get all labels
    labels = list(LM)
    labels.remove('comb')

    for label in labels:
        res[label] = calc_prob(LM, label, ngrams)
    
    output = max(res, key=res.get)
    if(res[output] == 0):
        output = 'other'

    return output

def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")

    # Open in_file
    file = open(in_file, encoding='utf8')
    lines = file.readlines()

    # Create out_file
    out = open(out_file, 'w')

    # Create prediction (label) and write the result in out_file
    res = {}
    for line in lines:
        out.write(predict(LM, line, res) + " " + line)
    
    # Close out_file
    out.close()
    
def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"
    )


input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], "b:t:o:")
except getopt.GetoptError:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == "-b":
        input_file_b = a
    elif o == "-t":
        input_file_t = a
    elif o == "-o":
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
