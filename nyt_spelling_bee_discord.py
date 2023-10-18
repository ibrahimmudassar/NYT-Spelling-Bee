# An implementation of nyt_spelling_bee_solver.py but it sends a discord embed to be

from PIL import Image
import json
from datetime import datetime
from pprint import pprint

import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook
from environs import Env
from wordfreq import zipf_frequency

# Setting up environment variables
env = Env()
env.read_env()  # read .env file, if it exists


def ispangram(word, alphabet):
    for letter in alphabet.upper():
        if letter not in word.upper():
            return False

    return True


soup = BeautifulSoup(requests.get(
    "https://www.nytimes.com/puzzles/spelling-bee").content, "html.parser")
key = soup.findAll("script", {"type": "text/javascript"})
gameData = ""
for i in key:
    if "window.gameData = " in i.text:
        gameData = i.text.replace("window.gameData = ", "")

gameData = json.loads(gameData)['today']
# pprint(gameData)

frequencies = {}
graded = {}
for word in gameData["answers"]:
    # zipf_frequency is a variation on word_frequency that aims to return the word frequency on a human-friendly logarithmic scale.
    # The Zipf frequency of a word is the base-10 logarithm of the number of times it appears per billion words. A word with Zipf value 6 appears once per thousand words, for example, and a word with Zipf value 3 appears once per million words.
    # Reasonable Zipf values are between 0 and 8, but because of the cutoffs described above
    # 0 is the default Zipf value for words that do not appear in the given wordlist, although it should mean one occurrence per billion words
    frequencies[word] = zipf_frequency(word, 'en')

    score = 0

    if len(word) == 4:
        score = 1
    else:
        score = len(word)

    if ispangram(word=word, alphabet="".join(gameData['validLetters'])):
        score += 7

    graded[word] = score


df = pd.DataFrame(frequencies.items(),
                  columns=['word', 'freq (occurrence per billion)'])
df['score'] = df['word'].map(graded)
df["isPangram"] = [ispangram(i, "".join(
    gameData['validLetters'])) for i in df['word']]

fig = px.strip(df, x='freq (occurrence per billion)',
               hover_data=df.columns, color="isPangram", title=f"NYT Spelling Bee Logarithmic Word Frequency Spread {gameData['printDate']}")

# Add image


# fig.add_layout_image(
#     dict(
#         xref="paper", yref="paper",
#         x=1.1, y=1.02,
#         sizex=0.22, sizey=0.22,
#         xanchor="right", yanchor="bottom"
#     )
# )

fig.write_image("fig1.png", width=1280, height=720)

# print the top 10 scores
top_5 = df.nlargest(5, 'score').query('isPangram == False')["word"].tolist()

rare_5 = df.nsmallest(5, 'freq (occurrence per billion)').query(
    'isPangram == False')["word"].tolist()


# create embed object for webhook
embed = DiscordEmbed(title='NYT Spelling Bee Answers', color='f7db1b')

# set author
embed.set_author(name=gameData['editor'])

embed.set_image(url='attachment://fig1.png')

# set thumbnail
# Open the image from the URL
now = datetime.now()
image_url = f'https://static01.nyt.com/images/{now.strftime("%Y/%m/%d")}/multimedia/{now.strftime("%d")}morning-bee/{now.strftime("%d")}morning-bee-superJumbo.png?quality=100&auto=png'
image = Image.open(requests.get(image_url, stream=True).raw)

# Make the white background transparent
image = image.convert("RGBA")
datas = image.getdata()
new_data = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        new_data.append((255, 255, 255, 0))
    else:
        new_data.append(item)
image.putdata(new_data)

# Center crop the image to 1:1 aspect ratio
width, height = image.size
if width > height:
    left = (width - height) / 2
    top = 0
    right = (width + height) / 2
    bottom = height
else:
    left = 0
    top = (height - width) / 2
    right = width
    bottom = (height + width) / 2
image = image.crop((left, top, right, bottom))

# Save the resulting image as a PNG
image.save("result.png", "PNG")
embed.set_thumbnail(
    url='attachment://result.png')

# set footer
embed.set_footer(text='Made By Ibrahim Mudassar',
                 icon_url='https://avatars.githubusercontent.com/u/22484328?v=4')

# set timestamp (default is now) accepted types are int, float and datetime
embed.set_timestamp()

# add fields to embed
embed.add_embed_field(name='Pangrams', value="\n".join(gameData["pangrams"]))

# add fields to embed
embed.add_embed_field(name='Top Words', value="\n".join(top_5))

# add fields to embed
embed.add_embed_field(name='Rare Words', value="\n".join(rare_5))

# add embed object to webhook(s)
for webhook_url in env.list("WEBHOOKS"):
    webhook = DiscordWebhook(url=webhook_url)

    with open("fig1.png", "rb") as f:
        webhook.add_file(file=f.read(), filename='fig1.png')

    with open("result.png", "rb") as f:
        webhook.add_file(file=f.read(), filename='result.png')

    webhook.add_embed(embed)
    webhook.execute()
