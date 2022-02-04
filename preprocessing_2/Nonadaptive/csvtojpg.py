#!/usr/bin/env python3
import numpy as np
import cv2
# import csv
import os
import sys

def main(input_file, output_file):
    input_path = input_file.rsplit("/",1)
    cwd = os.getcwd()
    os.chdir(input_path[0])
    print(input_file)
    

    csv = np.genfromtxt(input_path[1], delimiter=',')

    csv = csv*255

    image = np.zeros((180,180,3))
    image[:,:,0] = csv
    image[:,:,1] = csv
    image[:,:,2] = csv

    os.chdir(cwd)
    cv2.imwrite(output_file,image)

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Usage 'csvtojpg.py [input] [output]"

    filename = sys.argv[1]
    filename_out = sys.argv[2]
    main(filename, filename_out)