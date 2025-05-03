from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .gemini_service import generate_reply

@csrf_exempt
def ai_chat(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        user_input = body.get('message', '')
        ai_response = generate_reply(user_input)
        return JsonResponse({'response': ai_response})
