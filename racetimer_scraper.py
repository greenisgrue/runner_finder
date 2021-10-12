from datetime import datetime
import glob
import random
import string
from merge_data import Merge
import requests
import pandas as pd

from bs4 import BeautifulSoup
import urllib.request

from tqdm import tqdm

class ScrapeRacetimer:
    def __init__(self):
        print("hello")
        
        self.runner_df = pd.DataFrame(columns=["runner_id", "first_name", "last_name", "born", "club_id"])
        self.club_df = pd.DataFrame(columns=["club_id", "club_name"])
        self.race_data_df = pd.DataFrame(columns=["runner_id", "race_id", "place", "time"])
        self.race_df = pd.DataFrame(columns=["race_id", "race_name", "distance", "year"])

        try:
            f = open(f'master_files/club.csv')
            self.master_club_df = pd.read_csv(f'master_files/club.csv', encoding='utf-16')
            print("master club file opened")
        except IOError:
            print("Creating master club file")
            self.master_club_df = pd.DataFrame(columns=["club_id", "club_name"])
            self.master_club_df.to_csv(f'master_files/club.csv', encoding='utf-16', index = False)

        try:
            f = open(f'master_files/runner.csv')
            self.master_runner_df = pd.read_csv(f'master_files/runner.csv', encoding='utf-16')
            print("master runner file opened")
        except IOError:
            print("Creating master runner file")
            self.master_runner_df = pd.DataFrame(columns=["runner_id", "first_name", "last_name", "born", "club_id"])
            self.master_runner_df.to_csv(f'master_files/runner.csv', encoding='utf-16', index = False) 
        

    def get_race_data(self, race_class):
        mytds = self.soup.find("table", {"id": "top3-list"})
        
        mytrs = mytds.find_all('tr')
        
        for element in mytrs:
            full_name = element.find('a')
            if full_name:
                first_name = full_name.get_text().lower().strip().strip(',').split(' ', 1)[0]
                last_name = full_name.get_text().lower().strip().split(' ')[-1]
                last_name = last_name.replace(",", "")
                if len(last_name) == 0:
                    continue
            
                text_born = element.find("td", {"class": "yob_column"})
                text_born = text_born.text
                born = int(text_born)

                text_place = element.find("td", {"style": "width:2em;"})
                text_place = text_place.text

                race_time = element.find_all("td", {"style": "width:3em;"})
                if race_time[1]:
                    time = race_time[1].get_text().strip()
                    if len(time) == 7:
                        time = datetime.strptime(time, '%H:%M:%S').time()
                    else:
                        time = datetime.strptime(time, '%M:%S').time()
                else:
                    self.time = None

                club = element.find("td", {"class": "club_column"})
                club = club.get_text().strip().lower()
                club_split = club.split()
                club_id = ''.join(word[0].upper() for word in club_split) + '-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

                

    def iterate_pages(self, race_id, classes):
        for c in classes: 
            URL = f'https://www.racetimer.se/sv/race/resultlist/{race_id}?commit=Visa+resultat+%3E%3E&layout=marathon&page=1&per_page=25&race_id={race_id}&rc_id={c}'
            page = requests.get(URL)
            self.soup = BeautifulSoup(page.content, 'html.parser')
            pagination = self.soup.find('div', {'class': 'pagination'})
            pages = pagination.findAll(text=True)
            pages = [int(s) for s in pages if s.isdigit()]
            pages = [*range(1, pages[-1])]
            for page in tqdm(pages):
                URL = f'https://www.racetimer.se/sv/race/resultlist/{race_id}?commit=Visa+resultat+%3E%3E&layout=marathon&page={page}&per_page=25&race_id={race_id}&rc_id={c}'
                page = requests.get(URL)
                self.soup = BeautifulSoup(page.content, 'html.parser')
                
                race.get_race_data(c)

race = ScrapeRacetimer()
race.iterate_pages('4767', ['18437'])