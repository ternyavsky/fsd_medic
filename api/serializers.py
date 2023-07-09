import json
import re
import random
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import News, User, NumberCodes, Centers, Clinics




class UserSerializer(serializers.Serializer):
    number = serializers.CharField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    center_id = serializers.IntegerField(required=False)
    disease_id = serializers.IntegerField(required=False)
    stage = serializers.IntegerField(read_only=True)
    group = serializers.CharField()



    def create(self, validated_data):
        self.create_validate(validated_data)
        code = self.context['request'].data.get('code')
        print(code, 'code from serializer')
        stage = self.context['request'].data.get('stage')
        user = None

        if stage == '1':
            user = User.objects.create_user(
                number=validated_data['number'],
                password=validated_data['password1'],
                group=validated_data['group']
            )
            user.stage = stage
            validated_data['stage'] = stage

        if stage == '2':
            center_id = validated_data.get('center_id')
            disease_id = validated_data.get('disease_id')

            if not center_id or not disease_id:
                raise serializers.ValidationError('center_id and disease_id are required for stage 2')

            try:
                user = User.objects.get(number=validated_data['number'])
                center = Centers.objects.get(id=center_id)
                user.center_id = center.id
                user.country = center.country
                user.disease_id = disease_id
                user.save()

            except User.DoesNotExist:
                raise serializers.ValidationError('User does not exist for stage 2')

            user.stage = stage
            validated_data['stage'] = stage

        if stage == '3':
            user = User.objects.get(number=validated_data['number'])
            validated_data['stage'] = stage
            user.save()

        return user

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
        number_pattern = re.compile(r'^\+[0-9]{10}$')
        password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]+$')

        stage = self.context['request'].data.get('stage')
        # print(type(stage), 'тип stage')
        if stage == '1':
            # Проверка Номера
            if User.objects.filter(number=data['number']).exists():
                raise serializers.ValidationError('Номер уже используется')

            # if not number_pattern.match(data['number']):
            #     raise serializers.ValidationError('Введен некорректный номер телефона')


            # Проверка паролей
            password1 = data.get('password1')
            password2 = data.get('password2')
            if password1 != password2:
                raise serializers.ValidationError({'password2': 'Пароли должны совпадать'})

            if not password_pattern.match(password1):
                raise serializers.ValidationError(
                    {'password1': 'Пароль должен состоять из цифр и букв обоих регистров'})

            if len(password1) < 8:
                raise serializers.ValidationError({'password1': 'Пароль должен быть не менее 8 символов'})


        if stage == '2':

        # Проверка присувствия данных
            if data['number'] is None:
                raise serializers.ValidationError('Введите номер')
            if data['password1'] is None:
                raise serializers.ValidationError('Введите пароль')
            elif data['password2'] is None:
                raise serializers.ValidationError('Подтвердите пароль')
            if data['center_id'] is None:
                raise serializers.ValidationError('Выберите центр')

            if data['disease_id'] is None:
                raise serializers.ValidationError('Выберите заболевания')



    def update_validate(self, data):
        if data['email'] is not None:
            if User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError('Почта уже используется')


class VerifyCodeSerializer(serializers.Serializer):
    number = serializers.CharField()
    verification_code = serializers.IntegerField()


class AdminSerializer(serializers.Serializer):
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
            raise serializers.ValidationError('Введите почту')
        if data['first_name'] is None:
            raise serializers.ValidationError('Введите Имя')
        if data['last_name'] is None:
            raise serializers.ValidationError('Введите Фамилию')
        if data['password1'] is None:
            raise serializers.ValidationError('Введите пароль')
        elif data['password2'] is None:
            raise serializers.ValidationError('Подтвердите пароль')
        # Проверка Почты
        if not email_pattern.match(data['email']):
            raise serializers.ValidationError('Введена некоректная почта')
        # Проверка Имени
        if not name_pattern.match(data['first_name']):
            raise serializers.ValidationError('Имя может состоять только из букв кирилицы')
        if len(data['first_name']) < 3:
            raise serializers.ValidationError('Имя не может быть кароче 3 символов')
        if len(data['first_name']) > 20:
            raise serializers.ValidationError('Имя не может быть длинее 20 символов')
        # Проверка Фамилии
        # Проверка телефона
        if User.objects.filter(number=data['number']).exists():
            raise serializers.ValidationError('Номер уже используется')

        if not name_pattern.match(data['last_name']):
            raise serializers.ValidationError('Фамилия может состоять только из букв кирилицы')
        if len(data['last_name']) < 3:
            raise serializers.ValidationError('Фамилия не может быть кароче 3 символов')
        if len(data['last_name']) > 30:
            raise serializers.ValidationError('Фамилия не может быть длинее 30 символов')
        # Проверка паролей
        if not password_pattern.match(data['password1']):
            raise serializers.ValidationError('Пароль должен состоять из цифр и букв обоих регистров')
        if len(data['password1']) < 8:
            raise serializers.ValidationError('Пароль не может быть кароче 8 символов')
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Пароли должны совподвать')

    def update_validate(self, data):
        pass

    number = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)


class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

    def create(self, validated_data):
        return News.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.center = validated_data.get('center', instance.center)
        instance.disease = validated_data.get('disease', instance.disease)
        instance.save()
        return instance


class ClinicSerializer(serializers.Serializer):
    class Meta:
        model = Clinics
        fields = '__all__'


class CenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Centers
        fields = '__all__'


class SearchSerializer(serializers.Serializer):
    clinics = ClinicSerializer(read_only=True, many=True)
    centers = CenterSerializer(read_only=True, many=True)
    users = UserGetSerializer(read_only=True, many=True)

    class Meta:
        fields = '__all__'
