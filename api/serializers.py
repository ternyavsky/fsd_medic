import json
import re
import random
from rest_framework import serializers

from db.queries import get_user_by_args
from .models import News, User, NumberCodes, Centers, Clinics, Disease, Notes, Saved, Like
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField
class CenterSerializer(serializers.ModelSerializer):
    """Клиники"""
    class Meta:
        model = Centers
        fields = '__all__'

class DiseaseSerializer(serializers.ModelSerializer):
    """Болезни"""
    class Meta:
        model = Disease
        fields = '__all__'


class UserGetSerializer(serializers.ModelSerializer):
    """Получаем пользователя(аккаунт и т.п)"""
    disease = DiseaseSerializer(many=True, allow_null=True, required=False)
    center = CenterSerializer(many=True, allow_null=True, required=False)
    password = serializers.CharField(allow_null=True, required=False)  # убираем обяз. поле password
    group = serializers.CharField(allow_null=True, required=False)  # убираем обяз. поле group

    class Meta:
        model = User
        fields = '__all__'


class NewsSerializer(serializers.ModelSerializer):
    disease = DiseaseSerializer(allow_null=True, required=False)
    center = CenterSerializer(allow_null=True, required=False)

    class Meta:
        model = News
        fields = '__all__'

class CreateNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

    def create(self, validated_data):
        return News.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.center = validated_data.get('center', instance.center)
        instance.disease = validated_data.get('disease', instance.disease)
        instance.save()
        return instance


class NoteSerializer(serializers.ModelSerializer):
    user = UserGetSerializer()
    doctor = UserGetSerializer()
    center = CenterSerializer()

    class Meta:
        model = Notes
        fields = ['pk', 'user', 'doctor', 'center', 'title', 'time_start', 'time_end',
                  'online', 'notify', 'problem', 'duration_note', 'file', 'created_at', 'updated_at', 'status']


class NoteUpdateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    doctor = serializers.CharField(allow_null=True, required=False)
    title = serializers.CharField(allow_null=True, required=False)
    problem = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = Notes
        fields = '__all__'


class CreateNoteSerializer(serializers.ModelSerializer):
    """Создание записи"""
    class Meta:
        model = Notes
        fields = '__all__'

    def create(self, validated_data):
        user = self.context["request"].user

        request_user = get_user_by_args(number=user)
        note = Notes.objects.create(**validated_data)
        note.user = request_user
        return note


class ClinicSerializer(serializers.ModelSerializer):
    supported_diseases = serializers.SerializerMethodField()

    class Meta:
        model = Clinics
        fields = '__all__'

    def get_supported_diseases(self, obj):
        return DiseaseSerializer(obj.supported_diseases.all(), many=True).data


class SavedSerializer(serializers.ModelSerializer):
    ''' get serialier for saved model'''
    user = UserGetSerializer()
    news = NewsSerializer()

    class Meta:
        model = Saved
        fields = '__all__'


# like too up
class LikeSerializer(serializers.ModelSerializer):
    user = UserGetSerializer()
    news = NewsSerializer()

    class Meta:
        model = Like
        fields = '__all__'


class SearchSerializer(serializers.Serializer):
    clinics = ClinicSerializer(read_only=True, many=True)
    centers = CenterSerializer(read_only=True, many=True)
    users = UserGetSerializer(read_only=True, many=True)

    class Meta:
        fields = '__all__'
