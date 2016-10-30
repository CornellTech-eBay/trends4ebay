# @Author: Gao Bo
# @Date:   2016-10-11T20:27:15-04:00
# @Last modified by:   Gao Bo
# @Last modified time: 2016-10-29T21:41:40-04:00



import datetime
import time
import json
import codecs
import pickle
import copy

from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection

from pytrends.request import *

from buzzfeedtrends.BFRequest import getBFTrends

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
        BFTrendsList = getBFTrendingList('trending')
        print("BuzzFeed Stories:")
        print(BFTrendsList)

        keywordsList = keywordsList[0:10] + BFTrendsList[0:10]

        print(len(keywordsList))

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
        dumpHuman(itemDictList)

        itemDictList = parseItemList(itemDictList)
        save_obj(itemDictList, 'parsedData')

    else:

        itemDictList = load_obj('parsedData')
