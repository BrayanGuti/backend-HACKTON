import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.api_core.exceptions import GoogleAPIError
import json

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
model = "gemini-2.5-pro-exp-03-25"

system_instruction = [
    types.Part.from_text(text="""
Eres un agente inteligente especializado en gestión de correos electrónicos de plataformas como Gmail.

Tu tarea es interpretar las órdenes del usuario y devolver una acción estructurada para automatizarla. Debes responder **solo en formato JSON**, así:

{
  "action": "<una de: block_sender, delete_by_sender, mark_as_spam, summarize, reply>",
  "value": "<dirección de correo, dominio o contenido relevante>"
}

Ejemplos:
- "No quiero correos de @falabella.com" → {"action": "block_sender", "value": "@falabella.com"}
- "Borra todo lo que venga de promociones@gmail.com" → {"action": "delete_by_sender", "value": "promociones@gmail.com"}
- "Marcar como spam los correos de ofertas@spam.com" → {"action": "mark_as_spam", "value": "ofertas@spam.com"}

NO des ninguna explicación ni texto adicional, solo el JSON limpio.
""")
]

def analizar_mensaje(texto_usuario: str) -> str:
    if len(texto_usuario) > 8000:
        return json.dumps({"error": "⚠️ El mensaje es muy largo. Intenta resumirlo."})

    contents = [types.Content(role="user", parts=[types.Part.from_text(text=texto_usuario)])]
    config = types.GenerateContentConfig(
        temperature=0.5,
        response_mime_type="text/plain",
        system_instruction=system_instruction,
    )

    try:
        respuesta = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        ):
            respuesta += chunk.text
        return respuesta
    except GoogleAPIError as e:
        return json.dumps({"error": f"❌ Error de la API de Google: {e.message if hasattr(e, 'message') else str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"⚠️ Error inesperado: {str(e)}"})
