# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 18:04:32 2022

@author: Zerui Mu
"""

import os
from typing import Dict
import pandas as pd

from predicament.utils.config import STUDY_DATA_FOLDER, E4_LOCAL_DIRPATHS, E4_buffer
from Ray.Event_details import Event_time_details

E4_file_names = ['ACC', 'BVP', 'EDA', 'HR', 'IBI', 'TEMP'] # physiological data, tags.csv not included

class E4_data_class(object):
    def __init__(self, participant, data) -> None:
        self.ID = participant
        self.E4_data = data # each file including: start_time, Hz, data
        self.event_details = None # need to be set after init

    def set_event_details(self, event_details: Event_time_details):
        self.event_details = event_details

    def _get_event_period_by_name(self, file_name, event_name):
        exp_start_time = float(self.E4_data[file_name]['time'])
        event_start = self.event_details.events_info[event_name]["start"]
        event_end = self.event_details.events_info[event_name]["end"]
        return event_start - exp_start_time + E4_buffer, event_end - exp_start_time - E4_buffer

    def get_E4_by_filename_and_event(self, file_name, event_name):
        start, end = self._get_event_period_by_name(file_name, event_name)
        Hz = self.E4_data[file_name]['Hz']
        return self.E4_data[file_name]['data'].iloc[int(start * Hz): int(end * Hz),:]


def read_all_E4_files() -> Dict[str, E4_data_class]:
    return {participant: read_E4_file(participant) for participant in E4_LOCAL_DIRPATHS.keys()}

def read_E4_file(participant) -> E4_data_class:
    try:
        if participant not in E4_LOCAL_DIRPATHS.keys():
            raise IndexError("The given participant ({}) is not included".format(participant))
    except RuntimeError as e:
        print("Error:", e)
    data = {}
    for file_name in E4_file_names:
        E4_file_path = os.path.join(STUDY_DATA_FOLDER, E4_LOCAL_DIRPATHS[participant], file_name + '.csv')
        E4_file = pd.read_csv(E4_file_path)
        data[file_name] = {
            'time': E4_file.columns[0],
            'Hz': E4_file.iloc[0,0], # The first row is the sample rate expressed in Hz.
            'data': E4_file[1:].reset_index(drop = True)
        }
    E4_part_data = E4_data_class(participant, data)
    print("Successfully loaded {} E4 file (physiological data)".format(participant))
    return E4_part_data
    
