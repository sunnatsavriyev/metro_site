from django.http import HttpResponseForbidden

class IPLoginProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Hammasi ruxsat berilgan, hech qanday IP cheklovi yo‘q
        return self.get_response(request)

