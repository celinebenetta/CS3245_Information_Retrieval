import math

# Node class
class Node:
    # Function to initialize the node object
    def __init__(self, key = None):
        self.data = key
        self.tf = 1
        self.next = None
        self.skip = None
    
    # Function to view node
    def __str__(self):
        currNode = self.data
        currTF = self.tf
        nextNode = self.next.data if self.next is not None else None
        nextTF = self.next.tf if self.next is not None else None
        skipNode = self.skip.data if self.skip is not None else None
        skipTF = self.skip.tf if self.skip is not None else None
        data = [currNode, nextNode, skipNode]
        termFreq = [currTF, nextTF, skipTF]
        res = ""
        for i in range(len(data)):
            res += '(' + str(data[i]) + ', ' + str(termFreq[i]) + ')' 
            if(i < 2):
                res += ' --> '
        return res

    def __repr__(self):
        return self.__str__()
 
# Linked List class
class PostingList:
    # Function to initialize the Posting List object 
    # (based on Linked List with skip pointers)
    def __init__(self):
        self.head = None
        self.df = 0

    # Function to view list
    def __str__(self):
        data = []
        tf = []
        res = ''
        curr = self.head
        while curr is not None:
            data.append(curr.data)
            tf.append(curr.tf)
            curr = curr.next
        for i in range(len(data)):
            res += '(' + str(data[i]) + ', ' + str(tf[i]) + ')'
            if(i < len(data) - 1):
                res += ' --> '
        return res

    def __repr__(self):
        return self.__str__()

    # Add new docID
    def addNode(self, data):
        curr = self.head
        # Empty list / reach end of list, create new Node
        if curr is None:
            n = Node()
            n.data = data
            self.head = n
            self.df += 1
            return

        # input docID is smaller than current pointer, insert before current
        if curr.data > data:
            n = Node()
            n.data = data
            n.next = curr
            self.head = n
            self.df += 1
            return

        if curr.data == data:
            curr.tf += 1
            return

        # input docID is larger than current pointer, move forward
        while curr.next is not None:
            if curr.next.data == data:
                curr.next.tf += 1
                return
            if curr.next.data > data:
                break
            curr = curr.next
        n = Node()
        n.data = data
        n.next = curr.next
        curr.next = n
        self.df += 1
        return

    # Add evenly spaced pointers to posting list   
    def addSkipPointer(self):
        skip = math.floor(math.sqrt(self.df))
        n = 0
        curr = self.head
        skip_temp = curr

        while (n + skip < self.df):
            temp_skip_temp = skip_temp
            for i in range(skip): 
                temp = skip_temp.next
                skip_temp = skip_temp.next
            temp_skip_temp.skip = temp
            n += skip
        return

def mergeLists(headA, headB):
 
    res = PostingList()
    
    # A dummy node to store the result
    dummyNode = Node()
 
    # Tail stores the last node
    tail = dummyNode
    while True:
 
        # If any of the list gets completely empty
        # directly join all the elements of the other list
        if headA is None:
            tail.next = headB
            break
        if headB is None:
            tail.next = headA
            break
 
        # Compare the data of the lists and whichever is smaller is
        # appended to the last of the merged list and the head is changed
        minVal = min(headA.data, headB.data)   
        tail.next = Node(minVal)
        if (headA.data == minVal):
            headA = headA.next
        if (headB.data == minVal):
            headB = headB.next
 
        # Advance the tail
        tail = tail.next
    
    res.head = dummyNode.next
    return res

# pl (2, 5) --> (6, 2) --> (9, 2) --> (10, 1) --> (11, 1)

#pl.head (2, 5) --> (6, 2) --> (9, 2)
#pl.head.data 2
#pl.df ==> doc freq (aka length of posting list)
#pl.head.tf 5
# hi.head.next (advances to next node after head, (6,2))
# (6, 2) --> (9, 2) --> (None, None)
# hi.head.skip (go to next node that head skips to)
# (9, 2) --> (10, 1) --> (11, 1)