from django.http import HttpResponseNotFound

class ProtectAPIMiddleware:
    SECRET = "UZMETRO_SECRET_2026"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/api/"):
            key = request.headers.get("X-API-KEY")
            if key != self.SECRET:
                return HttpResponseNotFound()
        return self.get_response(request)
