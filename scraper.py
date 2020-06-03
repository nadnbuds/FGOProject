import os
import time
import requests
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tqdm import tqdm

#Globals
BUFFER_SIZE = 1024

#URL Links to scrape
BASE_URL = 'https://gamepress.gg'
CE_LIST_URL = '/grandorder/craft-essences'
TAGS_LIST_URL = '/grandorder/tags'
SERVANT_LIST_URL = '/grandorder/servants'
MATERIALS_LIST_URL = '/grandorder/materials'
CLASS_SKILL_LIST_URL = '/grandorder/class-skills'
SERVANT_SKILL_LIST_URL = '/grandorder/servant-skills'
PATH_TO_FILES = "./scraping_data/"

#Blacklist Servants that aren't obtainable
BLACKLIST = [
    '/grandorder/servant/beast-iiil',
    '/grandorder/servant/solomon-grand-caster',
    '/grandorder/servant/goetia',
    '/grandorder/servant/tiamat',
    '/grandorder/servant/solomon-true',
    '/grandorder/servant/beast-iiir'
]


def download_page(url, filename):
    page = requests.get(url)
    with open(filename, "wb") as f:
        f.write(page.content)


def download_image(url, filename):
    response = requests.get(url, stream=True)
    file_size = int(response.headers.get('Content-Length', 0))

    progress = tqdm(
        response.iter_content(BUFFER_SIZE), 
        f"Downloading {filename}",
        total=file_size,
        disable=True,
        unit="B",
        unit_scale=True,
        unit_divisor=1024)

    with open(filename, "wb") as f:
        for data in progress:
            f.write(data)
            progress.update(len(data))
        progress.close()


def scrape_servant_list(page):
    #Run BS4 to find servant list
    table = page.find('table', {'id':'servants-new-list'})
    rows = table.find_all('tr')

    directory = f'{PATH_TO_FILES}/servants/'
    #Make dir if not made
    if not os.path.isdir(directory):
        os.makedirs(directory)

    #Run through list with tqdm progress bar
    for row in tqdm(rows, desc='Servants'):
        if row.has_attr('class'):
            if 'servants-new-row' in row['class']:
                servant = row.find('span', {'class':'servant-list-title'})
                link = servant.a['href']
                img = row.find('img', {'class':'servant-icon'})['src']
                filename = link.split('/')[-1]
                filename = str.replace(filename, '-', '_')
                if link not in BLACKLIST:
                    pathname = f'{directory}{filename}'
                    #Make dir if not made
                    if not os.path.isdir(pathname):
                        os.makedirs(pathname)
                    #Cut off the 'get' req and access direct image
                    try:
                        pos = img.index('?')
                        img = img[:pos]
                    except ValueError:
                        pass
                    
                    page_link = f'{BASE_URL}{link}'
                    img_link = f'{BASE_URL}{img}'

                    #Define paths
                    page_file = f'{pathname}/page.html'
                    img_file = f'{pathname}/icon.{img.split(".")[-1]}'

                    download_page(page_link, page_file)
                    if os.path.exists(img_file) is not True:
                        download_image(img_link, img_file)


def scrape_craft_essence_list(page):
    #Run BS4 to find CE list
    table = page.find('table', {'id':'craft-essences-new-list'})
    rows = table.find_all('tr')

    directory = f'{PATH_TO_FILES}/craft_essences/'
    #Make dir if not made
    if not os.path.isdir(directory):
        os.makedirs(directory)

    #Run through list with tqdm progress bar
    for row in tqdm(rows, desc='Craft Essence'):
        if row.has_attr('class'):
            if 'craft-essences-new-row' in row['class']:
                ce = row.find('div', {'class':'essence-list-row-left'})
                link = ce.a['href']
                img = ce.a.img['src']
                filename = link.split('/')[-1]
                filename = str.replace(filename, '-', '_')
                pathname = f'{directory}{filename}'
                #Make dir if not made
                if not os.path.isdir(pathname):
                    os.makedirs(pathname)
                #Cut off the 'get' req and access direct image
                try:
                    pos = img.index('?')
                    img = img[:pos]
                except ValueError:
                    pass
                
                page_link = f'{BASE_URL}{link}'
                img_link = f'{BASE_URL}{img}'

                #Define paths
                page_file = f'{pathname}/page.html'
                img_file = f'{pathname}/icon.{img.split(".")[-1]}'

                if os.path.exists(page_file) is not True:
                    download_page(page_link, page_file)
                if os.path.exists(img_file) is not True:
                    download_image(img_link, img_file)


def scrape_materials_list(page):
    #Run BS4 to find material list of tables
    article = page.find('article', {'about':MATERIALS_LIST_URL})
    divContainer = article.find('div', {'class':'view-content'})
    tables = divContainer.find_all('table')

    directory = f'{PATH_TO_FILES}/materials/'
    #Make dir if not made
    if not os.path.isdir(directory):
        os.makedirs(directory)

    #Run through list of tables with tqdm progress bar
    for table in tqdm(tables, desc='Materials', position=0):
        title = table.find('h2', {'class':'main-title'}).text
        text = str.replace(title, ' ', '_').lower()
        category = f'{directory}/{text}/'
        if not os.path.isdir(category):
            os.makedirs(category)
        
        rows = table.find_all('tr')
        for row in tqdm(rows, desc=f'{title}', position=1, leave=False):
            if row.has_attr('class'):
                if 'materials-row' in row['class']:
                    material = row.find('a')
                    link = material['href']
                    img = material.img['src']
                    filename = link.split('/')[-1]
                    filename = str.replace(filename, '-', '_')
                    pathname = f'{category}{filename}'
                    #Make dir if not made
                    if not os.path.isdir(pathname):
                        os.makedirs(pathname)
                    #Cut off the get req and access direct image
                    try:
                        pos = img.index('?')
                        img = img[:pos]
                    except ValueError:
                        pass
                    
                    page_link = f'{BASE_URL}{link}'
                    img_link = f'{BASE_URL}{img}'

                    #Define paths
                    page_file = f'{pathname}/page.html'
                    img_file = f'{pathname}/icon.{img.split(".")[-1]}'

                    #No need to download pages for materials atm
                        #download_page(page_link, page_file)
                    if os.path.exists(img_file) is not True:
                        download_image(img_link, img_file)


def scrape_class_skills_list(page):
    #Run BS4 to find class skill list
    article = page.find('article', {'about':CLASS_SKILL_LIST_URL})
    table = article.find('table', {'id':'sort-table'}).tbody
    rows = table.find_all('tr')

    icons = f'{PATH_TO_FILES}/icons/'
    directory = f'{PATH_TO_FILES}/class_skills/'
    #Make dir if not made
    if not os.path.isdir(directory):
        os.makedirs(directory)
    if not os.path.isdir(icons):
        os.makedirs(icons)

    #Run through list with tqdm progress bar
    for row in tqdm(rows, desc='Class Skills'):
        link = row.find('a')['href']
        img = row.find('img')['src']
        filename = link.split('/')[-1]
        filename = str.replace(filename, '-', '_')
        pathname = f'{directory}{filename}'
        #Make dir if not made
        if not os.path.isdir(pathname):
            os.makedirs(pathname)
        #Cut off the 'get' req and access direct image
        try:
            pos = img.index('?')
            img = img[:pos]
        except ValueError:
            pass
        
        page_link = f'{BASE_URL}{link}'
        img_link = f'{BASE_URL}{img}'

        #Define paths
        page_file = f'{pathname}/page.html'
        img_file = f'{icons}/{img.split("/")[-1]}'

        if os.path.exists(page_file) is not True:
            download_page(page_link, page_file)
        if os.path.exists(img_file) is not True:
            download_image(img_link, img_file)


def scrape_servant_skills_list(page):
    #Run BS4 to find class skill list
    article = page.find('article', {'about':SERVANT_SKILL_LIST_URL})
    container = article.find('div', {'id':'load-content'})
    tables = container.find_all('table')

    icons = f'{PATH_TO_FILES}/icons'
    directory = f'{PATH_TO_FILES}/servant_skills/'
    #Make dir if not made
    if not os.path.isdir(directory):
        os.makedirs(directory)
    if not os.path.isdir(icons):
        os.makedirs(icons)

    #Run through list with tqdm progress bar
    for table in tqdm(tables, desc='Servant Skills', position=0):
        rows = table.tbody.find_all('tr')
        desc = ''
        if table.caption is not None:
            desc = table.caption.text
        else:
            desc = 'Other'

        for row in tqdm(rows, desc=f'{desc}', position=1, leave=False):
            link = row.find('a')['href']
            img = row.find('img')['src']
            filename = link.split('/')[-1]
            filename = str.replace(filename, '-', '_')
            pathname = f'{directory}{filename}'
            #Make dir if not made
            if not os.path.isdir(pathname):
                os.makedirs(pathname)
            #Cut off the 'get' req and access direct image
            try:
                pos = img.index('?')
                img = img[:pos]
            except ValueError:
                pass
            
            page_link = f'{BASE_URL}{link}'
            img_link = f'{BASE_URL}{img}'

            #Define paths
            page_file = f'{pathname}/page.html'
            img_file = f'{icons}/{img.split("/")[-1]}'

            if os.path.exists(page_file) is not True:
                download_page(page_link, page_file)
            if os.path.exists(img_file) is not True:
                download_image(img_link, img_file)


def main():
    updateServants = False
    if len(sys.argv) > 1:
        input = sys.argv[1].lower()
        updateServants = (input == 'update')
    
    if updateServants:
        page = requests.get(f'{BASE_URL}{SERVANT_LIST_URL}')
        soup = BeautifulSoup(page.content, 'html.parser')
        scrape_servant_list(soup)
    
    page = requests.get(f'{BASE_URL}{CE_LIST_URL}')
    soup = BeautifulSoup(page.content, 'html.parser')
    scrape_craft_essence_list(soup)
    
    page = requests.get(f'{BASE_URL}{MATERIALS_LIST_URL}')
    soup = BeautifulSoup(page.content, 'html.parser')
    scrape_materials_list(soup)
    
    page = requests.get(f'{BASE_URL}{CLASS_SKILL_LIST_URL}')
    soup = BeautifulSoup(page.content, 'html.parser')
    scrape_class_skills_list(soup)
    
    browser = webdriver.Firefox()
    browser.get(f'{BASE_URL}{SERVANT_SKILL_LIST_URL}')
    try:
        WebDriverWait(browser, 60).until(
            EC.presence_of_element_located((By.ID, "Critical-Crit Damage Up"))
        )
    except:
        browser.close()

    page = browser.page_source
    browser.close()
    soup = BeautifulSoup(page, 'html.parser')
    scrape_servant_skills_list(soup)

if __name__ == '__main__':
    main()
