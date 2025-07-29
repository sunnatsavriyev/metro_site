from rest_framework import serializers
from .models import (
    News, Comment, NewsImage, JobVacancy,
    StatisticData, LostItemRequest, CustomUser
)

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'role', 'is_staff', 'is_superuser')


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ['id', 'image']


class NewsCreateSerializerUz(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = News
        fields = [
            'title_uz',  'description_uz',
            'fullContent_uz',  'publishedAt',
            'category_uz',  'images'
        ]

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        news = News.objects.create(**validated_data)
        for image in images:
            NewsImage.objects.create(news=news, image=image)
        return news

class NewsCreateSerializerRu(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = News
        fields = [
            'title_ru',  'description_ru',
            'fullContent_ru',  'publishedAt',
            'category_ru',  'images'
        ]

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        news = News.objects.create(**validated_data)
        for image in images:
            NewsImage.objects.create(news=news, image=image)
        return news



class NewsCreateSerializerEn(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = News
        fields = [
            'title_en',  'description_en',
            'fullContent_en',  'publishedAt',
            'category_en',  'images'
        ]

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        news = News.objects.create(**validated_data)
        for image in images:
            NewsImage.objects.create(news=news, image=image)
        return news



class NewsSerializerUz(serializers.ModelSerializer):
    images = NewsImageSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title_uz', 
            'description_uz', 
            'fullContent_uz', 
            'publishedAt', 'category_uz',
            'like_count', 'images'
        ]


class NewsSerializerRu(serializers.ModelSerializer):
    images = NewsImageSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title_ru', 
            'description_ru', 
            'fullContent_ru', 
            'publishedAt', 'category_ru',
            'like_count', 'images'
        ]

class NewsSerializerEn(serializers.ModelSerializer):
    images = NewsImageSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title_en', 
            'description_en', 
            'fullContent_en', 
            'publishedAt', 'category_en',
            'like_count', 'images'
        ]


class CommentSerializerUz(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'news', 'author_uz',
            'content_uz',  'timestamp'
        ]



class CommentSerializerRu(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'news', 'author_ru',
            'content_ru',  'timestamp'
        ]




class CommentSerializerEn(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'news', 'author_en',
            'content_en',  'timestamp'
        ]


class JobVacancySerializerUz(serializers.ModelSerializer):
    created_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = JobVacancy
        fields = [
            'id', 'title_uz',
            'requirements_uz',
            'benefits_uz',
            'ageRange', 'created_by'
        ]
        read_only_fields = ['created_by']



class JobVacancySerializerRu(serializers.ModelSerializer):
    created_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = JobVacancy
        fields = [
            'id', 'title_ru',
            'requirements_ru',
            'benefits_ru',
            'ageRange', 'created_by'
        ]
        read_only_fields = ['created_by']



class JobVacancySerializerEn(serializers.ModelSerializer):
    created_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = JobVacancy
        fields = [
            'id', 'title_en',
            'requirements_en',
            'benefits_en',
            'ageRange', 'created_by'
        ]
        read_only_fields = ['created_by']


class StatisticDataSerializer(serializers.ModelSerializer):
    station_name = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()

    class Meta:
        model = StatisticData
        fields = ['id', 'station_name', 'user_count', 'month', 'created_at']
        read_only_fields = ['created_at']

    # --- O‘qish uchun tarjima ---
    def get_station_name(self, obj):
        lang = self.context.get('lang', 'uz')  # default uz
        return obj.get_station_translation(lang)

    def get_month(self, obj):
        lang = self.context.get('lang', 'uz')
        return obj.get_month_translation(lang)


class StatisticDataWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatisticData
        fields = ['station_name', 'user_count', 'month']


class LostItemRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostItemRequest
        fields = [
            'id',
            'name_uz', 'name_ru', 'name_en',
            'phone', 'email',
            'message_uz', 'message_ru', 'message_en',
            'created_at'
        ]
        read_only_fields = ['created_at']