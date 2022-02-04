#!/bin/bash

input="./dataset_list2.txt"
input_folder="data"
output_folder="data_cross"
song_limit=100
file_limit=100

song_count=0
file_count=0
file_err=()
title_err=()

mkdir ./$output_folder
while IFS=" " read -r title files
do 
    echo "title: $title, files: $files"
    IFS=',' read -ra FILES <<< "$files"

    if [ -d "./$input_folder/$title" ]; then
        mkdir ./$output_folder/$title
    else
        echo "$title not found."
        file_err+=("$title not found in directory.")
        continue
    fi
  
    length=${#FILES[@]}
    for (( i=0; i<length-1; i++ )); do
        ref="${FILES[i]}"
        ref_path="./$input_folder/$title/$ref.h5"

        if test -f "$ref_path"; then
            echo "Using $ref as reference."
        else
            echo "-- ERROR: reference file '$ref' not in folder."
            file_err+=("$ref from $title not found in directory.")
            break
        fi
        for (( j=i+1; j<length; j++ )); do
            query="${FILES[j]}"
            output="${FILES[i]}-${FILES[j]}.h5"
            query_path="./$input_folder/$title/$query.h5"
            output_path="./$output_folder/$title/$output.h5"
            
            if test -f "$query_path"; then
                echo "-- Using $query as query."
            else
                echo "-- ERROR: query file '$query' not in folder."
                file_err+=("$query from $title not found in directory.")
                continue
            fi

            python3 crosssimilarity.py $ref_path $query_path $output_path

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
    done

    ((song_count=song_count+1))

    echo "Done processing $title. Processed $song_count title(s)"
    if [[ $song_count -ge $song_limit ]]; then
        echo "$song_limit song limit has been reached."
        break
    fi

done < "$input"

len=${#file_err[@]}
echo "$len error(s):"
if [[ $len == 0 ]]; then
    echo "None"
fi

for file in "${file_err[@]}"; do
        echo "$file"
done

echo "Finished processing cross similarity: $song_count song(s), $file_count file(s)"