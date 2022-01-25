#!/usr/bin/env python3
import os
import sys
from tables import *
import csv
import numpy as np
#import essentia
import essentia.standard as es

def main(reference, query, output_file):
    ref_path = reference.rsplit("/",1)
    query_path = query.rsplit("/",1)
    cwd = os.getcwd()
    os.chdir(ref_path[0])
    chroma_reference = np.genfromtxt(ref_path[1], delimiter=',')  
      
    os.chdir(cwd)
    os.chdir(query_path[0])
    chroma_query = np.genfromtxt(query_path[1], delimiter=',')
    
    # Find the optimal transposition index
    reference_average = np.mean(chroma_reference,0)
    query_average = np.mean(chroma_query,0)
    euclidean_distance_shifted = np.zeros((1,12))
    for x in range(12):
        distance = np.absolute(reference_average - query_average)
        total_distance = np.sum(distance)
        euclidean_distance_shifted[0,x] = total_distance
        query_average = np.roll(query_average,1)
    opt_index = np.argmin(euclidean_distance_shifted)
    opt_index = int(opt_index)
    chroma_query = np.roll(chroma_query, opt_index,1)
    
    cross_similarity_matrix = es.CrossSimilarityMatrix()(chroma_query,chroma_reference) # original:query first
    cross_similarity_matrix = np.asarray(cross_similarity_matrix)
    cross_similarity_matrix = cross_similarity_matrix/np.max(cross_similarity_matrix)
    os.chdir(cwd)
  ###Automate Here############################################################
    with open(output_file, 'w+', newline ='') as file:    
        write = csv.writer(file)
        write.writerows(cross_similarity_matrix)
  ###########################################################################

if __name__ == "__main__":
    print(sys.argv)
    assert len(sys.argv) == 4, "Usage 'crosssimilarity.py [reference] [query] [output]"

    reference = sys.argv[1]
    query = sys.argv[2]
    filename_out = sys.argv[3]
    main(reference, query, filename_out)
