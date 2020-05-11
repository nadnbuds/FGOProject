import requests
import time
import os
from bs4 import BeautifulSoup
from tqdm import tqdm

#URL Links to scrape
base_url = 'https://gamepress.gg'
list_url = '/grandorder/servants'
path_to_files = "./scrapingData/"

#Blacklist Servants that aren't obtainable
blackList = [
    '/grandorder/servant/beast-iiil',
    '/grandorder/servant/solomon-grand-caster',
    '/grandorder/servant/goetia',
    '/grandorder/servant/tiamat',
    '/grandorder/servant/solomon-true',
    '/grandorder/servant/beast-iiir'
]

buffer_size = 1024

def scrape_html():
    page = requests.get(f'{base_url}{list_url}')
    soup = BeautifulSoup(page.content, 'html.parser')

    #Run BS4 On Local Page of Servants
    table = soup.find('table', { 'id': 'servants-new-list' })
    rows = table.find_all('tr')

    #Run through list with tqdm progress bar
    for row in tqdm(rows):
        if row.has_attr('class'):
            if row['class'] == ['servants-new-row']:
                link = row.find('span', {'class': 'servant-list-title'}).a['href']
                img = row.find('img', {'class': 'servant-icon'})['src']
                filename = link.split("/")[-1]
                if link not in blackList:
                    pathname = f'{path_to_files}{filename}'
                    #Make dir if not made
                    if not os.path.isdir(pathname):
                        os.makedirs(pathname)
                    #Cut off the get req and access direct image
                    try:
                        pos = img.index('?')
                        img = img[:pos]
                    except ValueError:
                        pass

                    #Define paths
                    ServantPage = f'{pathname}/{filename}.html'
                    ServantIcon = f'{pathname}/{filename}.{img.split(".")[-1]}'

                    #Get Image
                    img_url = f'{base_url}{img}'
                    response = requests.get(img_url, stream=True)
                    file_size = int(response.headers.get('Content-Length', 0))
                    progress = tqdm(response.iter_content(buffer_size), f"Downloading {filename}", total=file_size, disable=True, unit="B", unit_scale=True, unit_divisor=1024)
                    with open(ServantIcon, "wb") as f:
                        for data in progress:
                            f.write(data)
                            progress.update(len(data))
                        progress.close()

                    #Get Page
                    page = requests.get(f'{base_url}{link}')
                    with open(ServantPage, "wb") as f:
                        f.write(page.content)

                    #Sleep to not accidently DDOS
                    time.sleep(1)

if __name__ == "__main__":
    scrape_html()