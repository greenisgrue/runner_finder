import requests
import random
import string
import glob
import re

from tqdm import tqdm
from datetime import datetime

from bs4 import BeautifulSoup
import pandas as pd

from merge_data import Merge

class Scrape:
    def __init__(self):
        print("hello")
        # Hämtar resultatsidan och sparar soup objekt
        URL = 'https://results.lidingoloppet.se/result?eventgroupid=1&_ga=2.87176347.207120095.1619814767-527693088.1619814766'
        page = requests.get(URL)
        self.soup = BeautifulSoup(page.content, 'html.parser')

        # Skapar dataframes för de tabeller som finns i databasen
        self.update_files()
        self.race_df = pd.DataFrame(columns=["race_id", "race_name", "distance", "year"])

    def update_files(self):
        # Nollställer data frames
        self.runner_df = pd.DataFrame(columns=["runner_id", "first_name", "last_name", "born", "club_id", "gender"])
        self.club_df = pd.DataFrame(columns=["club_id", "club_name"])
        self.race_data_df = pd.DataFrame(columns=["runner_id", "race_id", "place", "time"])

        # Återöppnar master files med ny data eller skapar nya om de inte finns
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

        try:
            f = open(f'master_files/race_data.csv')
            master_race_data_df = pd.read_csv('master_files/race_data.csv', encoding='utf-16')
        except IOError:
            print("Creating master file")
            master_race_data_df = pd.DataFrame(columns=["runner_id", "race_id", "place", "time"])
            master_race_data_df.to_csv(f'master_files/race_data.csv', encoding='utf-16', index = False)

        
    def get_races(self, edition, distance):
        women = ["K15", "K30", "Women"]
        men = ["M15", "M30", "Men"]
        # Kollar om loppen är hämtade
        path = f"old_files/*.csv"
        files = []
        for fname in glob.glob(path):
            files.append(fname)
        if [match for match in files if f'LL{distance}_race.csv' in match]:
            print("Race names fetched")
            self.race_df = pd.read_csv(f'old_files/LL{distance}_race.csv', encoding='utf-16')

        # Annars hämtas de lopp som finns för varje år
        else:
            print(f"Fetching races: {edition}")
            results = self.soup.find(id='Year')
            years = results.find_all('option')
            for year in tqdm(years):
                if len(year) != 0:
                    URL = f'https://results.lidingoloppet.se/Result?EventGroupId=1&Year={year.text}&CompetitionId=&ClassId=&FirstName=&LastName=&Club=&NationalityCountryId=&StartNumber=&AgeClass=&BirthYearFrom=&BirthYearTo=&PlaceFrom=&PlaceTo=&Search=S%C3%B6k+resultat'
                    page = requests.get(URL)
                    self.soup = BeautifulSoup(page.content, 'html.parser')
                    self.soup = self.soup.find(id='ClassId')
                    self.race_id = self.soup.findAll(lambda tag:tag.name=="option" and edition in tag.text)
                    distance = int(distance)
                    for item in self.race_id:
                        if any(x in item.text for x in women):
                            gender = 'W'
                        elif any(x in item.text for x in men):
                            gender = 'M'
                        self.race_df = self.race_df.append({'race_id':item['value'], 'race_name':item.text, 'distance':int(distance), 'year':int(year.text), 'gender': gender}, ignore_index=True)

        # Lägger till datan i race master file
        try:
            f = open(f'master_files/race.csv')
            master_race_data_df = pd.read_csv('master_files/race.csv', encoding='utf-16')
        except IOError:
            print("Creating master file")
            master_race_data_df = pd.DataFrame(columns=["race_id", "race_name", "distance", "year"])
            master_race_data_df.to_csv(f'master_files/race.csv', encoding='utf-16', index = False)

        self.race_df.to_csv(f'old_files/LL{distance}_race.csv', encoding="utf-16", index = False)
        master_race_df = pd.read_csv(f'master_files/race.csv', encoding='utf-16')
        master_race_df = pd.concat([self.race_df, master_race_df]).drop_duplicates()
        master_race_df.to_csv(f'master_files/race.csv', encoding="utf-16", index = False)
        print('Done fetching race names')
            

    def get_race_data(self, c_id, gender):
        mydivs = self.soup.find_all("div", {"class": "border-bottom"})
        for element in mydivs:
            full_name = element.find('a', {'class': 'history'})
            self.first_name = full_name.get_text().lower().strip().strip(',').split(' ', 1)[0]
            self.last_name = full_name.get_text().lower().strip().split(' ')[-1]
            self.last_name = self.last_name.replace(",", "")
            if len(self.last_name) == 0:
                continue
            
            text_born = element.get_text().strip()
            for t in text_born.split():
                if len(t) < 7 and t.endswith('.'):
                    self.place = ''.join(filter(str.isdigit, t))
                    if self.place:
                        self.place = int(self.place)
                if len(t) == 3 and t.startswith('-'):
                    self.born = t.strip('-')
                    self.born = int(self.born)
                    if self.born > 5:
                        self.born = self.born + 1900
                    else:
                        self.born = self.born + 2000
                    break

            race_time = element.find('div', {'class': 'col-sm-2'})  
            if race_time and re.search("([0-9][0-9]\.[0-9][0-9]\.[0-9][0-9])", race_time.get_text().strip()) and len(race_time.get_text().strip()) == 8:
                self.time = race_time.get_text().strip()
                self.time = datetime.strptime(self.time, '%H.%M.%S').time()
            else:
                self.time = None

            club = element.find('div', {'class': 'col-9'})
            self.club = club.get_text().strip().lower()
            club_split = self.club.split()
            self.club_id = ''.join(word[0].upper() for word in club_split) + '-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            
            if not (self.club in self.club_df.values) and not (self.club in self.master_club_df.values) and len(self.club) > 0:
                self.club_df = self.club_df.append({'club_id':self.club_id, 'club_name':self.club}, ignore_index=True)
            elif len(self.club) > 0: 
                stored_club = self.master_club_df.loc[self.master_club_df['club_name'] == self.club]
                if stored_club.empty:
                    stored_club = self.club_df.loc[self.club_df['club_name'] == self.club]
                self.club_id = stored_club.iloc[0]['club_id']
            else:
                self.club_id = 'NOCL'

            if ((self.master_runner_df['first_name'] == self.first_name) & (self.master_runner_df['last_name'] == self.last_name) & (self.master_runner_df['born'] == self.born)).any() == False and ((self.runner_df['first_name'] == self.first_name) & (self.runner_df['last_name'] == self.last_name) & (self.runner_df['born'] == self.born)).any() == False:
                 self.born = str(self.born)
                 self.runner_id = self.first_name[0] + self.last_name[0] + self.born + '-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) 
                 self.born = int(self.born)
                 self.runner_df = self.runner_df.append({'runner_id':self.runner_id, 'first_name':self.first_name, 'last_name':self.last_name, 'gender':gender, 'born':self.born,'club_id':self.club_id}, ignore_index=True)
                 self.race_data_df = self.race_data_df.append({'runner_id':self.runner_id, 'race_id':c_id, 'place':self.place, 'time':self.time}, ignore_index=True)  
            else:
                master = self.master_runner_df.loc[(self.master_runner_df['first_name'] == self.first_name) & (self.master_runner_df['last_name'] == self.last_name) & (self.master_runner_df['born'] == self.born)]
                current = self.runner_df.loc[(self.runner_df['first_name'] == self.first_name) & (self.runner_df['last_name'] == self.last_name) & (self.runner_df['born'] == self.born)]
                master = master.append(current)
                has_run = False
                for index, row in master.iterrows():
                    if row['club_id'].startswith(self.club_id[:2]):
                        runner = row
                        has_run = True
                if has_run:    
                    self.race_data_df = self.race_data_df.append({'runner_id':runner['runner_id'], 'race_id':c_id, 'place':self.place, 'time':self.time}, ignore_index=True)  
                else:
                    self.born = str(self.born)
                    self.runner_id = self.first_name[0] + self.last_name[0] + self.born + '-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) 
                    self.born = int(self.born)
                    self.runner_df = self.runner_df.append({'runner_id':self.runner_id, 'first_name':self.first_name, 'last_name':self.last_name, 'gender':gender, 'born':self.born,'club_id':self.club_id}, ignore_index=True)
                    self.race_data_df = self.race_data_df.append({'runner_id':self.runner_id, 'race_id':c_id, 'place':self.place, 'time':self.time}, ignore_index=True)  


    def iterate_pages(self):
        self.update_files()
        pages = [*range(1,200)]
        path = "files_in_progress/*.csv"
        files = []
        for fname in glob.glob(path):
            files.append(fname)
        for index, row in self.race_df.iterrows(): 
            if not [match for match in files if str(row['race_id']) in match]:
                print(row['race_name'])
                gender = row['gender']
                self.year = row['year']
                print(self.year)
                race_id = row['race_id']
                for page in tqdm(pages):
                    URL = f'https://results.lidingoloppet.se/Result?EventGroupId=1&Year={self.year}&CompetitionId=&ClassId={race_id}&FirstName=&LastName=&Club=&NationalityCountryId=&StartNumber=&AgeClass=&BirthYearFrom=&BirthYearTo=&PlaceFrom=&PlaceTo=&Search=S%C3%B6k+resultat&x=2&PageNo={page}'
                    page = requests.get(URL)
                    self.soup = BeautifulSoup(page.content, 'html.parser')
                    if not (self.soup.find('div', {'class': 'competitionrow'})):
                        break

                    self.get_race_data(race_id, gender)
            
                self.runner_df.to_csv(f'files_in_progress/{race_id}_{self.year}_runner.csv', encoding="utf-16", index = False)  
                self.club_df.to_csv(f'files_in_progress/{race_id}_{self.year}_club.csv', encoding="utf-16", index = False)  
                self.race_data_df.to_csv(f'files_in_progress/{race_id}_{self.year}_race_data.csv', encoding="utf-16", index = False)

                prep_merge = Merge([f'{race_id}_{self.year}_runner.csv', f'{race_id}_{self.year}_club.csv', f'{race_id}_{self.year}_race_data.csv'])
                prep_merge.merge_df()
                self.update_files()






