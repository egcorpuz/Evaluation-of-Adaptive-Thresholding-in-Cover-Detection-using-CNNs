#!/bin/bash

input="./dataset_list2.txt"
input_folder="data"
output_folder="data_cross_noncover"
song_limit=100
file_limit=100

song_count=0
file_count=0
file_err=()
title_err=()

mkdir ./$output_folder &> /dev/null
input_folders=($input_folder/*/)
length=${#input_folders[@]}
for (( i=0; i<length-1; i++ )); do 
    for (( j=i+1; j<length; j++ )); do
        ref_folder=${input_folders[i]}
        query_folder=${input_folders[j]}

        if [[ $ref_folder == $query_folder ]]; then
            continue
        fi

        # Get folder name from complete path
        IFS='/'
        read -a ref_path <<< $ref_folder
        read -a query_path <<< $query_folder
        
        len=${#ref_path[@]}-1
        ref_title=${ref_path[len]}

        len=${#query_path[@]}-1
        query_title=${query_path[len]} 
        echo "Reference title: $ref_title, Query title: $query_title"

        mkdir ./$output_folder/$ref_title &> /dev/null
        
        output="$ref_title-$query_title.h5"
        output_path="./$output_folder/$ref_title/$output"
        echo "-- Output path: $output_path"

        # Get files inside folder and get the first file from the array
        # to use in cross similarity
        ref_files=("$ref_folder"*)
        ref_file=${ref_files[0]}
        query_files=("$query_folder"*)
        query_file=${query_files[0]}

        echo "-- Reference file: $ref_file, query file: $query_file"  
        python3 crosssimilarity.py $ref_file $query_file $output_path

        if test -f "$output_path"; then
            echo "-- $output cross similarity executed successfully"            
            ((file_count=file_count+1))
        else
            file_err+=("$file from $title error executing cross similarity.")
        fi

        if [[ $file_count -ge $file_limit ]]; then
            echo "$file_limit file limit has been reached."
            break 3
        fi
    done

    ((song_count=song_count+1))

    echo "Done processing $ref_title. Processed $song_count title(s)"
    if [[ $song_count -ge $song_limit ]]; then
        echo "$song_limit song limit has been reached."
        break
    fi

done

len=${#file_err[@]}
echo "$len error(s):"
if [[ $len == 0 ]]; then
    echo "None"
fi

for file in "${file_err[@]}"; do
    echo "$file"
done

echo "Finished processing cross similarity: $song_count song(s), $file_count file(s)"