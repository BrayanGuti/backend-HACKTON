# email_connector/oauth/gmail_auth.py

from google_auth_oauthlib.flow import Flow
import os
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'email_connector', 'oauth', 'client_secret.json')

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

REDIRECT_URI = 'http://localhost:8000/email_connector/oauth/callback'


def get_authorization_url():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, state = flow.authorization_url(
        prompt='consent',
        access_type='offline',
        include_granted_scopes='true'
    )
    return auth_url, state, flow

