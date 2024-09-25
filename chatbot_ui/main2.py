from flask import Flask, flash, render_template,jsonify,request
from flask_cors import CORS
import requests,os
import sys
import time
sys.path.append('/home/spanwar/Documents/collage/projects/chatbot_v2/utils')

# import utils lib
import re
import json
import QnA, shedule
import splitwise
# from query_manager import query_manager
from db_connection import db_response
from utils import read_json, write_json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]sss/'
CORS(app)


def response_to_query(query, agentname):
    cmd = query
    print(cmd)
    response = db_response(cmd)
    return response

@app.route('/')
def index():
    agentname='WearableBot'
    return render_template('chatbot.html', agentname=agentname)

@app.route('/data', methods=['POST'])
def get_data():
    data = request.get_json()
    agentname = data.get('agentname')
    print(agentname)
    user_input = data.get('data')
    # try:
    output = response_to_query(user_input, agentname)
    # time.sleep(5)
    # output = {"texts": text_data, "images": image_data}
    # output = {'texts': ['\nlabel: T-Shirt\nkids: 1\nrating: 0.9996854281397904\nprice: 1179', '\nlabel: T-Shirt\nkids: 1\nrating: 0.9964327330650846\nprice: 626'], 'images': ['/home/spanwar/Documents/collage/projects/chatbot_v2/data/cloth_data/archive/images_compressed/fb9a8852-83be-430c-be74-df92541011de.jpg', '/home/spanwar/Documents/collage/projects/chatbot_v2/data/cloth_data/archive/images_compressed/7b6b898d-fb33-4cb3-bc01-7013feadebb7.jpg']}
    return jsonify({"response":True,"message":output})
    # except Exception as e:
    #     print(e)
    #     error_message = f'Error: {str(e)}'
    #     return jsonify({"message":error_message,"response":False})
    
if __name__ == '__main__':
    app.run(debug=True)
