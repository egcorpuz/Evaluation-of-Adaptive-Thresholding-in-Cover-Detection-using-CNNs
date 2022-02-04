#!/bin/bash

input="./dataset_kpop_eval.txt" #or ./dataset_kpop_eval.txt
song_count=0
file_count=0
file_err=()
title_err=()

mkdir ./2_eval_clipped #output directory. all occurences must be changed accrdngly
while IFS=" " read -r title files
do 
    echo "title: $title, files: $files"
    IFS=',' read -ra FILES <<< "$files"

    if [ -d "./1_eval_sorted/$title" ]; then
        mkdir ./2_eval_clipped/$title
    else
        echo "$title not found."
        file_err+=("$title not found in directory.")
        break
    fi
  
    for file in "${FILES[@]}"; do
        input_path="./1_eval_sorted/$title/$file.csv" #input directory. all occurences must be changed accrdgnly
        output_path="./2_eval_clipped/$title/$file.csv"
    
        if test -f "$input_path"; then
            echo "Clipping $file.csv"
            
            python3 audioclip.py $input_path $output_path
        else
            echo "-- ERROR: file not in folder."
            file_err+=("$file from $title not found in directory.")
            continue
        fi

        if test -f "$output_path"; then
            echo "-- $file.csv clipped successfully"            
            ((file_count=file_count+1))
        else
            file_err+=("$file from $title error clipping.")
        fi
    done
    ((song_count=song_count+1))

    echo "Done clipping $title. $song_count titles have been clipped"
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

echo "Finished clipping: $song_count songs, $file_count files"