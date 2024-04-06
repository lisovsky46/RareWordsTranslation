import string
import nltk
import sys
import os
from nltk.corpus import brown
import deepl
import constants

#nltk.download('brown')

output_count = 200
deelp_auth_key = constants.deelp_auth_key
test_path = "D:\Code\Python\Scripts\RareWordsTranslation\subs2.srt"


class WordLocation:
    def __init__(self, lineNum, lineTime, subLines):
        self.lineNum = lineNum
        self.time = lineTime
        self.lines = subLines


        
def appendLine(wordsDict: dict, wordLoc: WordLocation):
    for line in wordLoc.lines:
        for word in line.translate(str.maketrans('', '', r"""!"#$%&()*+,-./:;<=>?@[\]^_`{|}~""")).split():
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


def sortWords(wordsDict: dict):
    # collect frequency information from brown corpus, might take a few seconds
    freqs = nltk.FreqDist([w.lower() for w in brown.words()])
    # sort wordlist by word frequency
    wordlist_sorted = dict(sorted(wordsDict.items(), key=lambda x: freqs[x[0]]))
    # print the sorted list
    return wordlist_sorted


def translate(wordsDict: dict):
    translator = deepl.Translator(deelp_auth_key)
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
            translated = translatedWords[index].text
            index += 1

            result = f'{k:15} Translation: {translated:30} Example: {lines:80} Time: {time:18} Count: {usages}\n'

            print (result, file=file_object)



# path = sys.argv[1]
path = test_path
wordsDict = ExtractWords(path)
sortedWords = sortWords(wordsDict)
limitedWords = dict(list(sortedWords.items())[:output_count])
translatedWords = translate(limitedWords)
# sortedWords = dict(reversed(list(sortedWords.items())))

oldPath, filename = os.path.split(path)
filename = os.path.splitext(filename)[0]
newfilename = '%s_top_%s.srt' % (filename, output_count)
newpath = os.path.join(oldPath, newfilename)

saveSorted(limitedWords, translatedWords, newpath)