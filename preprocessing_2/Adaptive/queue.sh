#!/bin/bash

dos2unix crosssimilarity.py crosssimilarity2.py csvtojpg.py 1covers_train.go 2noncovers_train1.go 3noncovers_train2.go 4covers_eval1.go 5covers_eval2.go 6noncovers_eval1.go 7noncovers_eval2.go
chmod +x crosssimilarity.py crosssimilarity2.py csvtojpg.py
./crosssimilarity.py
./crosssimilarity2.py
./csvtojpg.py

date=$(date '+%Y%m%d-%H:%M:%S')
log="log-$date.txt"

output=$( go run 1covers_train.go 2>&1 | tee /dev/tty )
echo "$output" > "log-1covers_train-$log"
# echo "#######################################################################################" >> $log
# echo -e "\n\n\n" >> $log
# echo "#######################################################################################" >> $log
tot_output=$(echo "$output" | tail -1)
tot_output=$(echo "1. Covers Train Set (2350): $tot_output")
clear

output=$( go run 2noncovers_train1.go 2>&1 | tee /dev/tty )
echo "$output" >> "log-2noncovers_train1-$log"
output=$(echo "$output" | tail -1)
tot_output=$(echo -e "$tot_output\n2. Noncovers Train Set (Batch 1) (32131): $output")
clear

output=$( go run 3noncovers_train2.go 2>&1 | tee /dev/tty )
echo "$output" >> "log-3noncovers_train2-$log"
output=$(echo "$output" | tail -1)
tot_output=$(echo -e "$tot_output\n3. Noncovers Train Set (Batch 2) (1209) (-r): $output")
clear

output=$( go run 4covers_eval1.go 2>&1 | tee /dev/tty )
echo "$output" >> "log-4covers_eval1-$log"
output=$(echo "$output" | tail -1)
tot_output=$(echo -e "$tot_output\n4. Covers Eval Set (Batch 1) (1650): $output")
clear

output=$( go run 5covers_eval2.go 2>&1 | tee /dev/tty )
echo "$output" >> "log-5covers_eval2-$log"
output=$(echo "$output" | tail -1)
tot_output=$(echo -e "$tot_output\n5. Covers Eval Set (Batch 2) (1650) (-r): $output")
clear

output=$( go run 6noncovers_eval1.go 2>&1 | tee /dev/tty )
echo "$output" >> "log-6noncovers_eval1-$log"
output=$(echo "$output" | tail -1)
tot_output=$(echo -e "$tot_output\n6. Noncovers Eval Set (Batch 1) (277365): $output")
clear

output=$( go run 7noncovers_eval2.go 2>&1 | tee /dev/tty )
echo "$output" >> "log-7noncovers_eval2-$log"
output=$(echo "$output" | tail -1)
tot_output=$(echo -e "$tot_output\n7. Noncovers Eval Set (Batch 2) (218835) (-r): $output")
clear

date2=$(date '+%Y%m%d-%H:%M:%S')
echo -e "Start: $date\n"
echo -e "$tot_output\n"
echo -e "End: $date2\n"
echo "Congratulations. You have reached the end of pre-processing. Above is a summary. View the the log files for in-depth review of possible runtime errors. A quick inspection of the images (files in the output folders) is necessary."
