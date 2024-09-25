from flask import Flask, flash, render_template,jsonify,request
from flask_cors import CORS
import requests,os
import sys
sys.path.append('/home/spanwar/Documents/collage/projects/chatbot_v2/utils')

# import utils lib
import re
import json
import QnA, shedule
import splitwise
from query_manager import query_manager
from utils import read_json, write_json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]sss/'
CORS(app)

def initialize_agent(agentname, qna_data_dir=None, schedule_json=None):
    if qna_data_dir:
        QnA.initialize_qna(qna_data_dir, agentname)
    if schedule_json:
        shedule.save_shedule(schedule_json, agentname)
    print(f'Agent {agentname} Initialized')

def response_to_query(query, agentname):
    cmd = json.loads(query_manager(query))
    query_response = ''
    print(cmd)
    for key in cmd:
        print('###'*20)
        if key=='qna':
            response = QnA.response(cmd['qna'], agentname)
            query_response = response
            # print(response)
        if key=='schedule':
            response = shedule.response(cmd['schedule'], agentname)
            query_response = query_response + "\n Schedule is " + response
            # print(response)
        if key=='splitwise':
            response = splitwise.response(cmd['splitwise'], agentname)
            print(response)
            query_response = query_response + "\n" + response
        if key=='Error':
            query_response = query_response + "\n" + cmd['Error']
            print(cmd['Error'])
        print(query_response)
    return query_response

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/repository')
def repository():
    agents_info = read_json('/home/spanwar/Documents/collage/projects/chatbot_v2/data/agents_info/agents_info.json')
    agents = agents_info['agents']
    return render_template('repository.html', agents=agents)

@app.route('/toolchain', methods=['GET'])
def render_toolchain():
    return render_template('toolchain.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Read agents info
    agents_info_file = '/home/spanwar/Documents/collage/projects/chatbot_v2/data/agents_info/agents_info.json'
    agents_info = read_json(agents_info_file)

    # Get form data
    agent_info_dict = {}
    agent_info_dict['name'] = request.form.get('name')
    agent_info_dict['description'] = request.form.get('description')
    agent_info_dict['toolchain'] = request.form.getlist('toolType[]')

    # Check if agent already exists
    for agent in agents_info['agents']:
        if agent['name'] == agent_info_dict['name']:
            flash('Agent of this name already exists!', "error")
            return render_template('toolchain.html')

    # Process file uploads
    if 'files' not in request.files:
        print('No file part')

    qna_data_dir = None
    for file in request.files.getlist('qnaFiles'):
        if file.filename == '':
            print('No selected file')
        if file:
            filename = secure_filename(file.filename)
            print(filename)
            qna_data_dir = f'/home/spanwar/Documents/collage/projects/chatbot_v2/data/text_data/{agent_info_dict["name"]}'
            os.makedirs(qna_data_dir, exist_ok=True)
            file.save(os.path.join(qna_data_dir, filename))
    
    schedule_json = None
    for file in request.files.getlist('scheduleFiles'):
        if file.filename == '':
            print('No selected file')
        if file:
            filename = secure_filename(file.filename)
            print(filename)
            schedule_json = json.loads(file.read())

    print(agent_info_dict)

    initialize_agent(agent_info_dict['name'], 
                     qna_data_dir=qna_data_dir, 
                     schedule_json=schedule_json) 
    
    # Save agent info
    agents_info['agents'].append(agent_info_dict)
    agents = agents_info['agents']
    write_json(agents_info_file, agents_info)

    return render_template('repository.html', agents=agents)

@app.route('/agent/<agentname>', methods=['GET'])
def render_agent(agentname):
    print(agentname)
    return render_template('chatbot.html', agentname=agentname)

@app.route('/data', methods=['POST'])
def get_data():
    data = request.get_json()
    agentname = data.get('agentname')
    print(agentname)
    user_input = data.get('data')
    # try:
    pattern = r'@(\w+)' # pattern to extract botname
    match = re.search(pattern, user_input)
    if match:
        activation_cmd = match.group(1)
    else:
        activation_cmd = None
    if activation_cmd=='agent':
        output = response_to_query(user_input, agentname)
        return jsonify({"response":True,"message":output})
    else:
        output = user_input
        return jsonify({"response":True,"message":output})

    # memory.save_context({"input": user_input}, {"output": user_input})
    # return jsonify({"response":True,"message":output})
    # except Exception as e:
    #     print(e)
    #     error_message = f'Error: {str(e)}'
    #     return jsonify({"message":error_message,"response":False})
    
if __name__ == '__main__':
    app.run(debug=True)
