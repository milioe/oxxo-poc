import logging
import os
import json
import requests
from datetime import datetime, timedelta
import pyodbc

import azure.functions as func


AOAI_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
AOAI_key = os.getenv("AZURE_OPENAI_API_KEY")
AOAI_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
embeddings_deployment = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")


# font color adjustments
blue, end_blue = '\033[36m', '\033[0m'

place_orders = False



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    messages = json.loads(req.get_body())

    response = chat_complete(messages)

    products = []
    
    try:
        response_message = response["choices"][0]["message"]
    except:
        logging.info(response)

    
    messages.append({'role' : response_message['role'], 'content' : response_message['content']})

    logging.info(json.dumps(response_message))

    response_object = {
        "messages": messages,
        "products": products
    }

    return func.HttpResponse(
        json.dumps(response_object),
        status_code=200
    )


def chat_complete(messages):
    """  Return assistant chat response based on user query. Assumes existing list of messages """
    
    url = f"{AOAI_endpoint}/openai/deployments/{chat_deployment}/chat/completions?api-version={AOAI_api_version}"

    headers = {
        "Content-Type": "application/json",
        "api-key": AOAI_key
    }

    data = {
        "messages": messages,
        "temperature" : 0
    }

    response = requests.post(url, headers=headers, data=json.dumps(data)).json()

    return response