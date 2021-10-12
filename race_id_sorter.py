from datetime import time
import glob
import pandas as pd
import numpy as np


def add_gender():
    path = "files_in_progress/*.csv"
    files_men = []
    files_women = []

    women = ["K15", "K30", "Women"]
    men = ["M15", "M30", "Men"]

    race_df = pd.read_csv('master_files/race.csv', encoding='utf-16')

    for index, row in race_df.iterrows(): 
        if any(x in row['race_name'] for x in women):
            files_women.append(row['race_id'])
        elif any(x in row['race_name'] for x in men):
            files_men.append(row['race_id'])

    files_women = list(map(str, files_women))
    files_men = list(map(str, files_men))

    path = "files_in_progress/*.csv"
    for fname in glob.glob(path):
        f = fname[18:]
        f = f.split('_')
        print(f)
        if f[0] in files_women and f[2] == "runner.csv":
            df = pd.read_csv(fname)
            df['gender'] = 'W'
            df.to_csv(f'files_in_progress/{f[0]}_{f[1]}_runner.csv', encoding='utf-16')
        elif f[0] in files_men and f[2] == "runner.csv":
            df = pd.read_csv(fname)
            df['gender'] = 'M'   
            df.to_csv(f'files_in_progress/{f[0]}_{f[1]}_runner.csv', encoding='utf-16')

def get_race_by_type(race_type):
    df = pd.read_csv(f'old_files/race/{race_type}_race.csv', encoding='utf-16')
    id_list = []
    for index, row in df.iterrows():
        id_list.append(row['race_id'])

    id_list = list(map(str, id_list))
    print(id_list)

#get_race_by_type("LL30")
#add_gender()



   









