from django.db.models.aggregates import Count
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.relations import PrimaryKeyRelatedField

from social.models import Chat, Notification, UnreadMessage
from auth_doctor.models import Doctor
from .models import (
    News,
    User,
    Center,
    Clinic,
    Disease,
    Note,
    Saved,
    Like,
    Country,
    Access,
    City,
    Subscribe,
    NewsImages,
    NewsVideos,
)
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField


class CountrySerializer(serializers.ModelSerializer):
    """Страны"""

    class Meta:
        model = Country
        fields = "__all__"


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    """Города"""

    class Meta:
        model = City
        fields = "__all__"


class CenterSerializer(serializers.ModelSerializer):
    """Клиники"""

    # unread_messages = serializers.SerializerMethodField()

    class Meta:
        model = Center
        fields = "__all__"

    # def get_unread_messages(self, obj):
    #    queryset = UnreadMessage.objects.filter(center=obj)
    #    return UnreadMsgSerializer(queryset, many=True).data


class DiseaseSerializer(serializers.ModelSerializer):
    """Болезни"""

    class Meta:
        model = Disease
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    disease = DiseaseSerializer(many=True)
    country = CountrySerializer()
    city = CitySerializer()
    interest = DiseaseSerializer()

    class Meta:
        model = User
        fields = "__all__"


class UserUpdateSerializer(serializers.ModelSerializer):
    """Получаем пользователя(аккаунт и т.п)"""

    password = serializers.CharField(required=False)
    disease = PresentablePrimaryKeyRelatedField(
        queryset=Disease.objects.all(),
        presentation_serializer=DiseaseSerializer,
        allow_null=True,
        required=False,
        many=True,
    )
    city = PresentablePrimaryKeyRelatedField(
        queryset=City.objects.all(),
        presentation_serializer=CitySerializer,
        allow_null=True,
        required=False,
    )
    country = PresentablePrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        presentation_serializer=CountrySerializer,
        allow_null=True,
        required=False,
    )
    centers = PresentablePrimaryKeyRelatedField(
        queryset=Center.objects.all(),
        presentation_serializer=CenterSerializer,
        allow_null=True,
        required=False,
        many=True,
    )

    clinic = PresentablePrimaryKeyRelatedField(
        queryset=Clinic.objects.all(),
        presentation_serializer=ClinicSerializer,
        allow_null=True,
        required=False,
        many=False,
    )

    class Meta:
        model = User
        fields = "__all__"


class AccessSerializer(serializers.ModelSerializer):
    """Доступ"""

    class Meta:
        model = Access
        fields = "__all__"


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImages
        fields = ["image"]


class NewsVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsVideos
        fields = ["video"]


class NewsSerializer(serializers.ModelSerializer):
    quant_likes = serializers.SerializerMethodField()
    news_images = NewsImageSerializer(many=True, read_only=True)
    news_videos = NewsVideoSerializer(many=True, read_only=True)
    upload_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=True),
        write_only=True,
        required=False,
    )
    upload_videos = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=True),
        write_only=True,
        required=False,
    )

    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "text",
            "clinic",
            "disease",
            "news_images",
            "news_videos",
            "quant_likes",
            "upload_images",
            "upload_videos",
            "created_at",
            "updated_at",
        ]

    def get_quant_likes(self, obj):
        try:
            return obj.quant_likes
        except AttributeError:
            return 0

    def create(self, validated_data):
        upload_images = validated_data.pop("upload_images", None)
        upload_videos = validated_data.pop("upload_videos", None)
        news = News.objects.create(**validated_data)
        if upload_images:
            for i in upload_images:
                news_image = NewsImages.objects.create(news=news, image=i)
        if upload_videos:
            for i in upload_videos:
                news_video = NewsVideos.objects.create(news=news, video=i)
        return news


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"

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
    """get serializer for saved model"""

    class Meta:
        model = Saved
        fields = "__all__"


class SubscribeSerializer(serializers.ModelSerializer):
    """get serializer for subscribe model"""

    user = UserSerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)
    main_doctor = DoctorGetSerializer(read_only=True)

    class Meta:
        model = Subscribe
        fields = "__all__"

    def create(self, validated_data):
        return Subscribe.objects.create(**validated_data)


class LikeSerializer(serializers.ModelSerializer):
    """get serializer for like model"""

    class Meta:
        model = Like
        fields = "__all__"
