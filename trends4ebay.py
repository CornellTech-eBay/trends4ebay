# @Author: Gao Bo
# @Date:   2016-10-11T20:27:15-04:00
# @Last modified by:   Gao Bo
# @Last modified time: 2016-10-11T20:59:13-04:00



import datetime
import json

from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection

from pytrends.request import *
import xmltodict


def parseHottrends(trends):
    trendsList = trends["rss"]["channel"]["item"]
    keywordsList = []
    # tLen = len(trendsList)
    assert len(trendsList) == 20
    for tItem in trendsList:
        keywordsList.append(tItem["title"])
    return keywordsList


def getItemList(ebayAPI, keywordsList, maxN):
    '''
    parameters:
    keywordsList    a list of keywords
    maxN            the max number of items returned for one keyword
    return:         A dict with keywords as keys and lists of dicts (items) as value
    '''

    itemDictList = {}

    for keyword in keywordsList:
        itemDictList[keyword] = []
        response = ebayAPI.execute('findItemsAdvanced', {'keywords': keyword})
        assert(response.reply.ack == 'Success')
        assert(type(response.reply.timestamp) == datetime.datetime)
        assert(type(response.reply.searchResult.item) == list)
        assert(type(response.dict()) == dict)
        assert(type(response.reply.searchResult.item[0].listingInfo.endTime) == datetime.datetime)

        item = response.reply.searchResult.item

        for i in range(min(maxN, len(item))):
            itemDictList[keyword].append(item[i])

    return itemDictList


if __name__ == "__main__":

    google_username = "cornelltechebay@gmail.com"
    google_password = "cornell&ebay"
    ebayappid = 'BoGao-CornellT-PRD-a9f17700d-30f3e552'

    # get hot searches on google
    pytrends = TrendReq(google_username, google_password, custom_useragent=None)
    hottrendsdetail = xmltodict.parse(pytrends.hottrendsdetail({}))

    # parse the searches into keywords
    keywordsList = parseHottrends(hottrendsdetail)
    print("Keywords List")
    print(keywordsList)

    # set up a connection with eBay
    try:
        ebayAPI = Connection(appid=ebayappid, config_file=None)
    except ConnectionError as e:
        print(e)
        print(e.response.dict())
    response = ebayAPI.execute('findItemsAdvanced', {'keywords': 'iphone'})

    # get the item lists from ebay
    itemDictList = getItemList(ebayAPI, keywordsList, 5)


    # dump the result
    outfile = open('itemsOutput.txt', 'w')

    for keyword in keywordsList:
        outfile.write(keyword + '\n\n')
        for item in itemDictList[keyword]:
            outfile.write(str(item) + '\n\n')
        outfile.write('\n\n')

    outfile.close()
