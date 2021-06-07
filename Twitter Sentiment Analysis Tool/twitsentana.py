import sys, tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import numpy as np
from PIL import Image
from imageio import imread
import nltk
from stop_words import get_stop_words
import re


analyzer = SentimentIntensityAnalyzer()

def percentage(part, whole):
    return 100 * float(part)/float(whole)

#Connecting to the API
consumer_key = "INSERTYOUR KEY"
consumer_secret = "INSERT YOUR KEY"

access_token = "INSERT YOUR TOKEN"
access_token_secret = "INSERT YOUR SECRET TOKEN"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

#Prompting user input
searchterm = input("Enter Keyword to search for: ")
numberoftweets = int(input("Enter how many tweets you want to analyze: "))

tweets = tweepy.Cursor(api.search, q=searchterm).items(numberoftweets)

neutral = 0
positive = 0
negative = 0  
polarity = 0

text=""
#Cleaning data
def remove_url(txt):
    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())

#Calculating the sentiment
for tweet in tweets:

    remove_url(tweet.text)

    analysation = analyzer.polarity_scores(tweet.text)

    text+=tweet.text

    if analysation["compound"] >= 0.05:
        positive += 1
    elif analysation["compound"] <= -0.05:
        negative += 1
    else:
        neutral+=1

#Clean data and add the text from the twets up
removewords = ["https", "RT", ".de", "said", "dear", "www", "com", "retweet", "pinned",
 "post", "re.sub","@", ".com", ".co", "Follow", "tweet", "a-z","h/t","can´t","don´t",
 "won´t","shouldn´t","wouldn´t","doesn´t", "didn´t","mustn´t","die","der","noch", "haben","wollen", "heute"]

for word in removewords:
    text = text.replace(word, "")

#Calculating percentage
positive = percentage(positive, numberoftweets)
negative = percentage(negative, numberoftweets)
neutral = percentage(neutral, numberoftweets)

positive = format(positive, ".2f")
negative = format(negative, ".2f")
neutral = format(neutral, ".2f")

print("How people react to "+ searchterm + " through analyzing " + str(numberoftweets) + " Tweets.")

#Visualizing the pie chart
f1 = plt.figure(1)
labels = ["Positive [" + str(positive) + "%]", "Neutral [" + str(neutral) + "%]", "Negative [" + str(negative) + "%]"]
sizes = [positive, neutral, negative]
colors = ["yellowgreen", "gold", "red"]
patches, texts = plt.pie(sizes, colors=colors, startangle=90)
plt.legend(patches, labels, loc="best")
plt.title("Twitter Sentiment about "+searchterm+" by analyzing "+str(numberoftweets)+" Tweets.")
plt.axis("equal")
plt.tight_layout()

stopwords = get_stop_words("german")+list(STOPWORDS)


logomask = imread("twitterlogo2.jpg")

#appearance
wc=WordCloud(background_color="white",
mask = logomask,
max_words=500,
stopwords=stopwords,
height = 1350,
min_word_length = 3,
repeat = False,
width=1200).generate(text)

#plotting
f2 = plt.figure(2)
plt.imshow(wc, interpolation = "bilinear")
plt.axis("off")
plt.show()




