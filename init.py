import csv
import string
import nltk
import sys
import os
from nltk.corpus import brown
import deepl
import constants

#nltk.download('brown')
deepl_auth_key = ""


class WordLocation:
    def __init__(self, lineNum, lineTime, subLines):
        self.lineNum = lineNum
        self.time = lineTime
        self.lines = subLines


        
def appendLine(wordsDict: dict, wordLoc: WordLocation):
    for line in wordLoc.lines:
        for word in line.translate(str.maketrans('', '', r"""!"#$%&()*+,./:;<=>?@[\]^_`{|}~""")).split():
            word = word.lower()
            if word in wordsDict:
                wordsDict[word].append(wordLoc)
            else:
                wordsDict[word] = [wordLoc]



def ExtractWords(path):
    subs = open(path)
    lines = subs.readlines()
    subLines = []
    state = 9
    wordsDict = dict()

    for line in lines:
                
        if (state == 9 and int(line)):
            state = 0
            subNumber = int(line)
            continue

        if (state == 0):
            state = 1
            subTime = line
            continue

        if (state == 1):
            if line.isspace():
                wordLoc = WordLocation(subNumber, subTime, subLines)
                appendLine(wordsDict, wordLoc)
                subLines = []
                state = 9
            else:
                subLines.append(line) 
            continue
    
    return wordsDict

# def FilterWords(wordsDict: dict):
#     dict(wordsDict)

def FilterWord(word):
    if (len(set(word))) < constants.min_word_length:
        return False
    if "'" in word:
        return False
    return True
    
def read_csv_to_dict(filename):
  my_dict = {}
  with open(filename, 'r') as csvfile:
    reader = csv.reader(csvfile)
    # Assuming the first row is the header
    headers = next(reader)  # Read and store the header row
    for row in reader:
      key = row[0]  # Assuming the first element is the key
      my_dict[key] = row[1]  # Remaining elements as a list (value)
  return my_dict

def sortWords(wordsDict: dict, freqs: dict):
    # collect frequency information from brown corpus, might take a few seconds
    # freqs = nltk.FreqDist([w.lower() for w in brown.words()])
    
    # end open file
    # sort wordlist by word frequency
    wordlist_sorted = dict(sorted(wordsDict.items(), key=lambda x: freqs.get(x[0], -1)))
    # print the sorted list
    return wordlist_sorted


def translate(wordsDict: dict):
    if not deepl_auth_key:
        return dict()
    translator = deepl.Translator(deepl_auth_key)
    result = translator.translate_text(wordsDict.keys(), target_lang="RU")
    return result

    
def saveSorted(wordlist_sorted: dict, translatedWords, path):

    with open(path, mode='w') as file_object:
        index = 0
        for k, v in wordlist_sorted.items():
            
            usages = len(v)
            first: WordLocation
            first = v[0]
            lines = " ".join(first.lines).replace("\n", "")
            time = first.time.replace("\n", "")[:8]
            translated = translatedWords[index].text if deepl_auth_key else 'None'
            index += 1

            result = f'{k:15} Translation: {translated:30} Example: {lines:80} Time: {time:18} Count: {usages}\n'

            print (result, file=file_object)



path = sys.argv[1]
deepl_auth_key =  sys.argv[2] if len(sys.argv) > 2 else "" #constants.deepl_auth_key
wordsDict = ExtractWords(path)
filteredDict = {k: v for k, v in wordsDict.items() if FilterWord(k)}
freqs =  nltk.FreqDist([w.lower() for w in brown.words()]) #read_csv_to_dict(constants.freqs_file)
sortedWords = sortWords(filteredDict, freqs)
limitedWords = dict(list(sortedWords.items())[:constants.default_output_count])
translatedWords = translate(limitedWords)
# sortedWords = dict(reversed(list(sortedWords.items())))

oldPath, filename = os.path.split(path)
filename = os.path.splitext(filename)[0]
newfilename = '%s_top_%s.txt' % (filename, constants.default_output_count)
newpath = os.path.join(oldPath, newfilename)

saveSorted(limitedWords, translatedWords, newpath)