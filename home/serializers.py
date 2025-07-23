from rest_framework import serializers
from .models import (
    News, Comment, NewsImage, JobVacancy,
    StatisticData, LostItemRequest, CustomUser
)

# --- Custom User ---
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'role', 'is_staff', 'is_superuser')


# --- News Image ---
class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ['id', 'image']


# --- News Create ---
class NewsCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = News
        fields = [
            'title_uz', 'title_ru', 'description_uz', 'description_ru',
            'fullContent_uz', 'fullContent_ru', 'publishedAt',
            'category_uz', 'category_ru', 'images'
        ]

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        news = News.objects.create(**validated_data)
        for image in images:
            NewsImage.objects.create(news=news, image=image)
        return news


# --- News Full Serializer (for list/detail) ---
class NewsSerializer(serializers.ModelSerializer):
    images = NewsImageSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title_uz', 'title_ru',
            'description_uz', 'description_ru',
            'fullContent_uz', 'fullContent_ru',
            'publishedAt', 'category_uz', 'category_ru',
            'like_count', 'images'
        ]


# --- Comments ---
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'news', 'author_uz', 'author_ru',
            'content_uz', 'content_ru', 'timestamp'
        ]


# --- Job Vacancy ---
class JobVacancySerializer(serializers.ModelSerializer):
    created_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = JobVacancy
        fields = [
            'id', 'title_uz', 'title_ru', 'icon', 'color',
            'requirements_uz', 'requirements_ru',
            'benefits_uz', 'benefits_ru',
            'ageRange', 'category_uz', 'category_ru',
            'salaryRange', 'created_by'
        ]
        read_only_fields = ['created_by']


# --- Statistic Data ---
class StatisticDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatisticData
        fields = ['id', 'station_name', 'user_count', 'month', 'created_at']
        read_only_fields = ['created_at']


# --- Lost Item Request ---
class LostItemRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostItemRequest
        fields = [
            'id', 'name_uz', 'name_ru',
            'phone', 'email',
            'message_uz', 'message_ru',
            'created_at'
        ]
        read_only_fields = ['created_at']
