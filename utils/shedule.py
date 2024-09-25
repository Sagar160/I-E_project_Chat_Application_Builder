#!/usr/bin/env python
# coding: utf-8

# # Imports 
import os
import json
from datetime import datetime
from utils import read_json
from gemini import call_gemini

def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def save_shedule(_dict, botname):
    path = f'/home/spanwar/Documents/collage/projects/chatbot_v2/data/schedule/{botname}.json'
    write_json(path, _dict)
    
# # Addition
def shedule(day, botname):
    day = day.lower()
    day_to_number = {
            0: "monday",
            1: "tuesday",
            2: "wednesday",
            3: "thursday",
            4: "friday",
            5: "Saturday",
            6: "sunday"
            }
    if day=='today':
        dt = datetime.now()  
        day = day_to_number[dt.weekday()]

    path = f'/home/spanwar/Documents/collage/projects/chatbot_v2/data/schedule/{botname}.json'
    day_to_time_range = read_json(path)

    # day_to_time_range = {
    #         "monday": "12:00 - 14:00",
    #         "tuesday": "14:00 - 16:00",
    #         "wednesday": "16:00 - 18:00",
    #         "thursday": "18:00 - 20:00",
    #         "friday": "20:00 - 22:00",
    #         "saturday": "10:00 - 12:00",
    #         "sunday": "10:00 - 12:00"
    #     }

    return f'{day_to_time_range[day]}'


def response(query, botname):
    prompt = '''function: schedule
It is a function return in python that return the daily schedule. Please help us find the variables for the function from the sentences. We have to pass 
one variable that is day. Contain the information of what day of the week.

These are few example how you have to response and try to find variable form the sntence that are useful for our function.
Example 1. Give me today schedule?
ans {"day": "today"}
example 2. What is schedule of monday?
ans {"day": "monday"}
all output in dictionary form.
##########

'''
    prompt = prompt + query
    text = call_gemini(prompt)
    data = json.loads(text)
    return shedule(data['day'], botname)