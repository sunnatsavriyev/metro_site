from rest_framework import permissions

class IsNewsEditorOrReadOnly(permissions.BasePermission):
    """
    Faqat yangilik muharriri (news_editor) yoki superuser post/create/update qilishi mumkin.
    Boshqalar faqat o'qiydi.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return user.is_authenticated and (user.is_news_editor or user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsHRUser(permissions.BasePermission):
    """
    Faqat HR (kadrlar) xodimlari yoki superuser kirishi mumkin.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_hr or user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsStatistician(permissions.BasePermission):
    """
    Faqat statistik foydalanuvchilar yoki superuserlar ruxsat oladi.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_statistician or user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)




class IsLostItemSupport(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'role', '') == 'lost_item_support'
        )