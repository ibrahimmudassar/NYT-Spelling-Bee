import json
from pprint import pprint

import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup
from wordfreq import zipf_frequency


def ispangram(word, alphabet):
    for letter in alphabet.upper():
        if letter not in word.upper():
            return False

    return True


soup = BeautifulSoup(requests.get(
    "https://www.nytimes.com/puzzles/spelling-bee").content, "html.parser")
# print(soup.prettify())
key = soup.findAll("script", {"type": "text/javascript"})
gameData = ""
for i in key:
    if "window.gameData = " in i.text:
        gameData = i.text.replace("window.gameData = ", "")

gameData = json.loads(gameData)['today']
pprint(gameData)


frequencies = {}
for i in gameData["answers"]:
    # zipf_frequency is a variation on word_frequency that aims to return the word frequency on a human-friendly logarithmic scale.
    # The Zipf frequency of a word is the base-10 logarithm of the number of times it appears per billion words. A word with Zipf value 6 appears once per thousand words, for example, and a word with Zipf value 3 appears once per million words.
    # Reasonable Zipf values are between 0 and 8, but because of the cutoffs described above
    # 0 is the default Zipf value for words that do not appear in the given wordlist, although it should mean one occurrence per billion words
    frequencies[i] = zipf_frequency(i, 'en')

# pprint(sorted(frequencies.items(), key=lambda x: x[1]))


df = pd.DataFrame(frequencies.items(),
                  columns=['word', 'freq (occurrence per billion)'])
df["isPangram"] = [ispangram(i, "".join(
    gameData['validLetters'])) for i in df['word']]

fig = px.strip(df, x='freq (occurrence per billion)',
               hover_data=['word'], color="isPangram", title=f"NYT Logarithmic Spelling Bee Word Frequency Spread {gameData['printDate']}")
fig.show()
