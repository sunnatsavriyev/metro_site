from django.http import HttpResponseForbidden

class IPLoginProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # faqat shu IP lar kirishi mumkin
        self.allowed_ips = ["127.0.0.1", "192.168.0.10"]

    def __call__(self, request):
        ip = request.META.get("REMOTE_ADDR")

        # faqat login URL larini cheklash
        if request.path.startswith("/api/auth/session/login/") and ip not in self.allowed_ips:
            return HttpResponseForbidden("Sizning IP manzilingizga ruxsat yo'q!")

        return self.get_response(request)
