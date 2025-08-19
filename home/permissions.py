from rest_framework import permissions

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
            getattr(request.user, 'role', '') == 'Lost_item_support'
        )