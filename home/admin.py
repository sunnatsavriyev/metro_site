from django.contrib import admin
from .models import (
    CustomUser, Department, News, NewsImage, Comment,
    JobVacancy,JobVacancyRequest, StatisticData,
    LostItemRequest,FoydalanuvchiStatistika,AnnouncementImage,Announcement,AnnouncementComment,AnnouncementLike,
    Korrupsiya, KorrupsiyaImage, KorrupsiyaComment, KorrupsiyaLike, SimpleUser, MediaPhoto, MediaVideo, FrontendImage,StationFront,Management
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.contrib.admin import AdminSite



class RoleBasedAdminSite(AdminSite):
    site_header = "SRM Admin Panel"

    def has_permission(self, request):
        user = request.user
        # Active va authenticated, simple bo'lmasa
        return user.is_active and user.is_authenticated and getattr(user, 'role', None) != 'simple'

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        role = getattr(request.user, 'role', None)

        if request.user.is_superuser:
            return app_list

        allowed_models = []
        if role == 'news_editor':
            allowed_models = ['Announcement', 'AnnouncementComment', 'AnnouncementLike',
                              'News',  'Comment',
                              'Korrupsiya', 'KorrupsiyaComment', 'KorrupsiyaLike']
        elif role == 'hr':
            allowed_models = ['JobVacancy', 'JobVacancyRequest']
        elif role == 'lost_item_support':
            allowed_models = ['LostItemRequest']
        elif role == 'statistician':
            allowed_models = ['StatisticData', 'FoydalanuvchiStatistika']

        filtered_app_list = []
        for app in app_list:
            filtered_models = []
            for model in app['models']:
                if model['object_name'] in allowed_models:
                    filtered_models.append(model)
            if filtered_models:
                app['models'] = filtered_models
                filtered_app_list.append(app)
        return filtered_app_list
    
    


# ---------- CustomUser ----------
class CustomUserCreationForm(forms.ModelForm):
    """Foydalanuvchini yaratish uchun forma: faqat username, role, parol"""
    password1 = forms.CharField(label='Parol', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Parolni tasdiqlang', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username', 'role')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Parollar mos emas")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    list_display = ['username', 'role', 'is_staff']
    list_filter = ['role', 'is_staff']
    search_fields = ['username']
    ordering = ['username']

    fieldsets = (
        (None, {'fields': ('username', 'role', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role', 'password1', 'password2'),
        }),
    )


# admin.site.register(CustomUser, CustomUserAdmin)


class RoleBasedModelAdmin(admin.ModelAdmin):
    allowed_roles = []

    # 1. SIDEBARDA APP KO'RINISHI UCHUN SHU METOD SHART
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return getattr(request.user, 'role', '') in self.allowed_roles

    # 2. MODEL ICHIGA KIRISH UCHUN
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return getattr(request.user, 'role', '') in self.allowed_roles

    def has_add_permission(self, request):
        return request.user.is_superuser or getattr(request.user, 'role', '') in self.allowed_roles

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or getattr(request.user, 'role', '') in self.allowed_roles

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or getattr(request.user, 'role', '') in self.allowed_roles


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1
    fields = ['image']
    # allowed_roles = ['news_editor']


# @admin.register(News)
class NewsAdmin(RoleBasedModelAdmin):
    list_display = ['title', 'category', 'publishedAt', 'like_count']
    list_filter = ['category']
    ordering = ['-publishedAt']
    search_fields = ['title', 'description']
    inlines = [NewsImageInline]
    allowed_roles = ['news_editor']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "created_by":
            # Admin va news_editor hammasini ko'radi
            if request.user.is_superuser or getattr(request.user, 'role', '') in ['news_editor', 'admin']:
                kwargs["queryset"] = CustomUser.objects.filter(role__in=['news_editor', 'admin'])
            else:
                # Oddiy foydalanuvchi faqat o'zini ko'radi
                kwargs["queryset"] = CustomUser.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# @admin.register(Comment)
class CommentAdmin(RoleBasedModelAdmin):
    list_display = ['news', 'author', 'timestamp']
    list_filter = ['timestamp']
    ordering = ['-timestamp']
    search_fields = ['author',  'content', ]
    allowed_roles = ['news_editor']

# @admin.register(JobVacancy)
class JobVacancyAdmin(RoleBasedModelAdmin):
    list_display = ['title', 'created_by']
    search_fields = ['title']
    ordering = ['title']
    allowed_roles = ['hr']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "created_by":
            # Superuser va HR hammasini ko'radi
            if request.user.is_superuser or getattr(request.user, 'role', '') in ['hr', 'admin']:
                kwargs["queryset"] = CustomUser.objects.filter(role__in=['hr', 'admin'])
            else:
                # Oddiy foydalanuvchi faqat o'zini ko'radi
                kwargs["queryset"] = CustomUser.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# @admin.register(JobVacancyRequest)
class JobVacancyRequestAdmin(RoleBasedModelAdmin):
    list_display = ['name', 'phone', 'email', 'status', 'created_at', 'file']
    search_fields = ['name', 'phone', 'email']
    list_filter = ['status', 'created_at']
    ordering = ['-created_at']
    allowed_roles = ['hr']

# @admin.register(StatisticData)
class StatisticDataAdmin(RoleBasedModelAdmin):
    list_display = ['station_name', 'user_count', 'year', 'month', 'created_at']
    list_filter = ['station_name']
    search_fields = ['station_name']
    allowed_roles = ['statistician']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "created_by":
            if request.user.is_superuser or getattr(request.user, 'role', '') in ['statistician', 'admin']:
                kwargs["queryset"] = CustomUser.objects.filter(role__in=['statistician', 'admin'])
            else:
                kwargs["queryset"] = CustomUser.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    


# @admin.register(LostItemRequest)
class LostItemRequestAdmin(RoleBasedModelAdmin):
    list_display = ['name', 'phone', 'email', 'address', 'passport', 'created_at', 'status']
    search_fields = ['name', 'phone', 'email', 'passport']
    list_filter = ['created_at', 'status']
    ordering = ['-created_at']
    allowed_roles = ['lost_item_support']


# @admin.register(FoydalanuvchiStatistika)
class FoydalanuvchiStatistikaAdmin(RoleBasedModelAdmin):
    list_display = ['jami_kirishlar', 'oxirgi_faollik']



class AnnouncementImageInline(admin.TabularInline):
    model = AnnouncementImage
    extra = 1
    fields = ['image']
    # allowed_roles = ['news_editor']


# @admin.register(Announcement)
class AnnouncementAdmin(RoleBasedModelAdmin):
    list_display = (
        'title',
        'published_at'
    )
    search_fields = (
        'title', 
        'description', 
    )
    ordering = ['-published_at']
    inlines = [AnnouncementImageInline]
    allowed_roles = ['news_editor']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "created_by":
            if request.user.is_superuser or getattr(request.user, 'role', '') in ['admin']:
                kwargs["queryset"] = CustomUser.objects.all()
            else:
                kwargs["queryset"] = CustomUser.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# @admin.register(AnnouncementComment)
class AnnouncementCommentAdmin(RoleBasedModelAdmin):
    list_display = ['announcement', 'author', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['author', 'content']
    ordering = ['-timestamp']
    allowed_roles = ['news_editor']


# @admin.register(AnnouncementLike)
class AnnouncementLikeAdmin(RoleBasedModelAdmin):
    list_display = ['announcement', 'session_key', 'created_at']
    list_filter = ['created_at']
    search_fields = ['session_key']
    allowed_roles = ['news_editor']
    


class KorrupsiyaImageInline(admin.TabularInline):
    model = KorrupsiyaImage
    extra = 1
    fields = ['image']
    # allowed_roles = ['news_editor']    
    
    

# @admin.register(Korrupsiya)
class KorrupsiyaAdmin(RoleBasedModelAdmin):
    list_display = (
        'title',
    )
    search_fields = (
        'title', 
        'description', 
    )
    inlines = [KorrupsiyaImageInline]
    allowed_roles = ['news_editor']
    
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "created_by":
            if request.user.is_superuser or getattr(request.user, 'role', '') in ['admin']:
                kwargs["queryset"] = CustomUser.objects.all()
            else:
                kwargs["queryset"] = CustomUser.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    
# @admin.register(KorrupsiyaComment)
class KorrupsiyaCommentAdmin(RoleBasedModelAdmin):
    list_display = ['korrupsiya', 'author', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['author', 'content']
    ordering = ['-timestamp']
    allowed_roles = ['news_editor']
    
# @admin.register(KorrupsiyaLike)
class KorrupsiyaLikeAdmin(RoleBasedModelAdmin):
    list_display = ['korrupsiya', 'session_key', 'created_at']
    list_filter = ['created_at']
    search_fields = ['session_key']
    allowed_roles = ['news_editor']
    
    
# @admin.register(SimpleUser)
class SimpleUserAdmin(RoleBasedModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'is_verified']
    search_fields = ['first_name', 'last_name', 'phone']
    
    
    
    
# @admin.register(MediaPhoto)
class MediaPhotoAdmin(RoleBasedModelAdmin):
    list_display = ("title", "language", "group_id", "order")
    list_editable = ("order",)
    list_filter = ("language", "category")
    search_fields = ("title",)
    allowed_roles = ['news_editor', 'admin']

class MediaVideoAdmin(RoleBasedModelAdmin):
    list_display = ("title", "language", "group_id", "order")
    list_editable = ("order",)
    list_filter = ("language", "category")
    search_fields = ("title",)
    allowed_roles = ['news_editor', 'admin']

class StationFrontAdmin(RoleBasedModelAdmin):
    list_display = ('name', 'video_title')
    search_fields = ('name',)
    allowed_roles = ['news_editor', 'admin'] # Rolni belgilashni unutmang

    # Admin panelda maydonlarni guruhlash
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('name',) # descriptionni ham qo'shdim
        }), # <-- BU YERDA VERGUL BO'LISHI SHART
        ("Rasmlar", {
            'fields': ('image1', 'image2')
        }), # <-- BU YERDA VERGUL BO'LISHI SHART
        ("Video ma'lumotlari", {
            'fields': ('video_title', 'video_url', 'video_thumbnail')
        }),
    )
    
    
    
class ManagementAdmin(RoleBasedModelAdmin):
    list_display = ('firstName', 'lastName', 'language', 'group_id', 'order')
    list_filter = ('language', 'department')
    search_fields = ('firstName', 'lastName', 'department')
    ordering = ('order', 'group_id')
    
    # Rolni belgilash
    allowed_roles = ['news_editor', 'admin']
    
    
class DepartmentAdmin(RoleBasedModelAdmin):
    list_display = ('title', 'language', 'group_id', 'order')
    list_filter = ('language',)
    search_fields = ('title', 'head')
    allowed_roles = ['news_editor', 'admin']

# Register
# role_based_admin.register(Management, ManagementAdmin)
    
# @admin.register(FrontendImage)
class FrontendImageAdmin(RoleBasedModelAdmin):
    list_display = ("id", "section", "order")
    list_filter = ("section",)
    list_editable = ("order",)
    search_fields = ("section",)
    
    
role_based_admin = RoleBasedAdminSite(name='role_based_admin')

role_based_admin.register(CustomUser, CustomUserAdmin)
role_based_admin.register(News, NewsAdmin)
role_based_admin.register(Comment, CommentAdmin)
role_based_admin.register(JobVacancy, JobVacancyAdmin)
role_based_admin.register(JobVacancyRequest, JobVacancyRequestAdmin)
role_based_admin.register(StatisticData, StatisticDataAdmin)
role_based_admin.register(LostItemRequest, LostItemRequestAdmin)
role_based_admin.register(FoydalanuvchiStatistika, FoydalanuvchiStatistikaAdmin)
role_based_admin.register(Announcement, AnnouncementAdmin)
role_based_admin.register(AnnouncementComment, AnnouncementCommentAdmin)
role_based_admin.register(AnnouncementLike, AnnouncementLikeAdmin)
role_based_admin.register(Korrupsiya, KorrupsiyaAdmin)
role_based_admin.register(KorrupsiyaComment, KorrupsiyaCommentAdmin)
role_based_admin.register(KorrupsiyaLike, KorrupsiyaLikeAdmin)
role_based_admin.register(SimpleUser, SimpleUserAdmin)
role_based_admin.register(MediaPhoto, MediaPhotoAdmin)
role_based_admin.register(MediaVideo, MediaVideoAdmin)
role_based_admin.register(FrontendImage, FrontendImageAdmin)
role_based_admin.register(StationFront, StationFrontAdmin)
role_based_admin.register(Management, ManagementAdmin)
role_based_admin.register(Department, DepartmentAdmin)

inlines = [NewsImageInline]  # faqat NewsAdmin ichida

# Announcement
inlines = [AnnouncementImageInline]  # AnnouncementAdmin ichida

# Korrupsiya
inlines = [KorrupsiyaImageInline] 
    
