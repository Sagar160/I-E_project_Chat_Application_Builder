#!/usr/bin/env python
# coding: utf-8

# # Imports
import os
import json
import numpy as np
from pypdf import PdfReader 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from gemini import call_gemini



# # Tools

# ## QnA
def find_files(path):
    '''
    find files from the directory
    '''
    if os.path.exists(path):
        if os.path.isdir(path):
            files = []
            for root, _, filenames in os.walk(path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            return files
        elif os.path.isfile(path):
            return [path]
        else:
            raise Exception('Unable to read directory')
    else:
        raise Exception('Path does not exsts')


def find_file_ext(path):
    '''
    return file extension.
    '''
    file_name, file_extension = os.path.splitext(path)
    return file_extension


def read_pdf(path):
    '''
    Read pdf file.
    '''
    # creating a pdf reader object 
    reader = PdfReader(path) 
    text   = ''
    for i in range(len(reader.pages)): 
        # getting a specific page from the pdf file 
        page = reader.pages[i] 
        # extracting text from page 
        text = text + page.extract_text() 
    return text

def read_text(path):
    with open(path, 'r') as f:
        content = f.read()
    return content

def text_words(text):
    return len(text.split(' '))

def read_directory_files(path):
    files     = find_files(path)
    text_data = {}
    
    for file in files:
        print(f'Reading the file: {file}')
        extension = find_file_ext(file)
        if extension=='.pdf':
            text = read_pdf(file)
            text_data[file] = {'len': text_words(text),
                               'text': text
                              }
        elif extension=='.rtf':
            text = read_text(file)
            text_data[file] = {'len': text_words(text),
                               'text': text
                              }
        else:
            text = read_text(file)
            text_data[file] = {'len': text_words(text),
                               'text': text
                              }

    return text_data

def save_emb_vectorizer(vectorizer, path):
    joblib.dump(vectorizer, path)  # Save the model to a file

def load_emb_vectorizer(path):
    # Load the saved moded
    return joblib.load(path)


def create_embedding(data):
    texts    = []
    for key in data:
        texts.append(data[key]['text'])
        
    vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1,2), stop_words = "english", lowercase = True, max_features = 10000)
    embeddings = vectorizer.fit_transform(texts).toarray()
    for index, key in enumerate(data):
        data[key]['emb'] = embeddings[index]
    
    return data, vectorizer


def create_embedding_from_vectorizer(text, vectorizer):
    return vectorizer.transform([text]).toarray()

def get_similar_text(doc_emb, emb, top_doc):
    similarities = cosine_similarity(emb, doc_emb)
    sorted_indices = np.argsort(similarities[0])[::-1]  # Sort in descending order
    top_indices = sorted_indices[:top_doc]
    return top_indices

def search_doc(text, data, top_index, vectorizer):
    text_emb = create_embedding_from_vectorizer(text, vectorizer)
    doc_emb  = [data[i]['emb'] for i in data]
    indexs = get_similar_text(doc_emb, text_emb, top_index)

    similar_doc = ''
    for i, index in enumerate(indexs):
        file  = list(data.keys())[index]
        similar_doc =  similar_doc + f'Doc {i}\n' + data[file]['text']

    return similar_doc

def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def process_data(path, botname):
    text_data = read_directory_files(path)
    data_index, vectorizer = create_embedding(text_data)

    np.save(f'/home/spanwar/Documents/collage/projects/chatbot_v2/data/qna_save_data/{botname}_qna.npy', data_index)
    save_emb_vectorizer(vectorizer, f'/home/spanwar/Documents/collage/projects/chatbot_v2/data/qna_save_data/{botname}_vec.pkl')


def initialize_qna(path, botname):
    process_data(path, botname)


def response(query, botname):
    # Load data
    data_index = np.load(f'/home/spanwar/Documents/collage/projects/chatbot_v2/data/qna_save_data/{botname}_qna.npy', allow_pickle=True)
    vectorizer = load_emb_vectorizer(f'/home/spanwar/Documents/collage/projects/chatbot_v2/data/qna_save_data/{botname}_vec.pkl')
    data_index = data_index.tolist()
    # Search doc
    message = search_doc(query, data_index, 2, vectorizer)
    message = message + f'\n#####\nUsing above data Please answer this question. Please write atmax 100 words only.: {query}'
    # call
    answer = call_gemini(message)
    return answer