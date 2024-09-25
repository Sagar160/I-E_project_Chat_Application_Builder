import os
import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession, Part
from vertexai.language_models import TextEmbeddingModel

def model_init():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/spanwar/Documents/collage/projects/chatbot_v2/vertex_key/oval-smile-417517-43cf867c95fd.json'
    project_id = "oval-smile-417517"
    location   = "us-central1"
    vertexai.init(project=project_id, location=location)

    model = GenerativeModel("gemini-pro")
    return model

def get_chat_response(model, prompt: str):
    response = model.generate_content(prompt)
    return response

def response_to_text(response):
    return response.text
        # return str(response.candidates[0].content.parts[0]).split('text: "')[-1].split('"\n')[0]

def call_gemini(message):
    model = model_init()
    message = message
    response = get_chat_response(model, message)
    txt_output = response_to_text(response)
    return txt_output