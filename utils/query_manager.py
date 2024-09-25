#!/usr/bin/env python
# coding: utf-8

# # Imports 
from gemini import call_gemini

def query_manager(query):
    prompt = '''
Your a bot that help us in break down query into instructions. 
Currently we can answer two type of query:
1. question and answer: qna
2. checking the schedule: schedule
3. manage money and record transaction: splitwise
Examples:
query: Can you please help me with what is the business model?
Answer like this: {"qna": "Can you please help me with what is the business model?"}
query: what is the schedule of today class?
Answer: {"schedule": "what is the schedule of today class?"}
query: jack have taken 2 euro from pio. add this to expense name ettp tt
Answer: {"splitwise": "jack have taken 2 euro from pio. add this to expense name ettp tt"}
query: calculate the money that have to paid to each other.
Answer: {"splitwise": "calculate the money that have to paid to each other"}
All answer in dictionory form.
######################

    '''
    return call_gemini(prompt + query)





