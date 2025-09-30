from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from ..models import FoydalanuvchiStatistika, SessiyaIzlovi

class FoydalanuvchiStatMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Sessiya ID olish
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        # Sessiya mavjudligini tekshirish
        sessiya, yaratildi = SessiyaIzlovi.objects.get_or_create(sessiya_id=session_id)

        if yaratildi:
            # Yangi sessiya bo‘lsa jami kirishlar sonini oshirish
            statistika, _ = FoydalanuvchiStatistika.objects.get_or_create(id=1)
            statistika.jami_kirishlar += 1
            statistika.save()

        # Har requestda oxirgi faollik vaqtini yangilash
        sessiya.oxirgi_harakat = timezone.now()
        sessiya.save()
