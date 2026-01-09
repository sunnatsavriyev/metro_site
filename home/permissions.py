from rest_framework import permissions
from .models import SimpleUser
class ReadOnly(permissions.BasePermission):
    
    def has_permission(self, request, view):
        # Faqat o‘qish metodlari uchun ruxsat
        return request.method in permissions.SAFE_METHODS


class IsNewsEditorOrReadOnly(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return user.is_authenticated and (getattr(user, 'is_news_editor', False) or user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsHRUserOrReadOnly(permissions.BasePermission):
   
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return user.is_authenticated and (getattr(user, 'is_hr', False) or user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsStatisticianOrReadOnly(permissions.BasePermission):
  
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return user.is_authenticated and (getattr(user, 'is_statistician', False) or user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)



class IsLostItemSupport(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'role', '') == 'lost_item_support'
        )
        
        
        
class IsVerifiedSimpleUser(permissions.BasePermission):
    """
    Faqat SimpleUser ro'yxatdan o'tib,
    telefoni tasdiqlangan foydalanuchilarga POST ruxsat
    """

    message = "Avval ro‘yxatdan o‘ting va telefon raqamingizni tasdiqlang."

    def has_permission(self, request, view):
        # 1. Superuserga ruxsat
        if request.user and request.user.is_authenticated and request.user.is_superuser:
            return True

        # 2. Faqat ma'lumot ko'rish bo'lsa hamma ko'raversin
        if request.method in permissions.SAFE_METHODS: # GET, HEAD, OPTIONS
            return True

        # 3. POST/PUT/PATCH qilayotgan foydalanuvchi:
        # - Tizimga kirgan bo'lishi kerak (Tokeni orqali)
        # - is_verified maydoni True bo'lishi kerak
        return bool(
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'is_verified', False)
        )