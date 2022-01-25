import os
import sys
import numpy as np
import csv
from tables import *

def main(input_file, output_file):
    input_path = input_file.rsplit("/",1)

    cwd = os.getcwd()
    os.chdir(input_path[0])

    # Load chroma from csv file into variable chroma
    print(input_file)
    chroma = np.genfromtxt(input_path[1], delimiter=',')


    # Check columns whether to apply clipping or zero-padding
    total_col = len(chroma[0])

    # Apply clipping/zero-padding and transpose rows and columns to match essentia's format
    if total_col > 180:
        chroma = np.transpose(chroma)
        chroma_180sec = chroma[0:180]
    else:
        chroma = np.transpose(chroma)
        length_zeropadding = 180 - total_col
        zero_padding = np.zeros((length_zeropadding,12)) 
        chroma_180sec = np.concatenate((chroma,zero_padding))
    
    os.chdir(cwd)
    # Writing the data into the file
    with open(output_file, 'w+', newline ='') as file:    
        write = csv.writer(file)
        write.writerows(chroma_180sec)

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Usage 'extractchromaadaptive.py [input] [output]"

    filename = sys.argv[1]
    filename_out = sys.argv[2]
    main(filename, filename_out)