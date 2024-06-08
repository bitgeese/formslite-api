import base64
import json
from datetime import datetime
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.urls import reverse_lazy
from notion_client import Client

REDIRECT_URI = reverse_lazy("dashboard:notion_callback")


def get_authorization_url():
    params = {
        "client_id": settings.NOTION_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "database.read database.write",
    }
    return f"{settings.NOTION_AUTHORIZATION_URL}?{urlencode(params)}"


def get_access_token(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"https://api.formslite.io{REDIRECT_URI}",
    }
    credentials = f"{settings.NOTION_CLIENT_ID}:{settings.NOTION_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_credentials}",
    }

    response = requests.post(
        settings.NOTION_TOKEN_URL, data=json.dumps(data), headers=headers
    )
    response.raise_for_status()
    return response.json()


class NotionClient:
    def __init__(self, token):
        self.notion = Client(auth=token)

    def get_all_databases(self):
        databases = []

        response = self.notion.search(
            filter={"property": "object", "value": "database"}
        )
        databases.extend(response["results"])

        while response.get("has_more"):
            response = self.notion.search(
                filter={"property": "object", "value": "database"},
                start_cursor=response.get("next_cursor"),
            )
            databases.extend(response["results"])

        return databases

    def get_database_by_id(self, database_id):
        return self.notion.databases.retrieve(database_id=database_id)

    def add_row_to_database(self, database_id, data):
        create_title = (
            lambda: f"Form Submission - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        properties = {"Name": {"title": [{"text": {"content": create_title()}}]}}
        for key, value in data.items():
            properties[key] = {"rich_text": [{"text": {"content": value}}]}
        try:
            new_page = self.notion.pages.create(
                parent={"database_id": database_id}, properties=properties
            )
        except Exception as e:
            print("Notion ERROR:", e)
            return None
        return new_page
