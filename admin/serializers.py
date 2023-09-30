

from django.core import cache
from rest_framework import serializers

from api.serializers import CenterSerializer, UserGetSerializer, NoteSerializer
from db.queries import *
from datetime import date





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
        return users.filter(created_at__day=date.today().day).count()

    

class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User


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
        return UserGetSerializer(result, many=True).data 

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
        return UserGetSerializer(result, many=True).data 

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
