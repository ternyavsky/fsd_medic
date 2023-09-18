from rest_framework import serializers

from api.models import Interview, User
from social.models import Chat

from rest_framework import status, exceptions
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .services.doctor_reg_services import doctor_reg_data_validate
from loguru import logger
from .models import Doctor

logger.add("logs/auth_doctor.log", format="{time} {level} {message}", level="DEBUG", rotation="12:00",
           compression="zip")


class DateTimeUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    datetime = serializers.DateTimeField()


class DoctorDataResponseSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=200)
    user_hash = serializers.CharField(max_length=200)


class VerificationCodeSerializer(serializers.Serializer):
    verification_code = serializers.CharField(max_length=10, required=True)
    user_hash = serializers.CharField(max_length=100, required=True)


class InterviewSerializer(serializers.ModelSerializer):
    '''Упрвление собесами'''

    class Meta:
        model = Interview
        fields = ['first_name', 'last_name', 'number', 'email']

    def create(self, validated_data):
        return Interview(**validated_data)

    def update(self, instance, validated_data):
        instance.number = validated_data.get('number', instance.number)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.group = validated_data.get('group', instance.group)

        return instance


class DoctorCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)

    class Meta:
        model = Doctor
        fields = [
            'phone_number',
            'first_name',
            'middle_name',
            'last_name',
            'city',
            'country',
            'center',
            'address',
            'specialization',
            'work_experience'
        ]

    def validate(self, data):
        doctor_reg_data_validate(data)
        return super().validate(data)
