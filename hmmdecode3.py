import sys
import json
import os

output_file="hmmoutput.txt"
model_file="hmmmodel.txt"

model_dict = open('hmmmodel.txt', 'r', encoding='UTF-8')
model = json.loads(model_dict.read())
model_dict.close()

transition_prob = model['transition']
emission_prob = model['emission']
tag_counts = model['tags']
most_prob_word_tag = model['most_tag_word']

dev_data = sys.argv[1]

f = open(dev_data, 'r', encoding='UTF-8')
allLines = f.read()
sentenceList = allLines.splitlines()
#print(sentenceList)
taggedS = []

def SentenceTagging(Vmodel, wordList):
    curState = len(wordList)
    curTag = 'end'
    res = ""
    i = len(wordList)-1
    while i>=0:
        res = wordList[i]+"/"+Vmodel[curState][curTag]['bp']+" " + res
        curTag = Vmodel[curState][curTag]['bp']
        curState = curState-1
        i-=1
    return res

for sentence in sentenceList:
    wordList = sentence.split()
    firstWord = wordList[0]
    Vmodel = []
    Vmodel.append({})
    
    States = {}
    if firstWord in emission_prob.keys():
        States = emission_prob[firstWord]
    else:
        States = most_prob_word_tag
    for tag in States:
        if tag == 'start' or tag=='end':
            continue
        elif firstWord in emission_prob:
            e_values = emission_prob[firstWord][tag]
        #elif tag in most_prob_tags:
        #    e_values = most_prob_tags[tag]/sum(most_prob_tags.values())
        else:
            e_values = 1  #tag_counts[tag]/sum(tag_counts.values())
        Vmodel[0][tag] = {}
        Vmodel[0][tag]['prob'] = e_values * transition_prob[tag]['start']
        Vmodel[0][tag]['bp'] = 'start'
        
    for i in range(1,len(wordList)+1):
        #handling the last step for the end state
        if i==len(wordList):
            lastword = Vmodel[-1]
            States = lastword.keys()
            maxProb ={'prob':0,'bp':''}
            Vmodel.append({})
            for tag in States:
                if tag=='end':
                    continue
                else:
                    prevProb = Vmodel[-2][tag]['prob'] * transition_prob['end'][tag]

                    if (prevProb>maxProb['prob']):
                        maxProb['prob'] = prevProb
                        maxProb['bp'] = tag

            Vmodel[-1]['end'] = {}
            Vmodel[-1]['end']['prob'] = maxProb['prob']
            Vmodel[-1]['end']['bp'] = maxProb['bp']
        else:    
            currentWord = wordList[i]
            Vmodel.append({})
            if currentWord in emission_prob:
                States = emission_prob[currentWord]
            else:
                States = most_prob_word_tag
            for tag in States:
                if tag=='start' or tag=='end':
                    continue
                elif currentWord in emission_prob:
                    e_values = emission_prob[currentWord][tag]
                #elif tag in most_prob_tags:
                #    e_values = most_prob_tags[tag]/sum(most_prob_tags.values())
                else:
                    e_values = 1  #tag_counts[tag]/sum(tag_counts.values())
                maxProb ={'prob':0,'bp':''}
                for lastTag in Vmodel[i-1]:
                    if lastTag=='start' or lastTag=='end':
                        continue
                    else:
                        prevProb = Vmodel[i-1][lastTag]['prob'] * e_values * transition_prob[tag][lastTag]

                        if(prevProb>maxProb['prob']):
                            maxProb['prob'] = prevProb
                            maxProb['bp'] = lastTag

                Vmodel[i][tag] = {}
                Vmodel[i][tag]['prob'] = maxProb['prob']
                Vmodel[i][tag]['bp'] = maxProb['bp']
    #this will append the tags sentence by sentence
    taggedS.append(SentenceTagging(Vmodel, wordList))
                
fwrite = open('hmmoutput.txt', 'w', encoding = 'UTF-8')
for s in taggedS:
    fwrite.write(s+'\n')