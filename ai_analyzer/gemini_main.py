import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.api_core.exceptions import GoogleAPIError  # Para manejo de errores

load_dotenv()
print("API Key detectada:", os.environ.get("GEMINI_API_KEY"))


def main():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-pro-preview-03-25"

    system_instruction = [
        types.Part.from_text(text="""Eres un agente inteligente especializado en gestión de correos electrónicos y mensajes de plataformas como Gmail, Outlook, Facebook Messenger y WhatsApp. 

Tu objetivo es ayudar al usuario a organizar, resumir, redactar respuestas, clasificar o reenviar mensajes según su contenido y prioridad. 

Responde siempre con claridad y sin repetir el mensaje original. Si se trata de un resumen, incluye solo lo más relevante. Si se trata de redactar una respuesta, hazla breve, profesional y adecuada al contexto. 

No incluyas información que no esté en el mensaje. Si el usuario pide algo que requiere contexto adicional, solicita la información necesaria.
""")
    ]

    print("🤖 Gemini chatbot listo. Escribe tu mensaje (o 'salir' para terminar):")

    while True:
        user_input = input("Tú: ")
        if user_input.strip().lower() in ["salir", "exit", "quit"]:
            print("👋 Hasta luego.")
            break

        if len(user_input) > 8000:
            print("⚠️ El mensaje es muy largo. Intenta resumirlo un poco.")
            continue

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_input)],
            ),
        ]

        generate_content_config = types.GenerateContentConfig(
            temperature=0.5,  # Más amigable
            response_mime_type="text/plain",
            system_instruction=system_instruction,
        )

        try:
            print("Gemini:", end=" ")
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                print(chunk.text, end="")
            print("\n")
        except GoogleAPIError as e:
            print(f"\n❌ Error de la API de Google: {e.message if hasattr(e, 'message') else str(e)}\n")
        except Exception as e:
            print(f"\n⚠️ Error inesperado: {str(e)}\n")

if __name__ == "__main__":
    main()
