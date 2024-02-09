from rest_framework import serializers
from rest_framework.fields import empty
from social.serializers import UnreadMsgSerializer
from social.models import UnreadMessage
from auth_doctor.models import Doctor
from .models import News, User, Center, Clinic, Disease, Note, Saved, Like, Country, Access, City, Subscribe
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField

class CountrySerializer(serializers.ModelSerializer):
    """Страны"""

    class Meta:
        model = Country
        fields = '__all__'

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    """Города"""

    class Meta:
        model = City
        fields = '__all__'
class CenterSerializer(serializers.ModelSerializer):
    """Клиники"""

    unread_messages = serializers.SerializerMethodField()

    class Meta:
        model = Center
        fields = '__all__'

    def get_unread_messages(self, obj):
        queryset = UnreadMessage.objects.filter(center=obj)
        return UnreadMsgSerializer(queryset, many=True).data


class DiseaseSerializer(serializers.ModelSerializer):
    """Болезни"""

    class Meta:
        model = Disease
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    disease = DiseaseSerializer(many=True)
    country = CountrySerializer()
    class Meta:
        model = User
        fields = '__all__'

class UserUpdateSerializer(serializers.ModelSerializer):
    """Получаем пользователя(аккаунт и т.п)"""  
    password = serializers.CharField(required=False)
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

    clinic = PresentablePrimaryKeyRelatedField(
        queryset=Clinic.objects.all(),
        presentation_serializer=ClinicSerializer,
        allow_null=True,
        required=False,
        many=False
    )


    class Meta:
        model = User
        fields = '__all__'

    


class AccessSerializer(serializers.ModelSerializer):
    """Доступ"""

    class Meta:
        model = Access
        fields = '__all__'


class NewsPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['image', 'title', 'created_at']



class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

 
    def create(self, validated_data):
        news = News.objects.create(**validated_data)
        return news


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'

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

    class Meta:
        model = Doctor
        fields = "__all__"
    

class SearchSerializer(serializers.Serializer):
    
    doctors = DoctorGetSerializer(read_only=True, many=True)
    clinics = ClinicSerializer(read_only=True, many=True)
    centers = CenterSerializer(read_only=True, many=True)


class SavedSerializer(serializers.ModelSerializer):
    ''' get serializer for saved model'''

    class Meta:
        model = Saved
        fields = '__all__'


class SubscribeSerializer(serializers.ModelSerializer):
    '''get serializer for subscribe model'''

    class Meta:
        model = Subscribe
        fields = '__all__'


class LikeSerializer(serializers.ModelSerializer):
    ''' get serializer for like model'''

    class Meta:
        model = Like
        fields = '__all__'
        
