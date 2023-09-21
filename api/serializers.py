import json
import re
import random
from rest_framework import serializers

from db.queries import get_users
from .models import News, User, NumberCode, Center, Clinic, Disease, Note, Saved, Like, Country, Access
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField



class CountrySerializer(serializers.ModelSerializer):
    """Страны"""

    class Meta:
        model = Country
        fields = '__all__'


class CenterSerializer(serializers.ModelSerializer):
    country = PresentablePrimaryKeyRelatedField(
            presentation_serializer=CountrySerializer,
            queryset=Country.objects.all()
            )
    """Клиники"""
    class Meta:
        model = Center
        fields = '__all__'


class DiseaseSerializer(serializers.ModelSerializer):
    """Болезни"""
    class Meta:
        model = Disease
        fields = '__all__'





class UserGetSerializer(serializers.ModelSerializer):
    """Получаем пользователя(аккаунт и т.п)"""
    disease = DiseaseSerializer(many=True, allow_null=True, required=False)
    main_center = CenterSerializer(many=False, allow_null=True, required=False)
    password = serializers.CharField(allow_null=True, required=False)  # убираем обяз. поле password
    group = serializers.CharField(allow_null=True, required=False)  # убираем обяз. поле group
    country = CountrySerializer(required=False) 
    centers = CenterSerializer(many=True, required=False)
    # access_accept = serializers.SerializerMethodField()
    # access_unaccept = serializers.SerializerMethodField()

    # def get_access_accept(self, obj):
    #     return UserGetSerializer(obj.access_accept.all(), many=True).data 

    # def get_access_unaccept(self, obj):
    #     return UserGetSerializer(obj.access_unaccept.all(),many=True).data

    class Meta:
        model = User
        fields = '__all__'

class AccessSerializer(serializers.ModelSerializer):
    user = UserGetSerializer()
    access_accept = serializers.SerializerMethodField()
    access_unaccept = serializers.SerializerMethodField()

    """Доступ"""
    class Meta:
        model = Access
        fields = '__all__'

    def get_access_accept(self, obj):
        return UserGetSerializer(obj.access_accept.all(), many=True).data

    def get_access_unaccept(self, obj):
        return UserGetSerializer(obj.access_unaccept.all(), many=True).data

class NewsSerializer(serializers.ModelSerializer):
    disease = PresentablePrimaryKeyRelatedField(queryset=Disease.objects.all(), presentation_serializer=DiseaseSerializer, required=False)
    center = PresentablePrimaryKeyRelatedField(queryset=Center.objects.all(), presentation_serializer=CenterSerializer, required=False)

    class Meta:
        model = News
        fields = '__all__'

    def create(self, validated_data):
        news = News.objects.create(**validated_data)
        if "disease" in validated_data and "center" in validated_data:
            news.disease = validated_data["disease"]
            news.center = validated_data["center"]
        elif "disease" in validated_data and "center" not in validated_data: 
            news.disease = validated_data["disease"]
        elif "center" in validated_data and "disease" not in validated_data:
            news.center = validated_data["center"]
        else:
            raise serializers.ValidationError("Center or disease should be specified!")
        return news

class NoteSerializer(serializers.ModelSerializer):
    user = PresentablePrimaryKeyRelatedField(queryset=User.objects.all(), presentation_serializer=UserGetSerializer, required=False)
    doctor = PresentablePrimaryKeyRelatedField(queryset=User.objects.all(), presentation_serializer=UserGetSerializer, required=False)
    center = PresentablePrimaryKeyRelatedField(queryset=Center.objects.all(), presentation_serializer=CenterSerializer, required=False)
    file = serializers.FileField()
    class Meta:
        model = Note
        fields = '__all__'

    def create(self, validated_data):
        self.create_validate(validated_data)
        note = Note.objects.create(**validated_data)
        note.user = validated_data["user"]
        note.doctor = validated_data["doctor"]
        note.center = validated_data["center"]
        return note

    def create_validate(self, validated_data):
        if "user" not in validated_data:
            return serializers.ValidationError("User not specified")
        if "doctor" not in validated_data:
            return serializers.ValidationError("Doctor not specified")
        if "center" not in validated_data:
            return serializers.ValidationError("Center not specified")

class ClinicSerializer(serializers.ModelSerializer):
    supported_diseases = serializers.SerializerMethodField()

    class Meta:
        model = Clinic
        fields = '__all__'

    def get_supported_diseases(self, obj):
        return DiseaseSerializer(obj.supported_diseases.all(), many=True).data


class SavedSerializer(serializers.ModelSerializer):
    ''' get serialier for saved model'''
    user = PresentablePrimaryKeyRelatedField(queryset=User.objects.all(), presentation_serializer=UserGetSerializer)
    news = PresentablePrimaryKeyRelatedField(queryset=News.objects.all(), presentation_serializer=NewsSerializer)

    class Meta:
        model = Saved
        fields = '__all__'



# like too up
class LikeSerializer(serializers.ModelSerializer):
    user = PresentablePrimaryKeyRelatedField(queryset=User.objects.all(), presentation_serializer=UserGetSerializer)
    news = PresentablePrimaryKeyRelatedField(queryset=News.objects.all(), presentation_serializer=NewsSerializer)

    class Meta:
        model = Like
        fields = '__all__'


class SearchSerializer(serializers.Serializer):
    clinics = ClinicSerializer(read_only=True, many=True)
    centers = CenterSerializer(read_only=True, many=True)
    users = UserGetSerializer(read_only=True, many=True)

    class Meta:
        fields = '__all__'


