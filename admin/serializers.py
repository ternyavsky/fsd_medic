

from django.core import cache
from rest_framework import serializers

from api.serializers import CenterSerializer, UserGetSerializer
from db.queries import get_users


class CenterProfileSerializer(serializers.Serializer):
    center = CenterSerializer(many=True)
    specialists = serializers.SerializerMethodField()
    pacients = serializers.SerializerMethodField()

    def get_specialists(self, obj):
        users = cache.get_or_set("users", get_users())
        # return DoctorSerializer
