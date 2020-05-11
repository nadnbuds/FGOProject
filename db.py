import json
from tqdm import tqdm
from bs4 import BeautifulSoup
from os import listdir
from dataclasses import dataclass

#Config Values
path_to_files = './scrapingData/'
output = './database/'
database = 'database.json'

@dataclass
class ServantStats:
    rarity: int = 0
    className: str = ""

class Servant:
    def __init__(self):
        self.name = ""
        self.stats = ServantStats()
        self.skill_cost = [{}] * 10
        self.ascension_cost = [{}] * 4

    def output(self):
        servant = {
            'Name': self.name,
            'Class': self.stats.className,
            'Rarity': self.stats.rarity,
            'AscensionCost': self.ascension_cost,
            'SkillCost' : self.skill_cost
        }

        return servant

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
        classTitle = FindFirstBottom(soup.find('span', {'class': 'class-title'}))
        rarity = FindFirstBottom(soup.find('span', {'class': 'class-rarity'}))
        servant.stats = ServantStats(rarity, classTitle)

def ScrapeTopSection(soup, servant):
    #Implement this later
    pass

def ScrapeStatus(soup, servant):
    #Just grab Ascension/Skill Materials for now
    ascension = []
    table = soup.find('table', {'id': 'ascension-materials-table'})
    rows = table.find_all('tr', {'class': 'ascension-row'})
    for item in rows:
        dic = {}
        #QP Cost Column
        cost = item.find('td', {'class': 'ascension-cost'})
        if len(cost.contents) > 0:
            dic['QP'] = cost.div['content']
        
        #Materials cost Column
        mats = item.find('td', {'class': 'ascension-materials'}).find_all('div')
        for mat in mats:
            if mat.has_attr('data-item'):
                dic[mat['data-item']] = mat['data-qty']
        ascension.append(dic)
    servant.ascension_cost = ascension

    skill = []
    table = soup.find('table', {'id': 'Skill-materials-table'})
    rows = table.find_all('tr', {'class': 'skill-row'})
    for item in rows:
        dic = {}
        #QP Cost Column
        cost = item.find('td', {'class': 'Skill-cost'})
        dic['QP'] = cost.string

        #Materials cost Column
        mats = item.find('td', {'class': 'Skill-materials'}).find_all('div')
        for mat in mats:
            if mat.has_attr('data-item'):
                dic[mat['data-item']] = mat['data-qty']
        skill.append(dic)
    servant.skill_cost = skill

def ScrapeServant(file):
    servant = Servant()
    
    #Init BS4
    soup = BeautifulSoup(file, 'html.parser')

    #Run BS4 On Local Page of Servant
    #Div SubHeader for Class Icon, Title, Rarity
    subheader = soup.find('div', {'id': 'servant-subheader'})
    ScrapeSubheader(subheader, servant)

    #Div Top Section for Servant Stats
    topsection = soup.find('div', {'id': 'servant-top-section-container'})
    ScrapeTopSection(topsection, servant)

    #Div Status for Skill/Np Info
    status = soup.find('div', {'id': 'status'})
    ScrapeStatus(status, servant)

    return servant

def process_db():
    servant_list = []
    #Populate db with scraped html pages
    for file in tqdm(listdir(path_to_files)):
        #Update for the new folder/icon duo
        with open(f'{path_to_files}{file}', 'r', encoding='UTF-8') as f:
            servant_list.append(ScrapeServant(f.read()).output())
    
    #Write the db
    with open(database, 'w') as db:
        json.dump(servant_list, db)

if __name__ == "__main__":
    process_db()