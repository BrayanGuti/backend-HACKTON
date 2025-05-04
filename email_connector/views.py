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
from supabase import create_client

supabase = create_client(
    'https://egpoxjmcflxqsywpiznw.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVncG94am1jZmx4cXN5d3Bpem53Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYyOTIxMzksImV4cCI6MjA2MTg2ODEzOX0.hNSzbpLTQNhrWgHP4UghidLB1Qo3qA2fsNRIp49hUNI'
)

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
    # 1. Validar el código de autorización
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'error': 'No code provided'}, status=400)

    # 2. Configurar el flujo OAuth
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            scopes=SCOPES,
            redirect_uri='http://localhost:8000/email_connector/oauth/callback'
        )
        flow.fetch_token(code=code)
        credentials = flow.credentials
    except Exception as e:
        return JsonResponse({'error': f'Error en el flujo OAuth: {str(e)}'}, status=400)

    # 3. Decodificar el ID token para obtener el email
    try:
        id_info = jwt.decode(credentials.id_token, options={"verify_signature": False})
        email = id_info.get('email')
        if not email:
            return JsonResponse({'error': 'Email no encontrado en el ID token'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error decodificando ID token: {str(e)}'}, status=400)

    # 4. Guardar en Supabase (CORRECCIÓN PRINCIPAL)
    try:
        # Primero verifica si el registro existe
        existing_record = supabase.table('user_oauth_providers') \
            .select('*') \
            .eq('user_email', email) \
            .execute()

        data = {
            'user_email': email,
            'provider': 'google',
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'token_expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }

        if existing_record.data:
            # Actualizar registro existente
            response = supabase.table('user_oauth_providers') \
                .update(data) \
                .eq('user_email', email) \
                .execute()
        else:
            # Insertar nuevo registro
            response = supabase.table('user_oauth_providers') \
                .insert(data) \
                .execute()

        # Verificar errores
        if hasattr(response, 'error'):
            raise Exception(response.error)

        return JsonResponse({
            'message': 'Autenticación exitosa',
            'data': {
                'email': email,
                'provider': 'google'
            }
        })

    except Exception as e:
        return JsonResponse({'error': f'Error al guardar en Supabase: {str(e)}'}, status=500)

# Almacena temporalmente los states de OAuth (en producción usar DB o sesión segura)
oauth_sessions = {}

@csrf_exempt
def auth_url(request):
    auth_url, state, flow = get_authorization_url()
    oauth_sessions[state] = flow  # ← Usa el `state` devuelto directamente
    return JsonResponse({'url': auth_url})
