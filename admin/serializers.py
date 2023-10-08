from datetime import date

from django.core.cache import cache
from rest_framework import serializers

from api.serializers import UserSerializer, NoteSerializer
from db.queries import *


class CityProfileSerializer(serializers.ModelSerializer):
    quant_centers = serializers.SerializerMethodField()
    quant_centers_today = serializers.SerializerMethodField()
    quant_clinics = serializers.SerializerMethodField()
    quant_clinics_today = serializers.SerializerMethodField()
    quant_users = serializers.SerializerMethodField()
    quant_users_today = serializers.SerializerMethodField()

    # quant_interview = serializers.SerializerMethodField()
    # quant_interview_today = serializers.SerializerMethodField()
    # quant_lid = serializers.SerializerMethodField()
    # quant_lid_today = serializers.SerializerMethodField()

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
        depth = 1


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


class MainPageSerializer(serializers.Serializer):
    diseases = DiseasePacientSerializer(read_only=True, many=True)
    ucreated_today = serializers.SerializerMethodField()

    def get_ucreated_today(self, obj):
        users = cache.get_or_set("users", get_users())
        return users.filter(created_at__date=date.today()).count()


class UserProfileSerializer(serializers.Serializer):
    users = UserSerializer(many=True, read_only=True)
    curr_notes = NoteSerializer(many=True, read_only=True)
    process_notes = NoteSerializer(many=True, read_only=True)


class CenterProfileSerializer(serializers.ModelSerializer):
    pacients = serializers.SerializerMethodField()
    total_notes = serializers.SerializerMethodField()
    reject_notes = serializers.SerializerMethodField()
    pass_notes = serializers.SerializerMethodField()
    visit_online = serializers.SerializerMethodField()
    visit_offline = serializers.SerializerMethodField()

    class Meta:
        model = Center
        fields = "__all__"
        depth = 1

    def get_pacients(self, obj):
        users = cache.get_or_set("users", get_users())
        users_mainc = users.filter(main_center__id=obj.id)
        users_centers = users.filter(centers__id=obj.id)
        result = users_mainc.union(users_centers)
        return UserSerializer(result, many=True).data

    def get_total_notes(self, obj):
        return obj.total_notes

    def get_reject_notes(self, obj):
        return obj.reject_notes

    def get_pass_notes(self, obj):
        return obj.pass_notes

    def get_visit_online(self, obj):
        return obj.visit_online

    def get_visit_offline(self, obj):
        return obj.visit_offline


class ClinicProfileSerializer(serializers.ModelSerializer):
    pacients = serializers.SerializerMethodField()
    total_notes = serializers.SerializerMethodField()
    reject_notes = serializers.SerializerMethodField()
    pass_notes = serializers.SerializerMethodField()
    visit_online = serializers.SerializerMethodField()
    visit_offline = serializers.SerializerMethodField()

    class Meta:
        model = Clinic
        fields = "__all__"
        depth = 1

    def get_pacients(self, obj):
        users = cache.get_or_set("users", get_users())
        result = users.filter(clinic=obj)
        return UserSerializer(result, many=True).data

    def get_total_notes(self, obj):
        return obj.total_notes

    def get_reject_notes(self, obj):
        return obj.reject_notes

    def get_pass_notes(self, obj):
        return obj.pass_notes

    def get_visit_online(self, obj):
        return obj.visit_online

    def get_visit_offline(self, obj):
        return obj.visit_offline
