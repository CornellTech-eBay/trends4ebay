# @Author: Gao Bo
# @Date:   2016-10-11T20:27:15-04:00
# @Last modified by:   Gao Bo
# @Last modified time: 2016-10-11T20:32:05-04:00



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


if __name__ == "__main__":
    # get hot searches on google
    google_username = "cornelltechebay@gmail.com"
    google_password = "cornell&ebay"
    pytrends = TrendReq(google_username, google_password, custom_useragent=None)

    # parse the searches into keywords
    keywordsList = parseHottrends(hottrendsdetail)
    print("Keywords List")
    print(keywordsList)

    # set up a connection with eBay
    ebayAPI = Connection(appid='BoGao-CornellT-PRD-a9f17700d-30f3e552', config_file=None)
    response = ebayAPI.execute('findItemsAdvanced', {'keywords': 'iphone'})
