# @Author: Gao Bo
# @Date:   2016-10-11T20:27:15-04:00
# @Last modified by:   Gao Bo
# @Last modified time: 2016-11-09T17:02:17-05:00



import datetime
import time
import json
import codecs
import pickle
import copy

from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection

import yahooWeather.yhweather as yhweather
import yahooWeather.weatherParser as weatherParser
import word_processer

from pytrends.request import *

from buzzfeedtrends.BFRequest import getBFTrends

from twitter import Twitter, OAuth

import xmltodict

datafolder = '../trendsData/'


def parseHottrends(trends):
    trendsList = trends["rss"]["channel"]["item"]
    keywordsList = []
    # tLen = len(trendsList)
    assert len(trendsList) == 20
    for tItem in trendsList:
        keywordsList.append(tItem["title"].lower())
    return keywordsList


def getItemList(ebayAPI, keywordsList, maxN):
    '''
    parameters:
    keywordsList    a list of keywords
    maxN            the max number of items returned for one keyword
    return:         A dict with keywords as keys and lists of dicts (items) as value
    '''

    itemDictList = {}
    itemDictList["keywordsList"] = keywordsList
    itemDictList["timestamp"] = time.time()

    for keyword in keywordsList:

        itemDictList[keyword] = []
        response = ebayAPI.execute('findItemsAdvanced', {'keywords': keyword, 'outputSelector': "SellerInfo"})
        if not hasattr(response.reply.searchResult, 'item'):
            continue
        assert(response.reply.ack == 'Success')
        assert(type(response.reply.timestamp) == datetime.datetime)
        assert(type(response.reply.searchResult.item) == list)
        assert(type(response.dict()) == dict)
        assert(type(response.reply.searchResult.item[0].listingInfo.endTime) == datetime.datetime)

        item = response.reply.searchResult.item

        for i in range(min(maxN, len(item))):
            # print ("item title: ", item[i].title)
            # print ("seller info: ", item[i].sellerInfo.topRatedSeller)
            # print ("seller feedbackScore: ", item[i].sellerInfo.feedbackScore)
            isTopRatedSeller = item[i].sellerInfo.topRatedSeller
            score = float(item[i].sellerInfo.feedbackScore)
            itemDictList[keyword].append(item[i])
            # if (score >= 10000):
            #     print ("saved")
            #     itemDictList[keyword].append(item[i])
            # else:
            #     if (len(item) > 1):
            #         if (float(item[i + 1].sellerInfo.feedbackScore) >= 10000):
            #             print ("item title: ", item[i + 1].title)
            #             print ("seller info: ", item[i + 1].sellerInfo.topRatedSeller)
            #             print ("saved second chance")
            #             itemDictList[keyword].append(item[i + 1])
            # print ("itemDictList value: ", itemDictList[keyword][0].sellerInfo)
    return itemDictList


# filtering function
def validItem(item):
    return (item.topRatedListing.lower() == 'true')


def parseItemList(itemDictList):
    '''
    parameters:
    itemDictList    a dict with the keys being "keywordsList" and "timestamp" and a list a keywords
    '''

    # tempItem = {"viewItemURL": "", "galleryURL": "", "title": "", "itemId": ""}

    shortItemDict = {}
    shortItemDict["keywordsList"] = itemDictList["keywordsList"]
    shortItemDict["timestamp"] = itemDictList["timestamp"]

    for keyword in shortItemDict["keywordsList"]:
        shortItemDict[keyword] = []
        for item in itemDictList[keyword]:
            tItem = {}
            if not (hasattr(item, 'viewItemURL') and hasattr(item, 'galleryURL') and hasattr(item, 'title') and hasattr(item, 'itemId') and hasattr(item, 'sellingStatus') and hasattr(item, 'topRatedListing')): continue
            # if not validItem(item): continue
            tItem["viewItemURL"] = item.viewItemURL
            tItem["galleryURL"] = "http://i.ebayimg.com/images/i/%s-0-1/s-l1000.jpg" % (item.itemId)
            tItem["title"] = item.title
            tItem["itemId"] = item.itemId
            tItem["currentPrice"] = item.sellingStatus.currentPrice.value
            tItem["topRatedListing"] = item.topRatedListing
            shortItemDict[keyword].append(tItem)

    return shortItemDict


def save_obj(obj, name):
    with codecs.open(datafolder + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f)


def load_obj(name):
    with open(datafolder + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def load_settings(name):
    settingDict = {}
    with open(datafolder + name, 'r') as f:
        key = f.readline()
        content = f.readline()
        if content: settingDict[key.strip()] = content.lower().strip().split(',')
        else: settingDict[key.strip()] = []
        key = f.readline()
        content = f.readline()
        if content: settingDict[key.strip()] = content.lower().strip().split(',')
        else: settingDict[key.strip()] = []
    assert("blacklist" in settingDict)
    assert("whitelist" in settingDict)
    return settingDict


def dumpHuman(itemDictList):
    # dump the item list
    outfile = codecs.open(datafolder + "itemsOutput.txt", "w", "utf-8")
    for keyword in itemDictList['keywordsList']:
        outfile.write(keyword + '\n\n')
        for item in itemDictList[keyword]:
            outfile.write(str(item) + '\n\n')
        outfile.write('\n\n')
    outfile.close()


def getBFTrendingList(section='trending'):
    parsedBFTrends = getBFTrends(section)
    BFTrendsList = []
    for buzz in parsedBFTrends:
        BFTrendsList.append(buzz['title'])

    return BFTrendsList


def SEO(settingDict, keywordsList):
    nkeywordsList = settingDict['whitelist']
    for keyword in keywordsList:
        notInBlacklist = True
        for blackword in settingDict['blacklist']:
            if blackword in keyword:
                notInBlacklist = False
                break
        if (notInBlacklist): nkeywordsList.append(keyword)

    return nkeywordsList[0: min(20, len(nkeywordsList))]


def get_weather_keywords(location):
    title, text, temp_today, temp_future, temp_diff = yhweather.get_weather(location)
    print ("Today's weather: ", title)
    print ("Condition ", text.strip().lower())
    print ('temperature today: ', temp_today)
    print ('temperature in a week: ', temp_future)
    temp_diff = float(temp_diff)
    print ('temp_diff: ', temp_diff)
    weather_keywords = ["get weather keywords unsuccessfully"]
    temperature_keywords = ["no indicator of changing season currently"]
    all_weather_keywords = weatherParser.weather_keywords()
    all_temperature_keywords = weatherParser.temperature_keywords()
    categories = ["overcast", "rainy", "snow", "sunny"]
    all_category = weatherParser.weather_category()
    # print (all_category)
    # Getting weather keywords for temperature change
    if temp_diff < -10:
        temperature_keywords = all_temperature_keywords[0]
    if temp_diff > 10:
        temperature_keywords = all_temperature_keywords[1]

    # Getting weather keywords for weather condition
    for i, category in enumerate(all_category):
        if text.strip().lower() in category:
            weather_keywords = all_weather_keywords[i]
    return weather_keywords, temperature_keywords



if __name__ == "__main__":

    getData = True

    if getData:

        google_username = "cornelltechebay@gmail.com"
        google_password = "cornell&ebay"
        ebayappid = 'BoGao-CornellT-PRD-a9f17700d-30f3e552'

        # get hot searches on google
        pytrends = TrendReq(google_username, google_password, custom_useragent=None)
        hottrendsdetail = xmltodict.parse(pytrends.hottrendsdetail({}))

        # parse the searches into keywords
        # googleKeywords = parseHottrends(hottrendsdetail)
        googleKeywords = ["thanksgiving decorations", "harry potter", "2016-17 nfl season", "cleveland cavaliers", "fallout 4", "leonardo dicaprio", "Donald Trump", "Metallica", "Houston Astros", "Kris Bryant‬", "Amazon.com"]
        print("Google Keywords List:")
        print(googleKeywords)

        # get buzzfeed trends
        # BFTrendsList = getBFTrendingList('trending')
        # print("BuzzFeed Stories:")
        # print(BFTrendsList)

        # get twitter trends
        config = {
        'consumer_key' : 'HsSAsHDYrqs1gkVDVI6djlV88',
        'consumer_secret' : '323NIf8LGUH3Umm1WXG8mTZ3ti68h8wOM9d5LU8mTC1R84wNoc',
        'access_key' : '796465615720640512-YXBMkfdYswssF17ln9SsxFFCdxHr69G',
        'access_secret' : 'Pd2ZUzQER5HLTPorsXISTjUinMSXXqZvOZhsDL3VNq3f5'}

        twitter = Twitter(auth = OAuth(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"]))

        results = twitter.trends.place(_id = 2459115)
        # localised trends can be specified by looking up WOE IDs:
        # http://woeid.rosselliot.co.nz/lookup/
        # WOEID for NYC is 2459115, for the world is 1, for United States is 23424977
        print("Twitter NYC Trends:")
        twitter_keywords = []
        # for location in results:
        #     for trend in location["trends"]:
        #         words = trend["name"].strip("#")
        #         twitter_keywords.append(words)
        # print (twitter_keywords)
        # twitter_keywords = ["Paris Hilton", "super moon", "Mitt Romney", "Knicks"]
        keywordsList = googleKeywords

        #  Merging different sources of keywords
        # for i in range(max(len(twitter_keywords), len(googleKeywords))):
        #     if i < len(googleKeywords):
        #         keywordsList.append(googleKeywords[i])
        #     if i < len(googleKeywords):
        #         keywordsList.append(twitter_keywords[i])
        # print ("merged raw keyword list: ", keywordsList)

        # topKeywordsList = word_processer.processer(keywordsList)
        #  To turn off printing: processer(keywords_list, printed=True)
        # print ("top words: ", topKeywordsList)
        # keywordsList = topKeywordsList + keywordsList
        # if getting weather keywords successfully
        # get weather keywords
        # weather_keywords, temperature_keywords = get_weather_keywords(2459115)
        # if (len(temperature_keywords) != 1):
        #     keywordsList = temperature_keywords + keywordsList
        #     if (len(weather_keywords) != 1):
        #         keywordsList = weather_keywords[:2] + keywordsList
        # else:
        # #  if no temperature_keywords is available
        #     if (len(weather_keywords) != 1):
        #         keywordsList = keywordsList + weather_keywords
        # print ("after weather merge: ", keywordsList)
        # keywordsList = ["New York Giants", "New York Jets"] + keywordsList
        # print(len(keywordsList))
        # keywordsList = keywordsList[:40]
        # get settings
        settingDict = load_settings("adminsettings")
        print("Settings")
        print(settingDict)

        # keywordsList = SEO(settingDict, keywordsList)
        print("Keywords List")
        print(keywordsList)

        # set up a connection with eBay
        try:
            ebayAPI = Connection(appid=ebayappid, config_file=None)
        except ConnectionError as e:
            print(e)
            print(e.response.dict())

        # get the item lists from ebay
        itemDictList = getItemList(ebayAPI, keywordsList, 1)

        save_obj(itemDictList, 'rawData')
        # dumpHuman(itemDictList)

        itemDictList = parseItemList(itemDictList)
        save_obj(itemDictList, 'parsedData')

    else:
        pass
