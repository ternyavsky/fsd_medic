import json
import re
import random

from rest_framework import serializers

from .models import News, User, NumberCodes, Centers, Clinics, Disease, Notes, Saved, Like

from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField


class CreateUserSerializer(serializers.Serializer):
    """Создание пользователей. Регистрация"""
    number = serializers.CharField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    center_id = serializers.IntegerField(allow_null=True, required=False)
    disease_id = serializers.PrimaryKeyRelatedField(
        queryset=Disease.objects.all(),
        allow_null=True,
        required=False,
        many=True
    )
    stage = serializers.IntegerField(read_only=True)
    group = serializers.CharField()



    def create(self, validated_data):
        self.create_validate(validated_data)
        code = self.context['request'].data.get('code')
        stage = self.context['request'].data.get('stage')
        stage = int(stage)

        user = None

        if stage == 1:
            user = User.objects.create_user(
                number=validated_data['number'],
                password=validated_data['password1'],
                group=validated_data['group']
            )
            user.stage = stage
            validated_data['stage'] = stage

        if stage == 2:
            center_id = validated_data.get('center_id')

            user = User.objects.get(number=validated_data['number'])
            try:
                center = Centers.objects.get(id=center_id)
                user.center_id = center.id
                user.country = center.country
            except Centers.DoesNotExist:
                user.center_id = None
            for i in validated_data['disease_id']:
                user.disease.add(i)

                if user.disease.count() >= 5:
                    raise serializers.ValidationError('You cannot specify more than 5 diseases')
                print(validated_data['disease_id'], ' test_data')


            user.stage = stage
            validated_data['stage'] = stage
            user.save()

        if stage == 3:
            try:
                user = User.objects.get(number=validated_data['number'])
                validated_data['stage'] = stage
                user.save()
            except User.DoesNotExist:
                raise serializers.ValidationError('User does not exist for stage 3')

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
        number_pattern = re.compile(r'^\+[0-9]{10}$')
        password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]+$')

        stage = self.context['request'].data.get('stage')
        # print(type(stage), 'тип stage')
        if stage == '1':
            # Проверка Номера
            if User.objects.filter(number=data['number']).exists():
                raise serializers.ValidationError('Номер уже используется')

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
            # if data['center_id'] is None:
            #     raise serializers.ValidationError('Выберите центр')
            #
            # if data['disease_id'] is None:
            #     raise serializers.ValidationError('Выберите заболевания')



    def update_validate(self, data):
        if data['email'] is not None:
            if User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError('Почта уже используется')


class VerifyCodeSerializer(serializers.Serializer):
    """Отправка кода для проверки. Регистрация"""
    number = serializers.CharField()
    verification_code = serializers.IntegerField()



class ResendCodeSerializer(serializers.Serializer):
    """Переотправка смс кода в разделе 'отправить код снова'. Регистрация."""
    number = serializers.CharField()


# RESET PASSWORD BLOCK
class PasswordResetSerializer(serializers.Serializer):
    """Сброс пароля. Этап отправки сообщения """
    number = serializers.CharField(allow_null=True, required=False)
    email = serializers.CharField(allow_null=True, required=False)


    def create(self, validated_data):
        number = self.context['request'].data.get('number')
        email = self.context['request'].data.get('email')
        user = None
        if number:
            try:
                user = User.objects.get(number=validated_data['number'])
                user.save()
            except User.DoesNotExist:
                raise serializers.ValidationError('User does not have a number')
        if email:
            try:
                user = User.objects.get(email=validated_data['email'])
            except User.DoesNotExist:
                raise serializers.ValidationError('User does not have an email')
        return user

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

#END RESET PASSWORD BLOCK

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


class CenterSerializer(serializers.ModelSerializer):
    """Клиники"""
    class Meta:
        model = Centers
        fields = '__all__'


class DiseaseSerializer(serializers.ModelSerializer):
    """Болезни"""
    class Meta:
        model = Disease
        fields = '__all__'


class UserGetSerializer(serializers.ModelSerializer):

    """Получаем пользователя(аккаунт и т.п)"""
    disease = DiseaseSerializer(many=True, allow_null=True, required=False)
    center = serializers.SerializerMethodField()
    password = serializers.CharField(allow_null=True, required=False) #убираем обяз. поле password
    group = serializers.CharField(allow_null=True, required=False) #убираем обяз. поле group
    class Meta:
        model = User
        fields = '__all__'

    def get_center(self, obj):
        if obj.center:
            return CenterSerializer(Centers.objects.get(id=obj.center.id)).data
        return None

## Email Block
class EmailBindingSerializer(serializers.Serializer):
    """Привязка email к аккаунту. Шаг 1 - отправка письма"""
    email = serializers.CharField()
    def validate(self,data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email":'Почта уже используется'})

class VerifyEmailCodeSerializer(serializers.Serializer):
    email_verification_code = serializers.IntegerField()
## end email block ##

#END USER BLOCK


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

class NoteSerializer(serializers.ModelSerializer):
    users_to_note = UserGetSerializer(many=True)
    doctor = UserGetSerializer()
    center = CenterSerializer
    class Meta:
        model = Notes
        fields = ['users_to_note', 'doctor', 'center', 'translate', 'translate_from', 'translate_to','title',
        'online','notify', 'problem', 'duration_note', 'file','created_at','updated_at', 'status']




class ClinicSerializer(serializers.ModelSerializer):
    supported_diseases = serializers.SerializerMethodField()
    class Meta:
        model = Clinics
        fields = '__all__'

    def get_supported_diseases(self, obj):
        return DiseaseSerializer(obj.supported_diseases.all(), many=True).data



class SavedSerializer(serializers.ModelSerializer):
    ''' get serialier for saved model'''
    user = UserGetSerializer()
    news = NewsSerializer()
    class Meta:
        model = Saved 
        fields = '__all__'



#like too up
class LikeSerializer(serializers.ModelSerializer):
    user = UserGetSerializer()
    news = NewsSerializer()
    class Meta:
        model = Like 
        fields = '__all__'


class SearchSerializer(serializers.Serializer):

    clinics = ClinicSerializer(read_only=True, many=True)
    centers = CenterSerializer(read_only=True, many=True)
    users = UserGetSerializer(read_only=True, many=True)

    class Meta:
        fields = '__all__'


