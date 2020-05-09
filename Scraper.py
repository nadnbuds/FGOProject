import requests
import time
from requests.exceptions import RequestException
from tqdm import tqdm
from contextlib import closing
from bs4 import BeautifulSoup

#Config Values
UpdateLocalFiles = False
BaseURL = 'https://gamepress.gg'
ListURL = '/grandorder/servants'
PathToFiles = "./Scraping Initial Data/"

#Blacklist Servants that aren't obtainable
BlackList = [
    '/grandorder/servant/beast-iiil',
    '/grandorder/servant/solomon-grand-caster',
    '/grandorder/servant/goetia',
    '/grandorder/servant/tiamat',
    '/grandorder/servant/solomon-true',
    '/grandorder/servant/beast-iiir'
]

#Globals
ServantList = []

class ServantInfo:
    def __init__(self, link):
        self.url = link['href']
        self.name = link.contents[0].replace('\\n', '')
        ScrapeServant(BaseURL + self.url, self)

#DFS Traversal of HTML until leaf is hit
def FindFirstBottom(soup):
    temp = soup
    bottom = False
    while not bottom:
        bottom = True
        #Check if current level has any contents
        if hasattr(temp, 'contents'):
            for content in temp.contents:
                #Check if the contents are traversible or just strings
                if hasattr(content, 'contents'):
                    temp = content
                    bottom = False
                    break
    return temp.text

#Handles the Subheader div class
def ScrapeSubheader(soup, servant):
        #classIcon = soup.find('span', {'class': 'class-icon'})
        servant.classTitle = FindFirstBottom(soup.find('span', {'class': 'class-title'}))
        servant.rarity = FindFirstBottom(soup.find('span', {'class': 'class-rarity'}))

def ScrapeServant(link, servant):
    #Define the File Name of Servant to be Scraped
    ServantPage = PathToFiles + link.split('/')[-1] + ".html"

    #Update Local HTML Pages to not accidently DDoS Site while testing
    if(UpdateLocalFiles):
        page = requests.get(link).content
        file = open(ServantPage, "w+", encoding="utf-8")
        file.write(str(page))
        time.sleep(5)
        file.close()
    
    #Init BS4
    file = open(ServantPage, "r", encoding="utf-8")
    soup = BeautifulSoup(file, 'html.parser')
    file.close()

    #Run BS4 On Local Page of Servant
    #Div SubHeader for Class Icon, Title, Rarity
    subheader = soup.find('div', {'id': 'servant-subheader'})
    if subheader != None:
        ScrapeSubheader(subheader, servant)

def ScrapeServantList():
    #Define the File Name for the list of Servants to be Scraped
    ListPage = PathToFiles + "List.html"
    
    #Update Local HTML Pages to not accidently DDoS Site while testing
    if(UpdateLocalFiles):
        page = requests.get(BaseURL + ListURL).content
        file = open(ListPage, "w", encoding="utf-8")                
        file.write(str(page))
        file.close()

    #Init BS4
    file = open(ListPage, "r", encoding="utf-8")
    soup = BeautifulSoup(file, 'html.parser')
    file.close()

    #Run BS4 On Local Page of Servants
    table = soup.find('table', { 'id': 'servants-new-list' })
    rows = table.find_all('tr')

    #Run through list with tqdm progress bar
    for row in tqdm(rows):
        if row.has_attr('class'):
            if row['class'] == ['servants-new-row']:
                title = row.find('span', {'class': 'servant-list-title'})
                if title.a['href'] not in BlackList:
                    ServantList.append(ServantInfo(title.a))

    for servant in ServantList:
        print(servant.name)
        print(servant.classTitle)
        print(servant.rarity)

if __name__ == "__main__":
    ScrapeServantList()