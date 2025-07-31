from rest_framework.throttling import AnonRateThrottle

class LostItemBurstRateThrottle(AnonRateThrottle):
    scope = 'lostitem_burst'  # settings.py da ishlatiladi
