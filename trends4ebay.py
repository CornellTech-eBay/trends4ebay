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

        print(keyword)

        itemDictList[keyword] = []
        response = ebayAPI.execute('findItemsAdvanced', {'keywords': keyword})
        if not hasattr(response.reply.searchResult, 'item'):
            continue
        assert(response.reply.ack == 'Success')
        assert(type(response.reply.timestamp) == datetime.datetime)
        assert(type(response.reply.searchResult.item) == list)
        assert(type(response.dict()) == dict)
        assert(type(response.reply.searchResult.item[0].listingInfo.endTime) == datetime.datetime)

        item = response.reply.searchResult.item

        for i in range(min(maxN, len(item))):
            itemDictList[keyword].append(item[i])

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
    print ('temp_diff: ', temp_diff)
    weather_keywords = ["get weather keywords unsuccessfully"]
    all_weather_keywords = weatherParser.weather_keywords()
    categories = ["overcast", "rainy", "snow", "sunny"]
    all_category = weatherParser.weather_category()
    print (all_category)
    for i, category in enumerate(all_category):
        print ("why", text.strip().lower(), category)
        if text.strip().lower() in category:
            weather_keywords = all_weather_keywords[i]
    return weather_keywords



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
        keywordsList = parseHottrends(hottrendsdetail)
        print("Keywords List:")
        print(keywordsList)

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
        for location in results:
            for trend in location["trends"]:
                words = trend["name"]
                twitter_keywords.append(words)

        keywordsList = keywordsList + twitter_keywords


        # get weather keywords
        weather_keywords = get_weather_keywords(2459115)
        keywordsList = word_processer.processer(keywordsList)
        # if getting weather keywords successfully
        if (len(weather_keywords) != 1):
            keywordsList = weather_keywords + keywordsList


        print(len(keywordsList))
        keywordsList = keywordsList[:20]
        # get settings
        settingDict = load_settings("adminsettings")
        print("Settings")
        print(settingDict)

        keywordsList = SEO(settingDict, keywordsList)
        print("Keywords List")
        print(keywordsList)

        # set up a connection with eBay
        try:
            ebayAPI = Connection(appid=ebayappid, config_file=None)
        except ConnectionError as e:
            print(e)
            print(e.response.dict())

        # get the item lists from ebay
        itemDictList = getItemList(ebayAPI, keywordsList, 5)

        save_obj(itemDictList, 'rawData')
        # dumpHuman(itemDictList)

        itemDictList = parseItemList(itemDictList)
        save_obj(itemDictList, 'parsedData')

    else:
        pass
