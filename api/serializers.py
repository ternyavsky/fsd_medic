from rest_framework import serializers
from .models import News, User


class CreateUserSerializer(serializers.Serializer):
    def create(self, validated_data):
        self.create_validate(validated_data)
        return User.objects.create_user(number=validated_data['number'],
                                        password=validated_data['password1'])

    def update(self, instance, validated_data):
        self.update_validate(validated_data)
        instance.number = validated_data.get('number', instance.number)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.center = validated_data.get('center', instance.center)
        instance.disease = validated_data.get('disease', instance.desease)
        password = validated_data.get('password', instance.password1)
        instance.set_pssword(password)
        instance.save()
        return instance

    def create_validate(self, data):
        if User.objects.filter(number=data['number']).exists():
            raise serializers.ValidationError('Пользователь с таким номером уже существует')
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Пароли должны совподать')

    def update_validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Пароли должны совподать')
        try:
            email = data['email']
            if User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError('Почта уже используется')
        except:
            pass

    number = serializers.CharField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)


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

