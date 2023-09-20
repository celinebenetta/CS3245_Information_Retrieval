This is the README file for A0200662U-A0222974Y's submission
Email(s): e0407643@u.nus.edu, e0564015@u.nus.edu

== Python Version ==

I'm (We're) using Python Version 3.8 and 3.11.1 for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

############# 
postlist.py

An implementation of LinkedList as the data structure of choice for 
posting list of docIDs. Will be used in index.py and search.py.

Contains 2 classes and 1 function:
1. Node
	Attributes used:
	- data: current docIds
	- tf: termFreq
	- next: subsequent docId
	
	Override __str__ method to print out the current Node attributes 
	for easier interpretation.
	- e.g., (1, 1) -> (2, 1)
	  Current docId is 1 with termFreq 1, followed by 
	  docId 2 with termFreq 1, and so on.

2. PostingList
	Contains 2 attributes:
	- head: the first Node of docId in posting list
	- df: number of document containing the term or length of posting list

	Used functions:
	- addNode
	  add the next docId to the posting list in sorted order. 
	  If docID exist add the termFreq.

##############

##############
index.py

# build_index function

1. Iterate through all files in corpus
   Initialized index (to be split into dictionary and posting) and 
   final_calculated_normalised_length (length of each document vector)
   
   # get_term function
   1.1. For each document, split text into tokens
   
   # update_index function
   1.2. Update index
	  For each token not in index create a new posting list with docID,
	  otherwise, add docID to the posting list.
	
	  Subsequently update length of document in final_calculated_normalised_length

   # calculate_normalised_length function
   1.3. Calculate final_calculated_normalised length with 
	  formula of (1 + log10(termFreq))^2
   
   1.4. Output all files into dictionary.txt and postings.txt
	  # output_dict
	  Create dictionary to store document frequenct and pointer to postings.txt  
	
	  # postings.txt
	    Dump posting list one by one to be access with python seek() 
	    function in search.py  
	
	  # full_doc_ids
	    Keep track of number of documents in corpus.

	  # dictionary.txt
	    Dump output_dict, full_doc_ids, and final calculated_normalised length.

##############

##############
search.py

For each query, we initialise 3 dictionaries:
1. "cosine_without_normalisation"
--> maps docId to a dictionary containing mappings of 'mappingid' to (1 + logtf) value. Each unique term in the query can be uniquely identified by their 'mapping' as explained in the 3rd dictionary below.

2. "curr_query_term_freq"
--> maps mapping to a list of 2 elements, [term freq of this unique term in the entire query, df for this unique term in entire index]

3. "curr_query_term_freq_mapping"
--> maps each unique term as seen in "curr_query_term_freq" to a number, where number = mappingid. mappingid is also used in "cosine_without_normalisation" (1st dictionary)

We only calculate the weights of terms that are common between query and in each document. For term in document weights, this is stored in "cosine_without_normalisation[currDocId][mappingid]" on line 87.

Next, in line 96, we calculate the tf-idf weight for each unique term in query. 

Then we proceed on to take the dot product of the 2 vectors (term weight with regards to query and document) and do so for each relevant document. 

After normalisation, we store the final cosine similarity score under the 'cosine_without_normalisation' dictionary with docId as the key.

At line 124, we heapify the dictionary into a min heap such that we can return the top k most relevant documents, where k = min(10, number of relevant documents available in 'cosine_without_normalisation')

##############

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

- postlist.py
	Implementation of LinkedList with docID and termFreq as values inside
	each node.

- index.py
	Implementation of indexing into dictionary, posting, 
	and document length files.

- search.py
	Implementation of cosine similarity score.

- dictionary.txt
	Dictionary with term(s), its document frequency and pointer to 
	the posting-file.

- postings.txt
	Posting lists of terms in dictionary.txt.

- README.txt
	This file which include python ver. used for this assignment, 
	overview of the code, statements of individual, and references.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[X] I/We, A0000000X, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

Document Length
- https://piazza.com/class/la0p9ydharl54v/post/196

Weight (wtd and wtq)
- https://piazza.com/class/la0p9ydharl54v/post/194

Queries checking
- https://piazza.com/class/la0p9ydharl54v/post/200

Heap library
- https://piazza.com/class/la0p9ydharl54v/post/217
