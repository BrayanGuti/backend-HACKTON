import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from supabase import create_client

# Variables de entorno Supabase (usamos directamente las que diste)
SUPABASE_URL = "https://egpoxjmcflxqsywpiznw.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVncG94am1jZmx4cXN5d3Bpem53Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYyOTIxMzksImV4cCI6MjA2MTg2ODEzOX0.hNSzbpLTQNhrWgHP4UghidLB1Qo3qA2fsNRIp49hUNI"

# Crear cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Buscar token para este correo
user_email = "mess.ia.hackaton.2025@gmail.com"
response = supabase.table("user_oauth_providers").select("*").eq("user_email", user_email).execute()

if not response.data:
    print(f"❌ No se encontraron tokens para: {user_email}")
    exit()

record = response.data[0]

# Construir objeto Credentials con refresco automático
credentials = Credentials(
    token=record["access_token"],
    refresh_token=record["refresh_token"],
    token_uri=record["token_uri"],
    client_id=record["client_id"],
    client_secret=record["client_secret"]
)

# Crear servicio Gmail
service = build('gmail', 'v1', credentials=credentials)

# Obtener últimos 5 correos
results = service.users().messages().list(userId='me', maxResults=5).execute()
messages = results.get('messages', [])

print(f"\n✅ Últimos {len(messages)} correos en {user_email}:")
for msg in messages:
    msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
    headers = msg_detail.get("payload", {}).get("headers", [])
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(Sin asunto)")
    print(f" - {subject}")
