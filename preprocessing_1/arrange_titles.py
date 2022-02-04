file = open('files.txt', 'r')
output = open('dataset_kpop_train.txt', 'w')
titles = file.readline().split(' ')
#lists and arranges the songs according to their title (middle id number)
#file names must be manually copied to a text file first using terminal
#output file is a new dataset_list txt file that can be used by the bash script codes
#this code can be used for both the raw training set and the raw evaluation set
songs = []
file_ctr = 0
count = 1
for title in titles:
    file_ctr+=1
    title = title.strip()
    parts = title.split('_')
    print(parts)
    if int(parts[1]) == count:
        songs.append(title.rstrip(".csv"))
    else:
        str_songs = ','.join(songs)
        str_title = f'{count:03d}'
        output.write(str_title + ' ' + str_songs + '\n')
        count=int(parts[1])
        songs=[]
        songs.append(title.rstrip(".csv"))

str_songs = ','.join(songs)
str_title = f'{count:03d}'
output.write(str_title + ' ' + str_songs + '\n')

print(str(file_ctr) + " files")