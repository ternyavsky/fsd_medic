from datetime import date

from django.core.cache import cache
from rest_framework import serializers

from api.serializers import UserSerializer, NoteSerializer, AccessSerializer
from db.queries import *



class CityProfileSerializer(serializers.ModelSerializer):
    quant_centers = serializers.SerializerMethodField()
    quant_centers_today = serializers.SerializerMethodField()
    quant_clinics = serializers.SerializerMethodField()
    quant_clinics_today = serializers.SerializerMethodField()
    quant_users = serializers.SerializerMethodField()
    quant_users_today = serializers.SerializerMethodField()


    class Meta:
        model = City
        fields = "__all__"

    def get_quant_centers(self, obj):
        return obj.quant_centers

    def get_quant_centers_today(self, obj):
        return obj.quant_centers_today

    def get_quant_clinics(self, obj):
        return obj.quant_clinics

    def get_quant_clinics_today(self, obj):
        return obj.quant_clinics_today

    def get_quant_users(self, obj):
        return obj.quant_users

    def get_quant_users_today(self, obj):
        return obj.quant_users_today


class CountryProfileSerializer(serializers.ModelSerializer):
    quant_clinics = serializers.SerializerMethodField()
    quant_clinics_today = serializers.SerializerMethodField()
    quant_users = serializers.SerializerMethodField()
    quant_users_today = serializers.SerializerMethodField()
    quant_doctors = serializers.SerializerMethodField()
    quant_doctors_today = serializers.SerializerMethodField()
    quant_use_site = serializers.SerializerMethodField()
    quant_use_site_today = serializers.SerializerMethodField()

    def get_quant_clinics(self, obj):
        return obj.quant_clinics

    def get_quant_clinics_today(self, obj):
        return obj.quant_clinics_today

    def get_quant_users(self, obj):
        return obj.quant_users

    def get_quant_users_today(self, obj):
        return obj.quant_users_today

    def get_quant_doctors(self, obj):
        return obj.quant_doctors

    def get_quant_doctors_today(self, obj):
        return obj.quant_doctors_today

    def get_quant_use_site(self, obj):
        return obj.quant_users

    def get_quant_use_site_today(self, obj):
        return obj.quant_users_today

    class Meta:
        model = Country
        fields = "__all__"


class CountryCitySerializer(serializers.Serializer):
    cities = CityProfileSerializer(many=True, read_only=True)
    country = CountryProfileSerializer(read_only=True, many=True)


class DiseasePacientSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = Disease
        fields = "__all__"

    def get_count(self, obj):
        return obj.most_count
    
    
class AgeSerializer(serializers.Serializer):
    man = serializers.IntegerField()
    woman = serializers.IntegerField()

class MainPageSerializer(serializers.Serializer):
    _10_20 = AgeSerializer(many=True, read_only=True)
    _20_30 = AgeSerializer(many=True, read_only=True)
    _30_40 = AgeSerializer(many=True, read_only=True)
    _40_50 = AgeSerializer(many=True, read_only=True)
    _50_60 = AgeSerializer(many=True, read_only=True)
    _60_70 = AgeSerializer(many=True, read_only=True)
    diseases = DiseasePacientSerializer(read_only=True, many=True)
    created_today = serializers.IntegerField()


class UserProfileSerializer(serializers.Serializer):
    user = UserSerializer(many=True, read_only=True)
    curr_notes = NoteSerializer(many=True, read_only=True)
    process_notes = NoteSerializer(many=True, read_only=True)
    miss_notes = NoteSerializer(many=True, read_only=True)
    access = AccessSerializer(many=True, read_only=True)


class CenterProfileSerializer(serializers.ModelSerializer):
    online_notes = serializers.SerializerMethodField()
    offline_notes = serializers.SerializerMethodField()
    visit_online = serializers.SerializerMethodField()
    visit_offline = serializers.SerializerMethodField()


    class Meta:
        model = Center
        fields = "__all__"

    def get_online_notes(self, obj):
        return obj.online_notes

    def get_offline_notes(self, obj):
        return obj.offline_notes

    def get_visit_online(self, obj):
        return obj.visit_online

    def get_visit_offline(self, obj):
        return obj.visit_offline


class CenterUserProfileSerializer(serializers.Serializer):
    center = CenterProfileSerializer(many=True, read_only=True)
    pacients = UserSerializer(many=True, read_only=True)

class ClinicProfileSerializer(serializers.ModelSerializer):
    online_notes = serializers.SerializerMethodField()
    offline_notes = serializers.SerializerMethodField()
    visit_online = serializers.SerializerMethodField()
    visit_offline = serializers.SerializerMethodField()

    class Meta:
        model = Clinic
        fields = "__all__"


    def get_online_notes(self, obj):
        return obj.online_notes

    def get_offline_notes(self, obj):
        return obj.offline_notes

    def get_visit_online(self, obj):
        return obj.visit_online

    def get_visit_offline(self, obj):
        return obj.visit_offline


class ClinicUserProfileSerializer(serializers.Serializer):
    clinic = ClinicProfileSerializer(many=True, read_only=True)
    pacients = UserSerializer(many=True, read_only=True)
