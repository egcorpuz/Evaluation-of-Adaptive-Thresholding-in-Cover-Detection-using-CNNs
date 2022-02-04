import shutil
import os
#this code sorts the raw dataset to folders according to titles (middle id) in order for the bash scripts to work
#this code works for both the raw training and raw eval set
#succeeding two lines are the input and output directory folders
#note, first 4 digits is the number of the file, middle 3 digits is the number of the song, and last 2 digits is the number of the cover
input_dir = "0_evaluation_raw"
output_dir = "1_eval_sorted"
os.mkdir(output_dir)
#succeeding line should contain the appropriate text file
for line in open("dataset_kpop_eval.txt", 'r'):
    title = line.split(" ")[0]
    songs = line.split(" ")[1].split(",")
    folder = os.path.join(output_dir, title)
    os.mkdir(folder)
    for song in songs:
        song=song.strip() + ".csv"
        ipath = os.path.join(input_dir, song)
        opath = os.path.join(folder, song)
        shutil.copy2(ipath, opath)
