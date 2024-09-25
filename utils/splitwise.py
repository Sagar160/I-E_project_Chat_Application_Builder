import os
import json
import time
from datetime import datetime
# from utils import read_json, write_json
from gemini import call_gemini


def read_json(file_path):
    """
    Read JSON data from a file.

    Parameters:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The JSON data as a dictionary.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def write_json(data, file_path):
    """
    Write JSON data to a file.

    Parameters:
        data (dict): The JSON data to write.
        file_path (str): The path to write the JSON file.
    """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
        

def get_time():
    # Getting the current date and time
    dt = datetime.now()
    ts = datetime.timestamp(dt)
    return ts

def calculate_net_amount(agentname, expense_name='None'):
    try:
        data              =  read_json(f'/home/spanwar/Documents/collage/projects/chatbot_v2/data/splitwise/{agentname}_data.json')
        expense_name_dict = read_json(f'/home/spanwar/Documents/collage/projects/chatbot_v2/data/splitwise/{agentname}_expense_id.json')
    except:
        return 'no data found'
    # try:
    if expense_name=='None':
        expense_name = max(expense_name_dict, key=expense_name_dict.get)
        key          = expense_name_dict[expense_name]   
        print(f'expense name not specified, so calculating last expenses\nexpense name: {expense_name}')
    elif expense_name=='last':
        expense_name = max(expense_name_dict, key=expense_name_dict.get)
        key          = expense_name_dict[expense_name]   
        print(f'last expense name: {expense_name}')
    else:
        key = expense_name_dict[expense_name]
        print(f'expense name: {expense_name}')
    # except:
    #     print('not found')
    #     return

    transactions = data[str(key)]
    net_amounts = {}
    
    # Iterate through each transaction
    for transaction in transactions:
        giver, receiver, amount = transaction
        amount = int(amount)
        
        # Update net amount for the giver and receiver
        net_amounts[giver] = net_amounts.get(giver, 0) - amount
        net_amounts[receiver] = net_amounts.get(receiver, 0) + amount
    
    print(f'Net Balance of the expenses\n{net_amounts}')

    return f'Net Balance of the expense name:{expense_name}\n{str(net_amounts)}'

def splitwise(_from, _to, money, agentname, expense_name='None'):
    try:
        data              =  read_json(f'/home/spanwar/Documents/collage/projects/chatbot_v2/data/splitwise/{agentname}_data.json')
        expense_name_dict = read_json(f'/home/spanwar/Documents/collage/projects/chatbot_v2/data/splitwise/{agentname}_expense_id.json')
    except:
        data = {}
        expense_name_dict = {}
        
    if expense_name=='None':
        print('creating new expense')
        key                         = get_time()
        expense_name_dict[str(key)] = key
        data[key]                   = [[_from, _to, money]]
    elif expense_name=='last':
        print(f'logging to expense name: {expense_name}')
        try:
            expense_name = max(expense_name_dict, key=expense_name_dict.get)
            key          = expense_name_dict[expense_name]
            data[str(key)].append([_from, _to, money])
        except:
            return 'no last expense'
    else:
        print(f'logging to expense name: {expense_name}')
        
        if expense_name in expense_name_dict:
            key = expense_name_dict[expense_name]
            data[str(key)].append([_from, _to, money])
        else:
            key                             = get_time()
            expense_name_dict[expense_name] = key
            data[str(key)]                       = [[_from, _to, money]]

    # print(expense_name_dict)
    # print(data)
    write_json(expense_name_dict, f'/home/spanwar/Documents/collage/projects/chatbot_v2/data/splitwise/{agentname}_expense_id.json')
    write_json(data, f'/home/spanwar/Documents/collage/projects/chatbot_v2/data/splitwise/{agentname}_data.json')
    print(f"Done: add {money} to {_to} paid by {_from}")

    return f"Done: add {money} to {_to} paid by {_from}"

def response(query, agentname):
    prompt = '''

Here's how to use the functions:

splitwise(_from, _to, money, expense_name=None) 
Use this function to record new transactions. Provide the payer (_from), recipient (_to), and the amount of money exchanged. 
Optionally, you can specify an expense_name to categorize the transaction if expense_name is last, it will add to expense name.

calculate_net_amount(expense_name=None): Use this function to calculate the net amounts owed or owed by each individual. 
If an expense_name is provided, the function will calculate net amounts based on transactions associated with that expense name. 
If no expense_name is specified, it will default to the last recorded expense.

example 1: I(sagar) have paid rena 20 euro. add this to last expense.
ans: {"splitwise":{ "from": "sagar", "to":"rena", "money":"20", "expense_name": "last"}}
example 2: ekta give me (liu) 5 euro.
ans: {"splitwise":{"from": "ekta", "to":"liu", "money":"5", "expense_name": "None"}}
example 3: jack have taken 2 euro from pio. add this to expense name ettp tt
ans: {"splitwise":{"from": "pio", "to":"jack", "money":"2", "expense_name": "ettp tt"}}
example: calculate the money that have to paid to each other.
ans: {"calculate_net_amount":{"expense_name": "None"}}
all output in dictionary form.
####################

'''
    prompt = prompt + query
    output = call_gemini(prompt)
    _dict = json.loads(output)
    print(_dict)
    result = ''
    for key in _dict:
        if key=='splitwise':
            result = result + splitwise(_dict[key]['from'], _dict[key]['to'], _dict[key]['money'], agentname, _dict[key]['expense_name'])
        if key=='calculate_net_amount':
            result = result + calculate_net_amount(agentname, _dict[key]['expense_name'])

    return result