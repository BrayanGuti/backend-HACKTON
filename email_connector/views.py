import os
import json
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from django.http import JsonResponse, HttpResponseRedirect
from .oauth.gmail_auth import get_authorization_url
from django.views.decorators.csrf import csrf_exempt
from .models import GmailAccount
from django.contrib.auth.models import User  # <-- Añade esta línea

# Configura las rutas importantes
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'email_connector', 'oauth', 'client_secret.json')
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "email"
]



def gmail_auth_init(request):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri='http://localhost:8000/email_connector/oauth/callback'
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return HttpResponseRedirect(auth_url)


@csrf_exempt
def gmail_auth_callback(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'error': 'No code provided'}, status=400)

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri='http://localhost:8000/email_connector/oauth/callback'
    )
    flow.fetch_token(code=code)

    credentials = flow.credentials

    # Simulación: en producción esto debe ligarse al usuario autenticado
    user = User.objects.first()  # ⚠️ temporal, usa request.user si tienes login

    GmailAccount.objects.update_or_create(
        user=user,
        email=credentials.id_token.get('email'),
        defaults={
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'token_expiry': datetime.utcnow() + timedelta(seconds=credentials.expiry - datetime.utcnow().timestamp())
        }
    )

    return JsonResponse({'message': 'Cuenta de Gmail conectada con éxito'})

# email_connector/views.py


# Almacena temporalmente los states de OAuth (en producción usar DB o sesión segura)
oauth_sessions = {}

@csrf_exempt
def auth_url(request):
    auth_url, state, flow = get_authorization_url()
    oauth_sessions[state] = flow  # ← Usa el `state` devuelto directamente
    return JsonResponse({'url': auth_url})
