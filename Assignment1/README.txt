This is the README file for A0200662U's submission
Email: e0407643@u.nus.edu

== Python Version ==

I'm using Python Version <3.9> for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

Following the ngram methods as described in the lecture, 
here are the following steps taken to create the Language Model(LM) 
up to predicting the output of unseen data:

#####
# build_LM function
1. Read input file
	Read each individual line from input file as input for building the LM.

2. Separate label and sentence(s)
	Take the first word in the each line as label and the rest of the words as sentence(s).

# update_LM function
3. Build/Update LM
	
	# preprocess function
	3.1. Pre-process string
		In hope of retaining the most useful information of the sentence(s),
		several methods of string manipulation were done, such as:
		- Retaining only alphabets characters
		- Transform multiple consecutive space(s) into one.
		- Removing leading and trailing space(s)
		- Converting all characters to lowercase
	
		The results showed little to no improvement, and its effect on the accuracy of the model 
		based on the given test file seems to vary.
		However, after considerations and testing on custom test inputs, 
		all pre-processing steps were kept as it intuitively seems to be beneficial for 
		predicting unseen data for the 3 languages in HW1 in general
		(e.g. all 3 languages seem to share the same numeric system (0-9), etc.)
	
	# ngram function
	3.2. Split sentence(s) into substrings (characters)
		Check to see if it's the start/end of the sentence.
		If yes, add start/end token accordingly ('<s>' and '</s>').
		Otherwise, split each string to substring(s) of length 4.
	
		After some testing, adding start and end token to the strings seems to slightly
		improve the accuracy of the model in some cases. 
		(Considering all characters were converted to lowercase 
		in step 3.1., this method serves to replace the use of capital letter and punctuations 
		to indicate the beginning and end of sentences)
	
	3.3. Update counts of substrings in LM
		Check to see if substring exist in the LM for the given label identified.
		If yes, then add 1 count to the substring in the LM for the given label.
		Otherwise, create a new entry for the substring.
	
	3.4. Keep track of all substrings occured in the given training data for smoothing in later step.
		Kept as a dicionary with key-value pair of 'comb' and the list of substring across all LM.

# nsmoothing function
4. N-smoothing (default n: 1)
	4.1. Identify all uniques label(s) in the LM
	4.2. Get all unique substring(s) across all label(s) in the LM
	4.3. Add n count to all substrings in each label's LM
	4.4. For every observered substring(s) in another label that doesn't exist in current label,
		Add substring with count of 1.

# prob function
5. Transform count ngrams to probability ngrams
Do the following for every label in the LM:
For every substring in the LM, divide the occurences of the substring with 
the total count of substrings in the LM for that particular label.

Overall, the LM structure used is as follow:
LM = {'comb': [sub1, sub2, ...], 'label1': {sub1: prob1, sub2: prob2, ...}, 'label2': {sub3: prob3, sub4: prob4, ...}, ...}
#####

#####
# test_LM function
1. Read input file
	Read each individual line from input file as input for the LM.

2. Create output file

# predict function
3. Calculate the probability of each line belonging to different labels in the LM 
	and take the highest probability as the output.
	
	3.1. Break down the line into substring of length 4 by applying the ngram function explained above. 
	
	# calc_prob function
	3.2 Calculate the probability of each individual line for different labels in the LM
		At the suggestion of one posting in the Piazza platform, reading through possible explanation of why it works, 
		and testing out the method itself, opt for calculating the probability by taking the sum of the probability of each substring 
		in each label instead of multiplying the probabilities directly.
		This was done to ensure that the probability tends away from 0 which is more prone to inaccuracy because of machine's precision.

	3.3. Get the label with highest probability as the predicted label
		If the probability for all label is 0, this implies that there's not enough information to make a prediction 
		using the current LM as all substrings have not been seen previously.
		Classify the line as 'other'.

4. Write the predicted label along with the line itself in the output file
######

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

1. README.txt
This file which include python ver. used for this assignment, 
overview of the code, statements of individual, and references.

2. build_test_LM.py
The code used to produce the predicted values to be evaluated against unseen data, 
achieved accuracy of 19/20 = 95% when tested with the given files.

3. ESSAY.txt
Answer to the optional questions for HW1.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[X] I, A0200662U, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0200662U, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

As the grading metrics specified.

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

Reading and writing files
- https://www.geeksforgeeks.org/read-a-file-line-by-line-in-python/
- https://stackoverflow.com/questions/9233027/unicodedecodeerror-charmap-codec-cant-decode-byte-x-in-position-y-character
- https://stackoverflow.com/questions/48959098/how-to-create-a-new-text-file-using-python

Splitting string to substrings of length 4
- https://stackoverflow.com/questions/13673060/split-string-into-strings-by-length

Working with dictionary and set
- https://www.geeksforgeeks.org/python-combine-two-dictionary-adding-values-for-common-keys/
- https://stackoverflow.com/questions/29648520/how-do-i-add-two-sets
- https://stackoverflow.com/questions/4880960/how-to-sum-all-the-values-in-a-dictionary
- https://datagy.io/python-get-dictionary-key-with-max-value/#:~:text=The%20simplest%20way%20to%20get,maximum%20value%20of%20any%20iterable.

String manipulation
- https://www.geeksforgeeks.org/python-extract-only-characters-from-given-string/
- https://stackoverflow.com/questions/1546226/is-there-a-simple-way-to-remove-multiple-spaces-in-a-string

Taking log of probability
- https://piazza.com/class/la0p9ydharl54v/post/19
- https://math.stackexchange.com/questions/892832/why-we-consider-log-likelihood-instead-of-likelihood-in-gaussian-distribution#:~:text=Taking%20the%20log%20not%20only,sum%20of%20the%20log%20probabilities.
