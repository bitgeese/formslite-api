import base64
import json
import logging
from datetime import datetime
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.urls import reverse_lazy
from notion_client import Client

logger = logging.getLogger(__name__)


REDIRECT_URI = reverse_lazy("dashboard:notion_callback")


def get_authorization_url():
    logger.info("Generating Notion authorization URL.")
    params = {
        "client_id": settings.NOTION_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "database.read database.write",
    }
    url = f"{settings.NOTION_AUTHORIZATION_URL}?{urlencode(params)}"
    logger.debug("Authorization URL: %s", url)
    return url


def get_access_token(code):
    logger.info("Exchanging code for Notion access token.")
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

    try:
        response = requests.post(
            settings.NOTION_TOKEN_URL, data=json.dumps(data), headers=headers
        )
        response.raise_for_status()
        logger.info("Successfully retrieved Notion access token.")
        return response.json()
    except requests.RequestException as e:
        logger.exception("Failed to retrieve Notion access token: %s", e)
        raise


class NotionClient:
    def __init__(self, token):
        self.notion = Client(auth=token)
        logger.info("Initialized Notion client.")

    def get_all_databases(self):
        logger.info("Fetching all Notion databases.")
        databases = []
        try:
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
            logger.info("Successfully fetched %d databases.", len(databases))
        except Exception as e:
            logger.exception("Error fetching databases from Notion: %s", e)
        return databases

    def get_database_by_id(self, database_id):
        logger.info("Fetching Notion database with ID: %s", database_id)
        try:
            database = self.notion.databases.retrieve(database_id=database_id)
            logger.info("Successfully retrieved database: %s", database_id)
            return database
        except Exception as e:
            logger.exception("Error fetching database with ID %s: %s", database_id, e)
            return None

    def add_row_to_database(self, database_id, data):
        logger.info("Adding row to Notion database with ID: %s", database_id)
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
            logger.info("Successfully added row to database %s.", database_id)
            return new_page
        except Exception as e:
            logger.exception(
                "Error adding row to Notion database %s: %s", database_id, e
            )
            return None
