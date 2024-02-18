import logging
import re

from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenObtainSerializer
from django.core.cache import cache
from db.queries import get_users, get_centers, get_cities, get_doctors
from api.models import Disease, Center, User, Subscribe, Country
from social.models import Chat
from api.serializers import UserSerializer, CountrySerializer
from api.backends import user_authenticate

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer, TokenObtainSerializer):

    # Overiding validate function in the TokenObtainSerializer  
    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        if "number" in attrs:
            authenticate_kwargs["number"] = attrs["number"]
        elif "email" in attrs:
            authenticate_kwargs["email"] = attrs["email"]

        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        try:
            user = None
            if "email" in authenticate_kwargs:
                user = User.objects.get(email=authenticate_kwargs['email'])
            elif "number" in authenticate_kwargs:
                user = User.objects.get(number=authenticate_kwargs['number'])
            if user:
                print(authenticate_kwargs)
                authenticate_kwargs.pop("request")
                auth = user_authenticate(**authenticate_kwargs)
                if auth is None:
                    self.error_messages['no_active_account'] = _(
                        'Incorrect password'
                    )
                logger.info("Incorrect password")
        except User.DoesNotExist:
            self.error_messages['no_active_account'] = _(
                'Account does not exist')
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )

        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["type"] = "user"
        token["number"] = user.number
        return token


class CreateUserSerializer(serializers.Serializer):
    '''Регистрация'''
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    country = serializers.CharField()

    def create(self, validated_data):
        self.create_validate(validated_data)
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data['password'],
        )
        user.country = Country.objects.get(name="Узбекистан")
        user.save()
        main_doctor = get_doctors(country="Узбекистан", main_status=True).first()
        Subscribe.objects.create(user=user, main_doctor=main_doctor)
        # Chat create with mdoctor
        return user

    def create_validate(self, validated_data):
        password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]+$')
        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError('Email already in use')
        if not password_pattern.match(validated_data['password']):
            raise serializers.ValidationError(
                {'password': 'The password must consist of numbers and letters of both cases'})
        if len(validated_data['password']) < 8:
            raise serializers.ValidationError({'password': 'Password must be at least 8 characters'})


# sms code block ##
class VerifyCodeSerializer(serializers.Serializer):
    """Отправка кода для проверки. Регистрация"""
    email = serializers.CharField()
    verification_code = serializers.IntegerField()


class ResendCodeSerializer(serializers.Serializer):
    """Переотправка смс кода в разделе 'отправить код снова'. Регистрация."""
    email = serializers.CharField()


class VerifyResetCodeSerializer(serializers.Serializer):
    """Проверка кода для сброса пароля"""
    email = serializers.CharField(allow_null=True, required=False)
    number = serializers.CharField(allow_null=True, required=False)
    reset_code = serializers.IntegerField()


class NewPasswordSerializer(serializers.Serializer):
    """Устанавливаем новый пароль в разделе 'забыли пароль' """
    email = serializers.CharField(allow_null=True, required=False)
    number = serializers.CharField(allow_null=True, required=False)
    password2 = serializers.CharField(min_length=8, max_length=128)


## number bind block
class NumberBindingSerializer(serializers.Serializer):
    """Привязка номера к аккаунту. Шаг 1 - отправка смс """
    number = serializers.CharField()

    def validate(self, data):
        if User.objects.filter(number=data['number']).exists():
            raise serializers.ValidationError({"number": 'Number already in use'})
        return data


class VerifyNumberCodeSerializer(serializers.Serializer):
    number = serializers.CharField()
    number_verification_code = serializers.IntegerField()


# end block#

class AdminSerializer(serializers.Serializer):
    """создаем админа"""

    def create(self, validated_data):
        self.create_validate(validated_data)
        return User.objects.create_superuser(email=validated_data['email'],
                                             first_name=validated_data['first_name'],
                                             last_name=validated_data['last_name'],
                                             password=validated_data['password'])

    def create_validate(self, data):
        number_pattern = re.compile('^[+]+[0-9]+$')
        email_pattern = re.compile('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if data['email'] is None:
            raise serializers.ValidationError('Enter email')
        if data['first_name'] is None:
            raise serializers.ValidationError('Enter firstname')
        if data['last_name'] is None:
            raise serializers.ValidationError('Enter lastname')
        # Проверка Почты
        if not email_pattern.match(data['email']):
            raise serializers.ValidationError('The email entered is incorrect')

        if len(data['first_name']) < 1:
            raise serializers.ValidationError('firstname cannot be shorter than 1 characters')
        if len(data['first_name']) > 20:
            raise serializers.ValidationError('firstname cannot be longer than 20 characters')
        # Проверка Фамилии
        # Проверка телефона
        if User.objects.filter(number=data['number']).exists():
            raise serializers.ValidationError('Number already in use')
        if len(data['last_name']) < 1:
            raise serializers.ValidationError('Lastname cannot be shorter than 1 char')
        if len(data['last_name']) > 30:
            raise serializers.ValidationError('Lastname cannot be longer than 30 char')

    def update_validate(self, data):
        pass

    # number = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True)
