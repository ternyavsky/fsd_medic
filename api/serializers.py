from rest_framework import serializers
from rest_framework.fields import empty

from auth_doctor.models import Doctor
from .models import News, User, Center, Clinic, Disease, Note, Saved, Like, Country, Access, City


class CountrySerializer(serializers.ModelSerializer):
    """Страны"""

    class Meta:
        model = Country
        fields = '__all__'
        depth = 1


class CitySerializer(serializers.ModelSerializer):
    """Города"""

    class Meta:
        model = City
        fields = '__all__'
        depth = 1
class CenterSerializer(serializers.ModelSerializer):
    """Клиники"""

    class Meta:
        model = Center
        fields = '__all__'
        depth = 1


class DiseaseSerializer(serializers.ModelSerializer):
    """Болезни"""

    class Meta:
        model = Disease
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Получаем пользователя(аккаунт и т.п)"""  

    def __init__(self, *args, **kwargs):
        self.depth = kwargs.pop("depth", 1)
        self.Meta.depth = self.depth
        super(UserSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = '__all__'


class AccessSerializer(serializers.ModelSerializer):
    """Доступ"""

    class Meta:
        model = Access
        fields = '__all__'
        depth = 1


class NewsPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['image', 'title', 'created_at']


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        news = News.objects.create(**validated_data)
        if "disease" in validated_data and "center" in validated_data:
            news.disease = validated_data["disease"]
            news.center = validated_data["center"]
        elif "disease" in validated_data and "center" not in validated_data:
            news.disease = validated_data["disease"]
        elif "center" in validated_data and "disease" not in validated_data:
            news.center = validated_data["center"]
        else:
            raise serializers.ValidationError(
                "Center or disease should be specified!")
        return news


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        self.create_validate(validated_data)
        note = Note.objects.create(**validated_data)
        note.user = validated_data["user"]
        note.doctor = validated_data["doctor"]
        note.center = validated_data["center"]
        return note

    def create_validate(self, validated_data):
        if "user" not in validated_data:
            return serializers.ValidationError("User not specified")
        if "doctor" not in validated_data:
            return serializers.ValidationError("Doctor not specified")
        if "center" not in validated_data:
            return serializers.ValidationError("Center not specified")


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'
        depth = 1


class DoctorGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = "__all__"
        depth = 1


class SearchSerializer(serializers.Serializer):
    doctors = DoctorGetSerializer(read_only=True, many=True)
    clinics = ClinicSerializer(read_only=True, many=True)
    centers = CenterSerializer(read_only=True, many=True)


class SavedSerializer(serializers.ModelSerializer):
    ''' get serialier for saved model'''

    class Meta:
        model = Saved
        fields = '__all__'
        depth = 1


# like too up
class LikeSerializer(serializers.ModelSerializer):
    ''' get serializer for saved model'''

    class Meta:
        model = Like
        fields = '__all__'
        depth = 1
