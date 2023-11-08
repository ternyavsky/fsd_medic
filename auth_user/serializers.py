import logging
import re

from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenObtainSerializer
from django.core.cache import cache
from db.queries import get_users, get_centers
from api.models import Disease, Center, User
from social.models import Chat
from api.serializers import UserSerializer

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer, TokenObtainSerializer):

    # Overiding validate function in the TokenObtainSerializer  
    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
            'number': attrs["number"]
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        try:
            user = User.objects.get(number=authenticate_kwargs['number'])

            if user:
                auth = authenticate(**authenticate_kwargs)
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
        token["number"] = user.number 
        token["huy"] = "asd"
        return token


class CreateUserSerializer(serializers.Serializer):
    """Создание пользователей. Регистрация"""
    number = serializers.CharField(required=False)
    password1 = serializers.CharField(write_only=True, required=False)
    password2 = serializers.CharField(write_only=True, required=False)
    birthday = serializers.DateField(required=False)
    main_center = serializers.PrimaryKeyRelatedField(
        queryset=Center.objects.all(),
        allow_null=True,
        required=False,
        many=False
    )
    disease_id = serializers.PrimaryKeyRelatedField(
        queryset=Disease.objects.all(),
        allow_null=True,
        required=False,
        many=True
    )
    stage = serializers.IntegerField(read_only=True)
    group = serializers.CharField(required=False)
    def create(self, validated_data):
        self.create_validate(validated_data)
        request = self.context['request']
        session = request.session
        stage = self.context['request'].data.get('stage')
        stage = int(stage)

        user = None

        if stage == 1:
            user = User.objects.create_user(
                number=validated_data['number'],
                password=validated_data['password1'],
                group__name=validated_data['group'],
                birthday=validated_data['birthday']
            )
            user.stage = stage
            validated_data['stage'] = stage
            session["user"] = UserSerializer(user).data
        print(request.session["user"])
        if stage == 2:
            center = None
            user = User.objects.get(number=session["user"]["number"])
            print(user)
            if "main_center" not in validated_data:
                user.main_center = None
            else:
                center = validated_data["main_center"]
                user.main_center = validated_data["main_center"]
                center = get_centers(id=user.main_center.id).first()
                chat = Chat()
                chat.save()
                chat.users.add(user)
                chat.centers.add(center)
                chat.save()
           

            if center:
                user.country = center.country
            else:
                user.country = None
            if "disease_id" in validated_data:
                for i in validated_data['disease_id']:
                    user.disease.add(i)

                    if user.disease.count() >= 5:
                        raise serializers.ValidationError('You cannot specify more than 5 diseases')
            
            user.stage = stage
            validated_data['stage'] = stage
            user.save()
            session["user"] = UserSerializer(user).data
        print(request.session["user"])
        if stage == 3:
            try:
                user = User.objects.get(number=session["user"]["number"])
                validated_data['stage'] = stage
                user.save()
            except User.DoesNotExist:
                raise serializers.ValidationError('User does not exist for stage 3')
            session.clear()
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['disease_id'] = instance.disease.values_list('id', flat=True)
        return representation

    def update(self, validated_data):
        self.update_validate(validated_data)
        User.objects.update_user(validated_data['instance'], number=validated_data['number'],
                                 email=validated_data['email'],
                                 password=validated_data['password1'],
                                 first_name=validated_data['first_name'], last_name=validated_data['last_name'],
                                 surname=validated_data['surname'],
                                 center_id=validated_data['center_id'],
                                 disease_id=validated_data['disease_id'])
        return validated_data['instance']

    def create_validate(self, data):
        password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]+$')
        stage = self.context['request'].data.get('stage')

        if stage == '1':
            # Проверка Номера
            if get_users(number=data['number']).exists():
                raise serializers.ValidationError('Number already in use')

            password1 = data.get('password1')
            password2 = data.get('password2')
            if password1 != password2:
                raise serializers.ValidationError({'password': 'passwords must match'})
            if not password_pattern.match(password1):
                raise serializers.ValidationError(
                    {'password': 'The password must consist of numbers and letters of both cases'})

            if len(password1) < 8:
                raise serializers.ValidationError({'password': 'Password must be at least 8 characters'})

        if stage == '2':

            # Проверка присувствия данных
            if data['number'] is None:
                raise serializers.ValidationError('Enter number')
            if data['password1'] is None:
                raise serializers.ValidationError('Enter password')
            elif data['password2'] is None:
                raise serializers.ValidationError('Confirm the password')

    def update_validate(self, data):
        if data['email'] is not None:
            if User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError('Email already in use')


# sms code block ##
class VerifyCodeSerializer(serializers.Serializer):
    """Отправка кода для проверки. Регистрация"""
    number = serializers.CharField()
    verification_code = serializers.IntegerField()


class ResendCodeSerializer(serializers.Serializer):
    """Переотправка смс кода в разделе 'отправить код снова'. Регистрация."""
    number = serializers.CharField()




class VerifyResetCodeSerializer(serializers.Serializer):
    """Проверка кода для сброса пароля"""
    email = serializers.CharField(allow_null=True, required=False)
    number = serializers.CharField(allow_null=True, required=False)
    reset_code = serializers.IntegerField()


class NewPasswordSerializer(serializers.Serializer):
    """Устанавливаем новый пароль в разделе 'забыли пароль' """
    email = serializers.CharField(allow_null=True, required=False)
    number = serializers.CharField(allow_null=True, required=False)
    password1 = serializers.CharField(min_length=8, max_length=128)
    password2 = serializers.CharField(min_length=8, max_length=128)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data


## email block
class EmailBindingSerializer(serializers.Serializer):
    """Привязка email к аккаунту. Шаг 1 - отправка письма"""
    email = serializers.CharField()

    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": 'Email already in use'})
        return data


class VerifyEmailCodeSerializer(serializers.Serializer):
    email = serializers.CharField()
    email_verification_code = serializers.IntegerField()


# end block#

class AdminSerializer(serializers.Serializer):
    """создаем админа"""

    def create(self, validated_data):
        self.create_validate(validated_data)
        return User.objects.create_superuser(number=validated_data['number'],
                                             email=validated_data['email'],
                                             first_name=validated_data['first_name'],
                                             last_name=validated_data['last_name'],
                                             password=validated_data['password1'])

    def update(self, validated_data):
        pass

    def create_validate(self, data):
        number_pattern = re.compile('^[+]+[0-9]+$')
        email_pattern = re.compile('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        name_pattern = re.compile('^[а-яА-Я]+$')
        password_pattern = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]+$')
        if data['email'] is None:
            raise serializers.ValidationError('Enter email')
        if data['first_name'] is None:
            raise serializers.ValidationError('Enter firstname')
        if data['last_name'] is None:
            raise serializers.ValidationError('Enter lastname')
        # Проверка Почты
        if not email_pattern.match(data['email']):
            raise serializers.ValidationError('The email entered is incorrect')

        if len(data['first_name']) < 2:
            raise serializers.ValidationError('firstname cannot be shorter than 2 characters')
        if len(data['first_name']) > 20:
            raise serializers.ValidationError('firstname cannot be longer than 20 characters')
        # Проверка Фамилии
        # Проверка телефона
        if User.objects.filter(number=data['number']).exists():
            raise serializers.ValidationError('Номер уже используется')
        if len(data['last_name']) < 3:
            raise serializers.ValidationError('Фамилия не может быть короче 3 символов')
        if len(data['last_name']) > 30:
            raise serializers.ValidationError('Фамилия не может быть длиннее 30 символов')
        # Проверка паролей
        if len(data['password1']) < 8:
            raise serializers.ValidationError('Пароль не может быть короче 8 символов')
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Пароли должны совпадать')

    def update_validate(self, data):
        pass

    number = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
