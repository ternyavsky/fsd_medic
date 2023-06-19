import re

from rest_framework import serializers
from .models import News, User, Interviews


class UserSerializer(serializers.Serializer):
    def create(self, validated_data):
        return User.objects.create_user(
            number=validated_data['number'],
            password=validated_data['password1'],
            is_patient=validated_data['is_patient'],
            center_id=validated_data['center_id'],
            disese_id=validated_data['disease_id'],
            group_name=validated_data['group_name']
        )

    def update(self, validated_data):
        self.update_validate(validated_data)
        User.objects.update_user(validated_data['instance'], number=validated_data['number'],
                                 email=validated_data['email'],
                                 password=validated_data['password1'],
                                 first_name=validated_data['first_name'], last_name=validated_data['last_name'],
                                 surname=validated_data['surname'],
                                 center_id=validated_data['center_id'], is_patient=validated_data['is_patient'],
                                 disease_id=validated_data['disease_id'])
        return validated_data['instance']

    def create_validate(self, data):
        number_pattern = re.compile('^[+]+[0-9]+$')
        email_pattern = re.compile('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        name_pattern = re.compile('^[а-яА-Я]+$')
        password_pattern = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]+$')

        # Проверка присувствия данных
        if data['number'] is None:
            raise serializers.ValidationError('Введите номер')
        if data['password1'] is None:
            raise serializers.ValidationError('Введите пароль')
        elif data['password2'] is None:
            raise serializers.ValidationError('Подтвердите пароль')
        if data['center_id'] is None:
            raise serializers.ValidationError('Выберите центр')
        if data['is_patient'] is None:
            data['is_patient'] = None
        if data['disease_id'] is None:
            data['disease_id'] = None
        if data['group_name'] == 'Пользователи':
            # Проверка Номера
            if not number_pattern.match(data['number']):
                raise serializers.ValidationError('Введен неоректный номер телефона')
            if User.objects.filter(number=data['number']).exists() or Interviews.objects.filter(
                    number=data['number']).exists():
                raise serializers.ValidationError('Номер уже используется')
            # Проверка паролей
            if not password_pattern.match(data['password1']):
                raise serializers.ValidationError('Пароль должен состоять из цифр и букв обоих регистров')
            if len(data['password1']) < 8:
                raise serializers.ValidationError('Пароль не может быть кароче 8 символов')
            if data['password1'] != data['password2']:
                raise serializers.ValidationError('Пароли должны совподать')

    def update_validate(self, data):
        if data['email'] is not None:
            if User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError('Почта уже используется')

    number = serializers.CharField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    is_patient = serializers.IntegerField()
    center_id = serializers.IntegerField()
    disease_id = serializers.IntegerField()
    group_name = serializers.CharField()


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
