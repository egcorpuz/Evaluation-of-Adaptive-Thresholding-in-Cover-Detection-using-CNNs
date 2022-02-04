#!/bin/bash

input="./dataset_kpop_eval.txt" #or ./dataset_kpop_eval.txt
song_count=0
file_count=0
file_err=()
title_err=()

mkdir ./3_eval_adaptive #output directory. all occurences must be changed accrdngly
while IFS=" " read -r title files
do 
    echo "title: $title, files: $files"
    IFS=',' read -ra FILES <<< "$files"

    if [ -d "./2_eval_clipped/$title" ]; then
        mkdir ./3_eval_adaptive/$title
    else
        echo "$title not found."
        file_err+=("$title not found in directory.")
        break
    fi
  
    for file in "${FILES[@]}"; do
        input_path="./2_eval_clipped/$title/$file.csv" #input directory. all occurences must be changed accrdgnly
        output_path="./3_eval_adaptive/$title/$file.csv"
    
        if test -f "$input_path"; then
            echo "Applying adaptive thresholding to $file.csv"
            
            python3 adaptive.py $input_path $output_path
        else
            echo "-- ERROR: file not in folder."
            file_err+=("$file from $title not found in directory.")
            continue
        fi

        if test -f "$output_path"; then
            echo "-- $file.csv applied with adaptive thresholding successfully"            
            ((file_count=file_count+1))
        else
            file_err+=("$file from $title error applying adaptive thresholding.")
        fi
    done
    ((song_count=song_count+1))

    echo "Done applying adaptive thresholding to $title. $song_count titles have been applied with adaptive thresholding."
    if [[ $song_count == $limit ]]; then
        break
    fi

done < "$input"

len=${#file_err[@]}
echo "$len errors:"
if [[ $len == 0 ]]; then
    echo "None"
fi

for file in "${file_err[@]}"; do
        echo "$file"
done

echo "Finished application of adaptive thresholding: $song_count songs, $file_count files"