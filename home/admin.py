from django.contrib import admin
from .models import (
    CustomUser, News, NewsImage, Comment,
    JobVacancy,JobVacancyRequest, StatisticData,
    LostItemRequest,FoydalanuvchiStatistika, Station, StationImage, StationVideo
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms


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


admin.site.register(CustomUser, CustomUserAdmin)


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1
    fields = ['image']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title_uz', 'title_ru', 'title_en', 'category_uz', 'category_ru', 'category_en', 'publishedAt', 'like_count']
    list_filter = ['category_uz', 'category_ru', 'category_en']
    ordering = ['-publishedAt']
    search_fields = ['title_uz', 'title_ru', 'title_en', 'description_uz', 'description_ru', 'description_en']
    inlines = [NewsImageInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['news', 'author_uz', 'author_ru', 'author_en', 'timestamp']
    list_filter = ['timestamp']
    ordering = ['-timestamp']
    search_fields = ['author_uz', 'author_ru', 'author_en', 'content_uz', 'content_ru', 'content_en']

@admin.register(JobVacancy)
class JobVacancyAdmin(admin.ModelAdmin):
    list_display = ['title_uz', 'title_ru', 'title_en', 'created_by']
    search_fields = ['title_uz', 'title_ru', 'title_en']
    ordering = ['title_uz']


@admin.register(JobVacancyRequest)
class JobVacancyRequestAdmin(admin.ModelAdmin):
    list_display = ['name_uz', 'name_ru', 'name_en', 'phone', 'email', 'status', 'created_at', 'file']
    search_fields = ['name_uz', 'name_ru', 'name_en', 'phone', 'email']
    list_filter = ['status', 'created_at']
    ordering = ['-created_at']

@admin.register(StatisticData)
class StatisticDataAdmin(admin.ModelAdmin):
    list_display = ['station_name', 'user_count', 'month', 'created_at']
    list_filter = ['station_name']
    search_fields = ['station_name']


@admin.register(LostItemRequest)
class LostItemRequestAdmin(admin.ModelAdmin):
    list_display = ['name_uz', 'name_ru', 'name_en', 'phone', 'email', 'created_at']
    search_fields = ['name_uz', 'name_ru', 'name_en', 'phone', 'email']
    list_filter = ['created_at']
    ordering = ['-created_at']


@admin.register(FoydalanuvchiStatistika)
class FoydalanuvchiStatistikaAdmin(admin.ModelAdmin):
    list_display = ['jami_kirishlar', 'oxirgi_faollik']




class StationImageInline(admin.TabularInline):
    model = StationImage
    extra = 1

class StationVideoInline(admin.TabularInline):
    model = StationVideo
    extra = 1

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [StationImageInline, StationVideoInline]

@admin.register(StationImage)
class StationImageAdmin(admin.ModelAdmin):
    list_display = ('station', 'image')

@admin.register(StationVideo)
class StationVideoAdmin(admin.ModelAdmin):
    list_display = ('station', 'title', 'url')