import glob
import pandas as pd
import numpy as np

class Merge():
    def __init__(self, files):

        self.club_file = []
        self.runner_file = []
        self.race_data_file = []

    #path = "files_in_progress/*.csv"
    #for fname in glob.glob(path):
        for fname in files:
            if 'club' in fname:
                self.club_file = fname
            elif 'runner' in fname:
                self.runner_file = fname
            elif 'race_data' in fname:
                self.race_data_file = fname

    def merge_df(self):
        master_club_df = pd.read_csv(f'master_files/club.csv', encoding='utf-16')
        club_file = pd.read_csv(f'files_in_progress/{self.club_file}', encoding='utf-16')
        master_club_df = pd.concat([club_file, master_club_df])
        master_club_df.to_csv(f'master_files/club.csv', encoding="utf-16", index = False)  

        master_runner_df = pd.read_csv(f'master_files/runner.csv', encoding='utf-16')
        runner_file = pd.read_csv(f'files_in_progress/{self.runner_file}', encoding='utf-16')
        master_runner_df = pd.concat([runner_file, master_runner_df])
        master_runner_df.to_csv(f'master_files/runner.csv', encoding="utf-16", index = False) 

        merged_race_data_df = pd.read_csv(f'master_files/race_data.csv', encoding='utf-16')
        race_data_file = pd.read_csv(f'files_in_progress/{self.race_data_file}', encoding='utf-16')
        merged_race_data_df = pd.concat([race_data_file, merged_race_data_df])
        merged_race_data_df.to_csv(f'master_files/race_data.csv', encoding="utf-16", index = False)


        