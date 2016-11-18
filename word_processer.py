import re
import nltk
import string
from nltk.tokenize import RegexpTokenizer
import numpy as np
import collections
import operator

tokenizer = RegexpTokenizer(r'\w+')

def processer(keywords_list, printed=True):
# preprocessing reference: http://billchambers.me/tutorials/2015/01/14/python-nlp-cheatsheet-nltk-scikit-learn.html
    word_count_dict = {}
    data = []
    for word_phrase in keywords_list:
        words = tokenizer.tokenize(word_phrase.strip().lower())
        data.append(words)

    ordered_keywords = []
    occurence = []
    for i, words in enumerate(data):
        count = 0
        for other_words in data[(i+1):]:
            overlap = set(words).intersection(other_words)
            count += len(overlap)
        words = " ".join(words)
        ordered_keywords.append(words)
        occurence.append(count + 1)
    word_count_dict = zip(ordered_keywords, occurence)
    word_count_dict = {key:value for key, value in word_count_dict}
    word_count_dict = sorted(word_count_dict.items(), key=operator.itemgetter(1), reverse=True)
    if printed == True:
        print ("Printing word count dict: ", word_count_dict)
    # sorted_keywords = [words[0] for words in word_count_dict]
    top_keywords = [words[0] for words in word_count_dict if words[1] > 1]
    return (top_keywords)
#
# keywords_list = ['powerball', 'empire', 'american horror story', 'designated survivor', 'arrow', 'gary johnson', 'cnn polls', 'twitter', 'california propositions', 'huffington post', 'putin', 'trump cabinet', 'google news', 'drudge', 'yahoo finance', 'simpsons predictions trump', 'walmart black friday 2016 ad', 'stranger things cast', 'how to impeach a president', 'xenophobia', 'Shop Here', 'ALL ITEMS ON SALE TODAY ONLY', 'Dream Kardashian', 'New Balance', 'Trump', 'Empire', 'TopCausesOfTwitterDrama', 'ClassicRockFood', 'Howard Dean', 'Silver Slugger', 'Coutinho', 'boycottgrubhub', 'DaeDaeDec3rd', 'Blac Chyna', 'Gary Trent Jr.', 'P.J. Washington', 'Conor McGregor', 'Rules for Survival', 'Vamos Argentina', 'Childish Gambino', 'Matt Beleskey', 'Megan Walker', 'Mascherano', 'Wallace Wade', 'Bob Iger', 'Jobs & Tech', 'Drew Barker', 'Torey Krug', 'BravsArg', 'CLEvsBAL', 'ThursdayThought', 'LittleKnownTrafficLaws', 'whatisschool', 'FacingRace', 'safetypin', 'ARGvBRA', 'RYMR6Chat', 'UNCvsDUKE', 'NGKVideoMidnight', 'wie2016', 'capitalfoodfight', 'PartyOlympus', 'SeesawChat', 'ANightWithNU', 'manniquinChallange', 'VamosColombia', 'kavliconvo', 'CES2017', 'InsteadOfBacon', 'MINvsPIT']
# print (processer(keywords_list))
