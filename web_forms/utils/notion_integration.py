import base64
import json
from urllib.parse import urlencode

import requests
from django.urls import reverse_lazy
from notion_client import Client

NOTION_CLIENT_ID = "86c089d5-b04f-430a-b938-c70d037a9e2b"
NOTION_CLIENT_SECRET = "secret_Q7qGk6TsJFOWkKprnBKsmUBEyOgnNwxD8yrmVANKsuC"
REDIRECT_URI = reverse_lazy("dashboard:notion_callback")
AUTHORIZATION_URL = "https://api.notion.com/v1/oauth/authorize?client_id="
"86c089d5-b04f-430a-b938-c70d037a9e2b&response_type=code&owner=user&redirect_uri="
"https%3A%2F%2Fapi.formslite.io%2Fdash%2Fnotion%2Fcallback%2F"
TOKEN_URL = "https://api.notion.com/v1/oauth/token"


def get_authorization_url():
    params = {
        "client_id": NOTION_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "database.read database.write",
    }
    url = f"{AUTHORIZATION_URL}?{urlencode(params)}"
    return url


def get_access_token(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "https://3475-152-170-68-27.ngrok-free.app" + REDIRECT_URI,
    }
    credentials = f"{NOTION_CLIENT_ID}:{NOTION_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    authorization_header = f"Basic {encoded_credentials}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization_header,
    }
    print(data)
    response = requests.post(TOKEN_URL, data=json.dumps(data), headers=headers)
    return response.json()


def get_all_databases(token):
    notion = Client(auth=token)
    databases = []

    # Replace 'your_workspace_page_id' with the actual workspace or page ID
    response = notion.search(**{"filter": {"property": "object", "value": "database"}})

    databases.extend(response["results"])

    # Handle pagination if there are more results
    while response.get("has_more"):
        response = notion.search(
            **{
                "filter": {"property": "object", "value": "database"},
                "start_cursor": response.get("next_cursor"),
            }
        )
        databases.extend(response["results"])
    return databases


def get_database_by_id(token, database_id):
    notion = Client(auth=token)
    database = notion.databases.retrieve(database_id=database_id)
    return database


def add_row_to_database(token, database_id, data):
    notion = Client(auth=token)
    properties = {
        "Name": {"title": [{"text": {"content": "Submission Title"}}]}
    }  # TODO generate title
    for key, value in data.items():
        properties[key] = {"rich_text": [{"text": {"content": value}}]}
    try:
        new_page = notion.pages.create(
            **{"parent": {"database_id": database_id}, "properties": properties}
        )
    except Exception as e:
        print("Notion ERROR:", e)
        return None
    print(new_page)
    return new_page
