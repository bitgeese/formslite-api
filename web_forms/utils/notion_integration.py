import requests
from urllib.parse import urlencode

NOTION_CLIENT_ID = 'your-client-id'
NOTION_CLIENT_SECRET = 'your-client-secret'
REDIRECT_URI = 'your-redirect-uri'
AUTHORIZATION_URL = 'https://api.notion.com/v1/oauth/authorize'
TOKEN_URL = 'https://api.notion.com/v1/oauth/token'

def get_authorization_url():
    params = {
        'client_id': NOTION_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'database.read database.write',
    }
    url = f"{AUTHORIZATION_URL}?{urlencode(params)}"
    return url

def get_access_token(code):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': NOTION_CLIENT_ID,
        'client_secret': NOTION_CLIENT_SECRET,
    }
    response = requests.post(TOKEN_URL, data=data)
    return response.json()
