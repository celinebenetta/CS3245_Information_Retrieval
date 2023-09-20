This is the README file for A0200662U-A0222974Y's submission
Email(s): e0407643@u.nus.edu, e0564015@u.nus.edu

== Python Version ==

I'm (We're) using Python Version 3.8 and 3.11.1 for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

### postlist.py
An implementation of LinkedList as the data structure of choice for 
posting list of docIDs. Will be used in index.py and search.py.

Contains 2 classes and 1 function:
1. Node
	Contains 3 attributes:
	- data: current docIds
	- next: subsequent docIds
	- skip: store the skipped docIds (if any)
	
	Override __str__ method to print out the current Node attributes 
	for easier interpretation.
	- e.g., 1 -> 2 -> 4
	  Current docId is 1, followed by docId 2, and 
	  will skip to Node with docId 4 if possible

2. PostingList
	Contains 2 attributes:
	- head: the first Node of docId in posting list
	- length: total length of posting list

	Contains functions:
	- addNode
	  add the next docId to the posting list in sorted order.
	- addSkipPointer
	  at the final posting list, calculate the length of skip pointer
	  and add skip pointer to the node(s) if possible.

3. mergeLists
   Function to merge 2 posting lists and return a sorted 
   combination of the 2 posting lists.

### index.py
1. Loop through files from the input directory to create block dictionary files stored under 'blockPath' directory. Each block dictionary has a maximum size of threshold_term which is defined to be 15000.

2. Perform merging bit by bit, and write the confirmed entries, which are all entries all the way till the term denoted as cut_off_temp (alphabetically minimum term that was written from each block at every iteration) into a pickled object in file (1 for every iteration). 

Each such file is stored under 'temp' directory.

Now, each file in the 'temp' directory, would be in alphabetical order and also according to the numerical order of file name, and also according to numerical order of the file name.

3. Now create the in_memory_dictionary that is eventually stored in 'output_file_dictionary'. An example of in memory dict would be: in_memory_dict = {"term1":(docfreq1, seekvalue1), "term2":(docfreq2, seekvalue2), etc.}
Simultaneously write final posting list one by one (as pickled object) into 'output_file_postings'

4. Before terminating, remove all temporarily created directories, in this case 'blockPath' and 'temp'

### search.py

# run_search function
1. Load dictionary file and full list of docIds obtained from index.py

2. Open posting file. NOT to be loaded until relevant term requires so.

3. Load files of queries line by line

4. For every query,
   
   4.1. Tokenize terms in query that is NOT operators.
	  # preprocess function
  	  Same as index.py. 
  	  Remove punctutations from terms in query.

	  # get_term function
  	  Similar as index.py. 
  	  Tokenize, stem, and case hold terms in query.
   
   4.2. Output postfix form of query through shunting yard algorithm.
        #shunting_yard function
	  To ensure query is processed appropriately, we had followed the 
	  shunting yard algorithm to generate postfix list of each query.
	  
	  Go through the query tokens once to identify AND NOT query.  
	  Sorted the query based on the order of operations' precedence 
	  ( () > NOT > AND == ANDNOT > OR ).
	  e.g., query 'a AND b OR NOT c' (without quotations) will be 
		  returned as ['a', 'b', 'AND', 'c', 'NOT', 'OR'].
		
	  Check for invalide query such as:
	  - consecutive NOT NOT	  
	  - Enforce # MismatchException class
  	    Handle error raised when query contains mismatch parantheses.
	    e.g., a AND (b OR c AND (e or d)

   4.3. Process postfix obtained form previous step.

	  4.3.1. Read through the values in postfix list until an operator is found.
		   Store terms in a temporary list called process_stack.
        
	  4.3.2. Once an operator is found,
		   
		   4.3.2.1. If the operator is AND, 
				
				4.3.2.2.1. Pop stack to get the most recent 2 terms to handle with current operator.
				
				4.3.2.2.2. Run and_query function
						# and_query function
						Function created to handle a AND b query.
						- Check if any of the 2 terms is of type string.
				  			If yes, this implies that no processing has been done yet to 
							the particular term(s).
				  			Obtained the posting list of the term(s) accordingly to be handled.
						- Go through the 2 posting lists.
				  			- If, current docID in the 2 posting lists are equal add to result.
				 	 		- Else, move to the next docId in the posting list, 
								skip if current docIDs has skip pointer.
						- Return posting list result, append to stack.
				
		   4.3.2.2. If the operator is ANDNOT,

				4.3.2.2.1. Pop stack to get the most recent 2 terms to handle with current operator.
				
				4.3.2.2.2. Run andnot_query function
						# andnot_query function
						Function created to handle a AND NOT b query.
						- Check if any of the 2 terms is of type string.
				  			If yes, this implies that no processing has been done yet to 
							the particular term(s).
				  			Obtained the posting list of the term(s) accordingly to be handled.
						- Handle special case where one of the list is empty. Otherwise,
						- Go through the 2 posting lists until the end of one of the list. 
						  Since the posting lists are sorted, we can follow the steps explained in lecture:
				  			- If, current docID in the 2 posting lists are equal, move to the next docId on both list.
				 	 		- Else if, docId a < docId b, add docId to result.
							- Else if, docId a > docId b, move to the next docId in b's posting list, 
									skip if current docIDs has skip pointer.
						- Return posting list result, append to stack.
		
			4.3.2.3. If the operator is OR, 
				
				4.3.2.2.1. Pop stack to get the most recent 2 terms to handle with current operator.
				
				4.3.2.2.2. Run or_query function
						# or_query function
						Function created to handle a OR b query.
						- Check if any of the 2 terms is of type string.
				  			If yes, this implies that no processing has been done yet to 
							the particular term(s).
				  			Obtained the posting list of the term(s) accordingly to be handled.
						- Go through the 2 posting lists.
				  			- If, current docID in the 2 posting lists are equal add to result.
				 	 		- Else, move to the next docId in the posting list, 
								skip if current docIDs has skip pointer.
						- Return posting list result, append to stack.

			4.3.2.4. If the operator is NOT
				Run not_query function
				# not_query function
				Return the NOT term of the first term in the stack,
				Otherwise if the term's posting list is empty, return post list of all docIds,
					    else, make use of the andnot_query as a helper function with parameters post list of all docIds and the term's posting list.
		   
				
	   4.3.3. At the end of trasversing the postfix list, return the final post list in the stack.
    
    4.4 Enforce invalid query checking such as:
	  - empty query

    # print_docID function
    4.5. Combine the docIDs result of current query separated by space.

5. Write the result in output file line by line per query

Experimentation:
- We decided to use only word_tokenize as the function already calls for sent_tokenize.
- We opted to remove all punctuations as there were some issues with stemming and tokenization with punctutions, 
  and since a stand-alone punctuations are unlikely to be a term to be searched for
- We tried to keep punctuations in between letters or numbers using regex, but decided against it since we're not sure 
  how it would affect the accuracy of the index.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

- postlist.py
	Implementation of LinkedList with skip pointers as the data 
	structure of choice for posting list.

- index.py
	Implementation of SPIMI with n-way merge to build index.

- search.py
	Implementation of Shunting Yard Algorithm to handle boolean query 
	and posting list merging.

- dictionary-file
	Dictionary with term(s), its document frequency and pointer to 
	the posting-file.

- postings-file
	Posting lists of terms in dictionary-file.

- README.txt
	This file which include python ver. used for this assignment, 
	overview of the code, statements of individual, and references.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[X] I/We, A0200662U-A0222974Y, certify that I/we have followed the CS 3245 Information
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

File/Folder Iteration or Handling (pickle and os library)
- https://www.geeksforgeeks.org/how-to-iterate-over-files-in-directory-using-python/
- https://pythonexamples.org/python-pickle-class-object/
- https://www.geeksforgeeks.org/create-a-directory-in-python/
- https://www.geeksforgeeks.org/python-check-if-a-file-or-directory-exists-2/
- https://stackoverflow.com/questions/13118029/deleting-folders-in-python-recursively
- https://stackoverflow.com/questions/49284015/how-to-check-if-folder-is-empty-with-python
- https://stackoverflow.com/questions/31613409/how-to-select-the-first-file-in-a-directory
- https://www.geeksforgeeks.org/delete-a-directory-or-file-using-python/
- https://stackoverflow.com/questions/10873777/in-python-how-can-i-check-if-a-filename-ends-in-html-or-files
- https://www.geeksforgeeks.org/python-move-all-files-from-subfolders-to-main-folder/
- https://stackoverflow.com/questions/17547273/flatten-complex-directory-structure-in-python
- https://www.geeksforgeeks.org/how-to-search-a-pickle-file-in-python/https://stackoverflow.com/questions/20716812/saving-and-loading-multiple-objects-in-pickle-file
- https://stackoverflow.com/questions/57127767/peek-of-a-closed-file-right-after-file-is-opened
- https://www.geeksforgeeks.org/python-tell-function/
- https://stackoverflow.com/questions/55809976/seek-on-pickled-data

Tokenization
- https://www.nltk.org/api/nltk.tokenize.html
- https://www.nltk.org/_modules/nltk/stem/porter.html
- https://piazza.com/class/la0p9ydharl54v/post/116

Shunting Yard Algorithm
- https://en.wikipedia.org/wiki/Shunting_yard_algorithm
- https://stackoverflow.com/questions/8344460/trouble-understanding-what-to-do-with-output-of-shunting-yard-algorithm

Handling Exception
- https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python

Data Structure (LinkedList implementation for PostingList and Dictionary)
- https://www.geeksforgeeks.org/python-sort-python-dictionaries-by-key-or-value/
- https://www.geeksforgeeks.org/merge-two-sorted-linked-lists/
- https://www.w3schools.com/python/python_dictionaries_loop.asp

String Manipulation
- https://www.digitalocean.com/community/tutorials/python-concatenate-string-and-int
- https://www.geeksforgeeks.org/python-remove-punctuation-from-string/

Checking Boolean Query Logic
- https://piazza.com/class/la0p9ydharl54v/post/99

Recursion Depth Error
- https://piazza.com/class/la0p9ydharl54v/post/120
- https://stackoverflow.com/questions/3323001/what-is-the-maximum-recursion-depth-in-python-and-how-to-increase-it
