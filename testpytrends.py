# @Author: Gao Bo
# @Date:   2016-10-03T22:39:11-04:00
# @Last modified by:   Gao Bo
# @Last modified time: 2016-10-11T20:21:34-04:00



from pytrends.request import *
import json
import xmltodict

def parsetop30in30(trends):
    tdate = 0
    # test: just get the most trending term of the first day of this week
    # date is a string
    date = trends["weeksList"][-1]["daysList"][tdate]["longFormattedDate"]
    # title if a string
    title = trends["weeksList"][-1]["daysList"][tdate]["data"]["trend"]["title"]
    # relatedSearchesList is a list of strings
    relatedSearchesList = trends["weeksList"][-1]["daysList"][tdate]["data"]["trend"]["relatedSearchesList"]

    print("On " + date)
    print("Most trending: " + title)
    print("Related searches:")
    print(", ".join(relatedSearchesList))
    # for term in relatedSearchesList:
    #     print()

def parseHottrends(trends):
    trendsList = trends["rss"]["channel"]["item"]
    keywordsList = []
    # tLen = len(trendsList)
    assert len(trendsList) == 20
    for tItem in trendsList:
        keywordsList.append(tItem["title"])
    return keywordsList


if __name__ == "__main__":
    google_username = "cornelltechebay@gmail.com"
    google_password = "cornell&ebay"
    pytrends = TrendReq(google_username, google_password, custom_useragent=None)

    # top30 = pytrends.top30in30()
    # parsetop30in30(top30)
    # hottrendsdetail = pytrends.hottrends({})

    # get trending searches now
    hottrendsdetail = xmltodict.parse(pytrends.hottrendsdetail({}))
    keywordsList = parseHottrends(hottrendsdetail)

    print(keywordsList)

    outfile = open('trendsOutput.txt', 'w')
    outfile.write(json.dumps(hottrendsdetail, sort_keys=True, indent=4, separators=(',', ': ')))
    outfile.close()
