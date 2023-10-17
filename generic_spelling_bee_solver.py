from pprint import pprint

import requests


def ispangram(word, alphabet):
    for letter in alphabet.upper():
        if letter not in word.upper():
            return False

    return True


# url = "https://raw.githubusercontent.com/dwyl/english-words/master/words_dictionary.json"
# resp = requests.get(url).json()
# word_list = [word for word in resp]
url = "https://raw.githubusercontent.com/freebee-game/enable/master/enable1.txt"
resp = requests.get(url).text.upper().split("\n")

# yellow letter in the center
center = "n".upper()
# letters on the outside
outside = "xmeict".upper()

all_letters = "abcdefghijklmnopqrstuvwxyz".upper()

exclude = ""
for letter in all_letters:
    if letter not in (outside+center):
        exclude += letter

filtered = []

for word in resp:
    should_i_add = True

    for letter in exclude:
        if letter in word:
            should_i_add = False

    if should_i_add:
        filtered.append(word)

filtered = [i for i in filtered if len(i) >= 4 and center in i]
graded = {}
for word in filtered:
    score = 0

    if len(word) == 4:
        score = 1
    else:
        score = len(word)

    if ispangram(word=word, alphabet=outside+center):
        score += 7

    graded[word] = score

gradedsorted = sorted([(v, k) for k, v in graded.items()])


pprint(gradedsorted)
pprint(len(filtered))
