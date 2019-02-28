"""
Author:         Shraey Bhatia
Date:           October 2016
File:           unsupervised_labels.py

This file will take candidate labels and give the best labels from them using unsupervised way which is just going
to be based on letter trigram ranking. 
"""

import pandas as pd
import numpy as np
import re
from scipy.spatial.distance import cosine
from collections import defaultdict, Counter
import argparse

# The Arguments which were giben in get_labels.py file.
parser = argparse.ArgumentParser()
parser.add_argument("num_unsup_labels") # The number of unsupervised labels.
parser.add_argument("data") # The topic data file. It contains topic terms.
parser.add_argument("output_candidates") # The file which contains candidate labels.
parser.add_argument("output_unsupervised") # The file in which output is written
args = parser.parse_args()

# Get the candidate labels form candidate labels generated by cand-generation(get_labels -cg mode)
label_list =[]
with open(args.output_candidates,'r') as k:
    for line in k:
        labels = line.split()
        label_list.append(labels[1:])

# Just get the number of labels per topic.
test_chunk_size = len(label_list[0])


# Number of Unupervised labels needed should not be less than the number of candidate labels
if test_chunk_size < int(args.num_unsup_labels):
    print ("\n")
    print ("Error")
    print ("You cannot extract more labels than present in input file")
    sys.exit()

# Reading in the topic terms from the topics file.
topics = pd.read_csv(args.data)
try:
    new_frame= topics.drop('domain',1)
    topic_list = new_frame.set_index('topic_id').T.to_dict('list')
except:
    topic_list = topics.set_index('topic_id').T.to_dict('list')
print ("Data Gathered for unsupervised model")
print ("\n")

# Method to get letter trigrams for topic terms.
def get_topic_lg(elem):
    tot_list =[]
    for item in elem:
        trigrams = [item[i:i+3] for i in range(0, len(item) - 2)] 
        tot_list = tot_list + trigrams
    x = Counter(tot_list)
    total = sum(x.values(), 0.0)
    for key in x:
        x[key] /= total
    return x

"""
This method will be used to get letter trigrams for candidate labels and then rank them.
It uses cosine similarity to get a score between a letter trigram vector of label candidate and vector of
topic terms.The ranks are given based on that score. Based on this rank It will give the best 
unsupervised labels.
"""

def get_best_label(label_list,num):
    topic_ls = get_topic_lg(topic_list[num])
    val_dict = {}
    for item in label_list:
        trigrams = [item[i:i+3] for i in range(0, len(item) - 2)] #Extracting letter trigram for label
        label_cnt = Counter(trigrams)
        total = sum(label_cnt.values(), 0.0)
        for key in label_cnt:
            label_cnt[key] /= total
        tot_keys = list(set(list(topic_ls.keys()) + list(label_cnt.keys())))
        listtopic = []
        listlabel = []
        for elem in tot_keys:
            if elem in topic_ls:
                listtopic.append(topic_ls[elem])
            else:
                listtopic.append(0.0)
            if elem in label_cnt:
                listlabel.append(label_cnt[elem])
            else:
                listlabel.append(0.0)
        val = 1 - cosine(np.array(listtopic),np.array(listlabel))   # Cosine Similarity
        val_dict[item] = val
    list_sorted=sorted(val_dict.items(), key=lambda x:x[1], reverse = True) # Sorting the labels by rank
    return [i[0] for i in list_sorted[:int(args.num_unsup_labels)]]

unsup_output =[]
for j in range(0,len(topic_list)):
    unsup_output.append(get_best_label(label_list[j],j))

# printing the top unsupervised labels.
print ("Printing labels for unsupervised model")
print ("\n")
g = open(args.output_unsupervised,'w')
for i,item in enumerate(unsup_output):
    print ("top " +args.num_unsup_labels+ " labels for topic " +str(i) +" are:")
    # g.write("top " +args.num_unsup_labels+ " labels for topic " +str(i) +" are:" +"\n")
    g.write(str(i) + ",")
    for index, elem in enumerate(item):
        print (elem)
        g.write(elem)
        if index != (len(item) - 1):
            g.write(",")

    print ("\n")
    g.write("\n")
g.close()


