from rest_framework import serializers

from api.models import Clinic, Country, City
from .models import Interview
from social.models import Chat
from api.serializers import CenterSerializer, CountrySerializer
from rest_framework import status, exceptions
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import Doctor





class ClinicCreateSerializer(serializers.ModelSerializer):
    city = serializers.CharField()
    country = serializers.CharField()
    class Meta:
        model = Clinic
        fields = [
            'name',
            'description',
            'number',
            'email',
            'supported_diseases',
            'country',
            'city',
            'address',
            'center'
        ]





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
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.group = validated_data.get('group', instance.group)

        return instance


class DoctorCreateSerializer(serializers.ModelSerializer):
    city = serializers.CharField()
    country = serializers.CharField()
    class Meta:
        model = Doctor
        fields = [
            'number',
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


class DoctorPasswordResetSerializer(serializers.Serializer):
    """Сброс пароля. Этап отправки сообщения """
    number = serializers.CharField(allow_null=True, required=False)
    email = serializers.CharField(allow_null=True, required=False)

    def create(self, validated_data):
        number = self.context['request'].data.get('number')
        #email validate pydantic class
        email = self.context['request'].data.get('email')
        doctor = None
        if number:
            try:
                doctor = Doctor.objects.get(number=validated_data['number'])
            except Doctor.DoesNotExist:
                raise serializers.ValidationError('Doctor does not have a number')
        if email:
            try:
                doctor = Doctor.objects.get(email=validated_data['email'])
            except Doctor.DoesNotExist:
                raise serializers.ValidationError('Doctor does not have an email')
        return doctor

class DoctorVerifyResetCodeSerializer(serializers.Serializer):
    """Проверка кода для сброса пароля"""
    email = serializers.CharField(allow_null=True, required=False)
    number = serializers.CharField(allow_null=True, required=False)
    reset_code = serializers.IntegerField()

class DoctorNewPasswordSerializer(serializers.Serializer):
    """Устанавливаем новый пароль в разделе 'забыли пароль' """
    email = serializers.CharField(allow_null=True, required=False)
    number = serializers.CharField(allow_null=True, required=False)
    password1 = serializers.CharField(min_length=8, max_length=128)
    password2 = serializers.CharField(min_length=8, max_length=128)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data


class ClinicPasswordResetSerializer(serializers.Serializer):
    """Сброс пароля. Этап отправки сообщения """
    number = serializers.CharField(allow_null=True, required=False)
    email = serializers.CharField(allow_null=True, required=False)

    def create(self, validated_data):
        number = self.context['request'].data.get('number')
        #email validate pydantic class
        email = self.context['request'].data.get('email')
        clinic = None
        if number:
            try:
                clinic = Clinic.objects.get(number=validated_data['number'])
            except Clinic.DoesNotExist:
                raise serializers.ValidationError('Clinic does not have a number')
        if email:
            try:
                Clinic = Clinic.objects.get(email=validated_data['email'])
            except Clinic.DoesNotExist:
                raise serializers.ValidationError('Clinic does not have an email')
        return clinic

class ClinicVerifyResetCodeSerializer(serializers.Serializer):
    """Проверка кода для сброса пароля"""
    email = serializers.CharField(allow_null=True, required=False)
    number = serializers.CharField(allow_null=True, required=False)
    reset_code = serializers.IntegerField()

class ClinicNewPasswordSerializer(serializers.Serializer):
    """Устанавливаем новый пароль в разделе 'забыли пароль' """
    email = serializers.CharField(allow_null=True, required=False)
    number = serializers.CharField(allow_null=True, required=False)
    password1 = serializers.CharField(min_length=8, max_length=128)
    password2 = serializers.CharField(min_length=8, max_length=128)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
