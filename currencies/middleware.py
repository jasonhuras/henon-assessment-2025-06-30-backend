from django.http import JsonResponse
from django.conf import settings
from django.utils.crypto import constant_time_compare

class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    
    def __call__(self, request):
        if request.method == "OPTIONS":
            return self.get_response(request)

        if request.path.startswith("/api/"):
            api_key = request.headers.get("X-API-Key")

            if not api_key or not constant_time_compare(api_key, settings.API_KEY):
                return JsonResponse({"error": "Invalid API key"}, status=401)

        return self.get_response(request)
