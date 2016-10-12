# @Author: Gao Bo
# @Date:   2016-10-11T15:21:44-04:00
# @Last modified by:   Gao Bo
# @Last modified time: 2016-10-11T20:32:42-04:00



import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection

try:
    ebayAPI = Connection(appid='BoGao-CornellT-PRD-a9f17700d-30f3e552', config_file=None)

    response = ebayAPI.execute('findItemsAdvanced', {'keywords': 'iphone'})

    assert(response.reply.ack == 'Success')
    assert(type(response.reply.timestamp) == datetime.datetime)
    assert(type(response.reply.searchResult.item) == list)
    item = response.reply.searchResult.item[0]
    assert(type(item.listingInfo.endTime) == datetime.datetime)
    assert(type(response.dict()) == dict)

    outfile = open('itemsOutput.txt', 'w')
    for i in range(5):
        outfile.write(str(response.reply.searchResult.item[i]) + '\n\n')
    outfile.close()

except ConnectionError as e:
    print(e)
    print(e.response.dict())
