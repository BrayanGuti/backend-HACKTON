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
import jwt  # <-- Añade esta importación al inicio del archivo


# Configura las rutas importantes
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'email_connector', 'oauth', 'client_secret.json')
# En views.py (y gmail_auth.py)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",  # Acceso de solo lectura a Gmail
    "openid",  # Para autenticación básica
    "https://www.googleapis.com/auth/userinfo.email"  # Para obtener el email del usuario
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
    print("Credentials object:", dir(credentials))  # Lista todos los atributos y métodos
    print("Credentials expiry:", credentials.expiry)  # Verifica si existe
    # Decodifica el id_token para obtener el email
    id_token = credentials.id_token
    if not id_token:
        return JsonResponse({'error': 'ID token missing'}, status=400)

    try:
        # Decodifica el JWT sin verificar la firma (solo para prueba)
        id_info = jwt.decode(id_token, options={"verify_signature": False})  # <-- Aquí se corrige el error
        email = id_info.get('email')
    except Exception as e:
        return JsonResponse({'error': f'Error decoding ID token: {str(e)}'}, status=400)


    user = User.objects.first()  # Temporal: reemplazar con request.user

    GmailAccount.objects.update_or_create(
        user=user,
        email=email,  # <-- Usa la variable decodificada
        defaults={
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'token_expiry': credentials.expiry  # ← Usa directamente el datetime de expiración
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
