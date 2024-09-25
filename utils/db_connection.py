import pandas as pd
from sqlite3 import connect
import sys
import os
import numpy as np
import base64
import io
from PIL import Image
from gemini import call_gemini

sys.path.append('/home/spanwar/Documents/collage/projects/chatbot_v2/utils')
_dir = '/home/spanwar/Documents/collage/projects/chatbot_v2/data/cloth_data/archive'

def read_data_from_path():
    df = pd.read_csv(os.path.join(_dir, 'images.csv'))
    df['rating'] = np.random.rand(len(df))
    df['rating'] = df['rating'].apply(lambda x: round(x, 2))
    df['price']  = np.random.randint(4, 50, len(df))
    return df

def pil_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    encoded_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return encoded_string

def get_image_path(image_id):
    image_path = os.path.join(_dir, 'images_compressed', image_id+'.jpg')
    pil_image = Image.open(image_path)
    return pil_to_base64(pil_image)

def create_sql_prompt(data, data_info, column_info, display_info, data_name):
    # print(column_info)
    prompt = 'SQL dataset information: ' + data_info
    prompt = '\nSQL dataset name: ' + data_name
    prompt = prompt + '\n#column information#\n'
    prompt = prompt + 'column names in SQL dataset: ' + str(list(column_info.keys())) + '\ncolumn description\n'
    for col in column_info:
        col_prompt = str(col) + ': '
        col_info = column_info[col]
        col_prompt = col_prompt + str(col_info['description'])
        if col_info['is_tag']:
            if len(data[col].unique())<25:
                col_prompt = col_prompt + ' This column have few tags such as ' + str(data[col].unique()).replace('\n', '')
        prompt = prompt + col_prompt + '\n'

    prompt = prompt + f'\nIn SQL query select the following columns: {display_info}\n'
    prompt = prompt + '##########\nknowing above information create a sql query for below question. Please return the only sql querry.\n'
    return prompt

def creating_sql_querry(prompt, querry):
    return call_gemini(prompt + querry)

def response_to_querry(data, dataname, data_info, column_info, display_info, querry):
    text_data = []
    image_data = []
    
    # create_sql_data(data, dataname)
    conn = connect(':memory:')
    data.to_sql(name=dataname, con=conn)
    prompt = create_sql_prompt(data, data_info, column_info, display_info, dataname)
    sql_querry = creating_sql_querry(prompt, querry)
    sql_querry = sql_querry.replace('```', '').replace('sql', '')
    sub_data = pd.read_sql(sql_querry, conn)
    print(sub_data)
    print(sql_querry)
    for index, row in sub_data.iterrows():
        columns = list(sub_data.columns)
        text = ''
        for col in columns:
            if column_info[col]['is_image']:
                image_data.append(get_image_path(row[col]))
            else:
                text = text + '<br>' +  f'{col}: {row[col]}'
        text_data.append(text)
    
    return {"texts": text_data, "images": image_data}

def database_info():
    data_info   = '''It is the dataset contain the information about various wearable products.'''
    column_info = {'image': {'description': 'Column contain Image ids', 'is_tag': False, 'is_image': True}, 
                'sender_id': {'description': 'contain the sender id, not useful', 'is_tag': False, 'is_image': False},
                'label': {'description': 'contain various important label about item.', 'is_tag': True, 'is_image': False},
                'kids': {'description': 'contain the label is belong to kid or not,', 'is_tag': True, 'is_image': False},
                'rating': {'description': 'contain the rating of items,', 'is_tag': False, 'is_image': False},
                'price': {'description': 'contain the price of items,', 'is_tag': False, 'is_image': False}}
    display_info = ['label', 'kids', 'rating', 'price', 'image']
    
    return data_info, column_info, display_info

def db_response(querry):
    data_info, column_info, display_info = database_info()
    df = read_data_from_path()
    return response_to_querry(df, 
                            'wearable_data', 
                            data_info, 
                            column_info, 
                            display_info, querry)

