from lxml import html
import nltk
import requests
from nltk.tokenize import RegexpTokenizer

# def parse_XML():
#     page = requests.get('http://www.ticketsnow.com/')
#     print ("page", page)
#     tree = html.fromstring(page.content)
#     print ("tree", type(tree))
#     # find every <li> in the <ul> under div with class div_class
#     raw_html = tree.xpath("//div[@class='subMenuTable']/a")
#     for item in raw_html:
#         print(type(item))
#     #This will create a list of buyers:
#
#     #This will create a list of prices
#     # prices = tree.xpath('//span[@class="item-price"]/text()')
def loadEvents():
    location = []
    team = []
    events = []
    files = open("./events.txt", "rb")
    tokenizer = RegexpTokenizer(r'\w+')
    files.readline()
    for line in files:
        words = tokenizer.tokenize(line.strip().decode('utf-8'))
        events.append(words)
    location = [" ".join(row[:-1]) for row in events]
    team = [" ".join(row) for row in events]
    sports_event_dict = zip(location, team)
    sports_event_dict = {key:value for key, value in sports_event_dict}
    return sports_event_dict
print (loadEvents())
