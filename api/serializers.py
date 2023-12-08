from rest_framework import serializers
from rest_framework.fields import empty
from social.serializers import UnreadMsgSerializer
from social.models import UnreadMessage
from auth_doctor.models import Doctor
from .models import News, User, Center, Clinic, Disease, Note, Saved, Like, Country, Access, City
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField

class CountrySerializer(serializers.ModelSerializer):
    """Страны"""

    class Meta:
        model = Country
        fields = '__all__'
        depth = 1

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
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

    unread_messages = serializers.SerializerMethodField()

    class Meta:
        model = Center
        fields = '__all__'
        depth = 1

    def get_unread_messages(self, obj):
        queryset = UnreadMessage.objects.filter(center=obj)
        return UnreadMsgSerializer(queryset, many=True).data


class DiseaseSerializer(serializers.ModelSerializer):
    """Болезни"""

    class Meta:
        model = Disease
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Получаем пользователя(аккаунт и т.п)"""  
    password = serializers.CharField(required=False)
    unread_messages = serializers.SerializerMethodField()
    disease = PresentablePrimaryKeyRelatedField(
        queryset=Disease.objects.all(),
        presentation_serializer=DiseaseSerializer,
        allow_null=True,
        required=False,
        many=True
    )
    centers = PresentablePrimaryKeyRelatedField(
        queryset=Center.objects.all(),
        presentation_serializer=CenterSerializer,
        allow_null=True,
        required=False,
        many=True
    )
    
    main_center = PresentablePrimaryKeyRelatedField(
        queryset=Center.objects.all(),
        presentation_serializer=CenterSerializer,
        allow_null=True,
        required=False,
        many=False
    )
    clinic = PresentablePrimaryKeyRelatedField(
        queryset=Clinic.objects.all(),
        presentation_serializer=ClinicSerializer,
        allow_null=True,
        required=False,
        many=False
    )
    city = PresentablePrimaryKeyRelatedField(
        queryset=City.objects.all(),
        presentation_serializer=CitySerializer,
        allow_null=True,
        required=False,
        many=False
    )
    country = PresentablePrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        presentation_serializer=CountrySerializer,
        allow_null=True,
        required=False,
        many=False
    )
    
    def __init__(self, *args, **kwargs):
        self.depth = kwargs.pop("depth", 1)
        self.Meta.depth = self.depth
        super(UserSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = '__all__'

    def get_unread_messages(self, obj):
        queryset = UnreadMessage.objects.filter(user=obj)
        return UnreadMsgSerializer(queryset, many=True).data


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





class DoctorGetSerializer(serializers.ModelSerializer):
    unread_messages = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = "__all__"
        depth = 1
    
    
    def get_unread_messages(self, obj):
        queryset = UnreadMessage.objects.filter(doctor=obj)
        return UnreadMsgSerializer(queryset, many=True).data


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
