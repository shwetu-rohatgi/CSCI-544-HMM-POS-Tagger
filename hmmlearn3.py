import sys
import json
import os
import glob

model_file="hmmmodel.txt"
output_file="hmmoutput.txt"

train_files = sys.argv[1]

fp = open(train_files, encoding = 'UTF-8')

words_in_line = [line.rstrip('\n').split() for line in fp]

#print(words_in_line)
tag_counts = {}
tag_word = {}
most_prob_tag_word = {}

tag_counts['start'] = len(words_in_line)
tag_counts['end'] = len(words_in_line)

for line_list in words_in_line:
    for word_tag in line_list:
        intermediate = word_tag.split('/')
        tag = intermediate[-1]
        word = intermediate[:-1]
        if tag not in most_prob_tag_word:
            most_prob_tag_word[tag] = []
        if word[0] not in most_prob_tag_word[tag]:
            most_prob_tag_word[tag].append(word[0])
        word = '/'.join(word)
        if tag not in tag_counts:
            tag_counts[tag] = 1
        else:
            tag_counts[tag]+=1
        if tag not in tag_word:
            tag_word[tag] = {}
        if word not in tag_word[tag]:
            tag_word[tag][word] = 1
        else:
            tag_word[tag][word]+=1
            
most_prob_tag_word = sorted(most_prob_tag_word, key=lambda k: len(most_prob_tag_word[k]), reverse=True)
send_tags = most_prob_tag_word[0:5]
            
#print(tag_word)
#print(tag_counts)
fhandle = open('hmmmodel.txt', 'w')

emission_prob = {}
for tag in tag_word:
    for word in tag_word[tag]:
        if word not in emission_prob:
            emission_prob[word] = {}
        if tag not in emission_prob[word]:
            emission_prob[word][tag] = tag_word[tag][word]/tag_counts[tag]
            
previous_tags = {}
for tags in tag_counts:
    previous_tags[tags] = {}
    
for line in words_in_line:
    for i in range(len(line)+1):
        if i==0:
            if 'start' not in previous_tags[line[i].split('/')[-1]]: 
                previous_tags[line[i].split('/')[-1]]['start'] = 1
            else:
                previous_tags[line[i].split('/')[-1]]['start'] += 1
        elif i==len(line):
            if line[i-1].split('/')[-1] not in previous_tags['end']:
                previous_tags['end'][line[i-1].split('/')[-1]] = 1
            else:
                previous_tags['end'][line[i-1].split('/')[-1]] += 1                
        else:
            if line[i-1].split('/')[-1] not in previous_tags[line[i].split('/')[-1]]:
                previous_tags[line[i].split('/')[-1]][line[i-1].split('/')[-1]] = 1
            else:
                previous_tags[line[i].split('/')[-1]][line[i-1].split('/')[-1]] += 1
        

transition_prob = previous_tags
#fhandle.write(json.dumps(transition_prob, indent=2))

for cur_tag in transition_prob:
    for prev_tag in tag_counts:
        if prev_tag == 'end':
            continue
        #adding add one smoothing
        elif prev_tag not in transition_prob[cur_tag]:
            transition_prob[cur_tag][prev_tag] = 1/(tag_counts[prev_tag]+(4*len(tag_counts))-1)
        else:
            transition_prob[cur_tag][prev_tag] = (transition_prob[cur_tag][prev_tag]+1)/(tag_counts[prev_tag]+(4*len(tag_counts))-1)

model = {'tags': tag_counts, 'transition': transition_prob, 'emission': emission_prob, 'most_tag_word': send_tags}            

fhandle.write(json.dumps(model, indent=2))
#fhandle.write(json.dumps(transition_prob, indent=2))

fhandle.close
fp.close

