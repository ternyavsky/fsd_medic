import re
from rest_framework import serializers

from api.models import Disease, Centers, User
from social.models import Chat


class CreateUserSerializer(serializers.Serializer):
    """Создание пользователей. Регистрация"""
    number = serializers.CharField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    main_center = serializers.PrimaryKeyRelatedField(
        queryset=Centers.objects.all(),
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
    group = serializers.CharField()

    def create(self, validated_data):
        self.create_validate(validated_data)
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
            print(type(validated_data["main_center"]), validated_data["main_center"])
            user = User.objects.get(number=validated_data['number'])
            user.main_center = validated_data["main_center"]
            user.country = user.main_center.country
            if "disease_id" in validated_data:
                print(validated_data["disease_id"])
                for i in validated_data['disease_id']:
                    user.disease.add(i)

                    if user.disease.count() >= 5:
                        raise serializers.ValidationError('You cannot specify more than 5 diseases')

            chat = Chat.objects.create(
                to_user=user,
                from_center=user.main_center
            )
            chat.save()
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
        password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]+$')
        stage = self.context['request'].data.get('stage')

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


    def update_validate(self, data):
        if data['email'] is not None:
            if User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError('Почта уже используется')

# sms code block ##
class VerifyCodeSerializer(serializers.Serializer):
    """Отправка кода для проверки. Регистрация"""
    number = serializers.CharField()
    verification_code = serializers.IntegerField()

class ResendCodeSerializer(serializers.Serializer):
    """Переотправка смс кода в разделе 'отправить код снова'. Регистрация."""
    number = serializers.CharField()

# password-reset block#
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

## email block
class EmailBindingSerializer(serializers.Serializer):
    """Привязка email к аккаунту. Шаг 1 - отправка письма"""
    email = serializers.CharField()

    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": 'Почта уже используется'})
        return data

class VerifyEmailCodeSerializer(serializers.Serializer):
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
