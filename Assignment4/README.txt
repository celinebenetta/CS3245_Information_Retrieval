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

# Zone and Fields
1. Create a mapping of important court names to keep track of.
2. For every row (document) in the dataset, retrieve information in each field/zone (column).
3. Keep track of title, court name (after mapping), and date posted in zones_and_fields_dict.

# Content
4. Breakdown content of document to tokens with preprocess_text (keep only alphanumeric and spacecharacters) and get_term (tokenization and stemming).
5. Calculate terms, term frequency, and positional index as implemented in update_index function.
6. Get doc_vector which is a dictionary with docID as the key and terms Counter object as the value, implemented in update_docs_vector function. 
	This was stored for easier traversal during relevance feedback later in searching process.

# Compressing and output
7. To reduce file size, compress index by transforming the list objects to tuples and performing byte-encoding for positional indices.
8. Store the file with pickle library, separating the index to dictionary and postings file with dictionary storing the terms and their pointers to postings file.
9. Store other miscellaneous information such as zone and fields in dictionary.

##############

##############
search.py

1. Load index values stored in dictionary.txt and postings.txt

2. For every unique term in the query, process each word by applying tokenization and stemming as implemented in the get_tokens.

3. Calculate the query vector (tf-idf value) by using the get_query_vector_function to retrieve the tf from dictionary.txt and 
	calculating the tf-idf value with calculate_query_vector function, keeping only terms with idf > 0.1 to only consider most value adding words.

4. Expand the original query_vector to terms that exist in the given relevant documents through relevance feedback.
	Consider only words that appear across all relevant documents and keep only the top 20 most value adding terms (based on the Rocchio's formula) 
	as the query vector quickly expanded if all terms were to be considered. 
	This allows the search process to stay focused to terms within the query and limit the number of terms to search which greatly
	keep the execution time and performance in check.

5. Get document vector by retrieveng the term frequency in the document(s) which contained terms within the query vector as implemented in 
	the get_docs_vector function.
	Keep documents which contained at least one of the term in the original query to ensure relevancy in the result.

6. Calculate similarity of document(s) to query through cosine similarity score with normalisation as implemented in the get_score function.

7. Finally sort the output based on the score obtained on previous step in descending order.

##############

##############
Experiments 

1. We removed stop words from the original index as we find most of them add little values to the overall performance.
	This allows us to reduce the size of the index to 1/3 of its original size.

2. We encoded the positional index in byte encoding to save space.

3. We implemented several query refinements thought in class (more in BONUS.txt) namely, relevance feedback, 
	pseudo relevance feedback, query expansion. We also tried adding bonus scores based on zone and fields information 
	such as, adding arbitraty bonus score if the term appeared in the title or 
	if the court is said to be of importance (as stated in the 'Notes about Court Hierarchy.txt' file. 
		We opted to use only relevance feedback as we found the rest to add little to no value to (sometimes even worsen) 
		the overall performance.

4. We tried making use of the boolean operator (if any) by adding extra score to documents that contain all queries that
	contains all terms in the query. We found this to also worsen the overall performance.

5. We tried to adjust our model (mainly search.py) based on the performace of F1, precision, and recall score on the 3 sample queries given.
	We found that although sometimes it improved the scores on specific query, it didn't work against other unseen queries as
	the overall performance of the search result was worse in the leaderboard.

6. We also decided to not consider terms that are of low importance (low idf) which we found to reduce the overall execution time
	and generally improve the overall performance. Changin the cutoff value of the idf had varied result on the performance
	as setting it too high may exclude terms that may be important, but setting too low has little effect on the outcome.
		We settled for 0.1 after experimenting with values from 0.01 to 0.5 and after looking through idf values of stop words 
		which was roughly around 0.1 on average based on our index.

7. We tried pre-calculating the weight of document vector (1 + math.log10(tf)) during the indexing process,
	but as this resulted in float numbers which take up more space we decided to move the process to searching which slightly slow down
	the searching process but in favor of less space taken by the index.

8. We tried changing alpha and beta value in Rocchio's formula used in relevance feedback, but found that lower alpha value resulted in worse performance.
	We think that this was a result of putting less importance in terms that appear in the original query.
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
	Implementation of relevant documents retrieval based on queries given.
	Includes cosine similarity score, relevance feedback, and query expansion.

- dictionary.txt
	Dictionary with term(s), its document frequency and pointer to 
	the posting-file. Also store miscellaneous informations such as 
	court information, other zone and field information, document vectors.

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

Installing packages
- https://stackoverflow.com/questions/12332975/how-can-i-install-a-python-module-within-code

Dictionary, List, Other Python packages or data structures
- https://note.nkmk.me/en/python-dict-swap-key-value/
- https://stackoverflow.com/questions/19356055/summing-the-contents-of-two-collections-counter-objects
- https://www.geeksforgeeks.org/numpy-percentile-in-python/
- https://stackoverflow.com/questions/3462143/get-difference-between-two-lists-with-unique-entries
- https://stackoverflow.com/questions/6612775/how-to-make-a-copy-of-a-list-of-objects-not-change-when-modifying-the-original-l
- https://stackoverflow.com/questions/3975376/why-updating-shallow-copy-dictionary-doesnt-update-original-dictionary
- https://stackoverflow.com/questions/7323782/how-to-join-entries-in-a-set-into-one-string
- https://www.geeksforgeeks.org/convert-string-to-set-in-python/
- https://stackoverflow.com/questions/19258652/how-to-get-synonyms-from-nltk-wordnet-python

Performance Evaluation
- https://datascience.stackexchange.com/questions/36909/evaluating-metrics-f1-f2-mean-average-precision-for-object-detection

Piazza
- https://piazza.com/class/la0p9ydharl54v/post/264