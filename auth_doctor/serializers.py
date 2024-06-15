from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.transaction import atomic
from rest_framework import serializers

from api.models import City, Clinic, ClinicAdmin, Country
from .models import Doctor


from .models import Interview


class ClinicCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = [
            "number",
            "password",
            "workdays",
            "worktime",
        ]

    @transaction.atomic
    def create(self, validated_data):
        d = validated_data
        password = d.pop("password")
        clinic = Clinic.objects.create(
            password=make_password(password),
            **d,
        )
        return clinic


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
    """Упрвление собесами"""

    class Meta:
        model = Interview
        fields = "__all__"


class DoctorCreateSerializer(serializers.ModelSerializer):
    city = serializers.CharField()
    country = serializers.CharField()

    class Meta:
        model = Doctor
        fields = [
            "number",
            "first_name",
            "middle_name",
            "last_name",
            "city",
            "country",
            "center",
            "address",
            "specialization",
            "work_experience",
        ]


class DoctorVerifyResetCodeSerializer(serializers.Serializer):
    """Проверка кода для сброса пароля"""

    email = serializers.CharField(allow_null=True, required=False)
    number = serializers.CharField(allow_null=True, required=False)
    reset_code = serializers.IntegerField()


class DoctorNewPasswordSerializer(serializers.Serializer):
    """Устанавливаем новый пароль в разделе 'забыли пароль'"""

    email = serializers.CharField(allow_null=True, required=False)
    number = serializers.CharField(allow_null=True, required=False)
    password1 = serializers.CharField(min_length=8, max_length=128)
    password2 = serializers.CharField(min_length=8, max_length=128)

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data


class ClinicVerifyResetCodeSerializer(serializers.Serializer):
    """Проверка кода для сброса пароля"""

    email = serializers.CharField(allow_null=True, required=False)
    number = serializers.CharField(allow_null=True, required=False)
    reset_code = serializers.IntegerField()


class ClinicNewPasswordSerializer(serializers.Serializer):
    """Устанавливаем новый пароль в разделе 'забыли пароль'"""

    email = serializers.CharField(allow_null=True, required=False)
    number = serializers.CharField(allow_null=True, required=False)
    password1 = serializers.CharField(min_length=8, max_length=128)
    password2 = serializers.CharField(min_length=8, max_length=128)

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data
