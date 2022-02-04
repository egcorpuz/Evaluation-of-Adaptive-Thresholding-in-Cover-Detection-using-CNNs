import os
import sys
import numpy as np
import statistics
import csv
from tables import *

def main(input_file, output_file):
    input_path = input_file.rsplit("/",1)

    cwd = os.getcwd()
    os.chdir(input_path[0])
    # Load chroma from csv file into variable chroma
    print(input_file)
    chroma = np.genfromtxt(input_path[1], delimiter=',')

    # Check array dimensions
    total_row = len(chroma)
    total_col = len(chroma[0])

    # Initialize array for chroma with adaptive thresholding applied
    adaptivechroma = np.zeros((total_row,total_col))

    # Window for adaptive thresholding is 12 Frequency bins x 15 time frames 
    # Note: Initially 35 frequency bins but the chroma is limited to 12 bins
    time_window = 15

    # Initialize temp array to store values of each window
    temp_array = np.zeros((time_window,total_col))

    row = 0
    window_edge = 0

    # Apply adaptive thresholding to the chroma
    while row < total_row:
        col = 0
        
        # Check if current row is a new window. If new window, recalculate local median.
        if row == window_edge:
            temp_row = row
            window_edge = temp_row + time_window
            # Load current window into temp array
            while temp_row < window_edge and window_edge < total_row:
                temp_col = 0
                while temp_col < total_col:
                    temp_array[temp_row - row][temp_col] = chroma[temp_row][temp_col]
                    temp_col += 1
                temp_row += 1
            # Turn temp array to a 1d array and calculate the median for the window
            flat_temparray = temp_array.flatten()
            localmedian = statistics.median(flat_temparray)
        
        # Set value of array element to 1 if value is greater than the threshold (local median)
        while col < total_col:
            if chroma[row][col] >= localmedian:
                adaptivechroma[row][col] = 1
            else:
                adaptivechroma[row][col] = 0    
            col += 1
        row += 1

    os.chdir(cwd)    
    # Writing the data into the file
    with open(output_file, 'w+', newline ='') as file:    
        write = csv.writer(file)
        write.writerows(adaptivechroma)

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Usage 'adaptive.py [input] [output]"

    filename = sys.argv[1]
    filename_out = sys.argv[2]
    main(filename, filename_out)
