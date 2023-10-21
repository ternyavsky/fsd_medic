from rest_framework.views import APIView
from datetime import date, datetime
from django.core.cache import cache
from django.db.models import Count, Q, Subquery, F
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from api.serializers import CenterSerializer
from db.queries import *
from .serializers import *
# Create your views here.


class UserProfileViewset(viewsets.ViewSet):
    serializer_class = UserProfileSerializer

    def get_queryset(self, pk=None):
        users = cache.get_or_set("users", get_users())
        users = users.filter(pk=pk) if pk else users
        access = cache.get_or_set("access", get_access())
        access = access.filter(user_id=pk) if pk else access   
        notes = cache.get_or_set("notes", get_notes())
        curr_notes = notes.filter(user_id__in=Subquery(users.values("id")), status="Passed")
        process_notes = notes.filter(user_id__in=Subquery(users.values("id")), status="In processing")
        miss_notes = notes.filter(user_id__in=Subquery(users.values("id")), time_start__gt=datetime.now())
        result = {  
            "user": users,  
            "curr_notes": curr_notes, #Текущие записи
            "process_notes": process_notes, # Неустановленные записи
            "miss_notes": miss_notes, # Пропущенные записи
            "access": access
        }
        return result

    @swagger_auto_schema(
        operation_summary="Все пользователи/Админка"
    )
    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Конкретный пользователь/Админка"
    )
    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, pk=None):
        queryset = self.get_queryset(pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClinicProfileViewset(viewsets.ModelViewSet):
    serializer_class = ClinicUserProfileSerializer

    def get_queryset(self, pk=None):
        clinics = cache.get_or_set("clinics", get_clinics())
        clinics = clinics.filter(pk=pk) if pk else clinics
        clinics = clinics.annotate(
            online_notes=Count("note", filter=Q(note__online=True)),
            offline_notes=Count("note", filter=Q(note__online=False)),
            visit_online=Count("note", filter=Q(note__online=True, note__time_start__day=date.today().day)),
            visit_offline=Count("note", filter=Q(note__online=False, note__time_start__day=date.today().day))
        )
        users = cache.get_or_set("users", get_users())
        users = users.filter(clinic__id__in=clinics.values("id"))
        return {
            "clinic": clinics,
            "pacients": users
        }

    @swagger_auto_schema(
        operation_summary="Все клиники/Админка"
    )
    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        data = self.get_queryset()
        serializer = self.serializer_class(data)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        operation_summary="Конкретная клиники/Админка"
    )
    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, pk):
        data = self.get_queryset(pk=pk)
        serializer = self.serializer_class(data)
        return Response(serializer.data, status=200) 



class CenterProfileViewset(viewsets.ModelViewSet):
    serializer_class = CenterUserProfileSerializer

    def get_queryset(self, pk=None):
        centers = cache.get_or_set("centers", get_centers())
        centers = centers.filter(pk=pk) if pk else centers
        centers = centers.annotate(
            online_notes=Count("note", filter=Q(note__online=True)),
            offline_notes=Count("note", filter=Q(note__online=False)),
            visit_online=Count("note", distinct=True,
                               filter=Q(note__online=True, note__time_start__day=date.today().day)),
            visit_offline=Count("note", distinct=True,
                                filter=Q(note__online=False, note__time_start__day=date.today().day)),
        )
        users = cache.get_or_set("users", get_users())
        users_mainc = users.filter(main_center__id__in=centers.values("id"))
        users_centers = users.filter(centers__id__in=centers.values("id"))
        result = users_mainc.union(users_centers)
        obj = {
            "center": centers,
            "pacients": result
        }
        return obj

    @swagger_auto_schema(
        operation_summary="Все центры/Админка"
    )
    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        data = self.get_queryset()
        serializer = self.serializer_class(data)
        return Response(serializer.data, status=200)
    
    @swagger_auto_schema(
        operation_summary="Конкретный центр/Админка"
    )
    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, pk):
        data = self.get_queryset(pk=pk)
        serializer = self.serializer_class(data)
        return Response(serializer.data, status=200)


class MainPage(APIView):
    @swagger_auto_schema(
        operation_summary="Сайт и приложение"
    )
    @method_decorator(cache_page(60 * 60))
    def get(self, request):
        users = get_users()
        created_today = users.filter(created_at__date=date.today()).count()
        group_1 = users.filter(birthday__year__lte=date.today().year - 10, birthday__year__gte=date.today().year - 20)
        group_1 = group_1.annotate(
            man=Count("sex", filter=Q(sex="Мужчина")),
            woman=Count("sex", filter=Q(sex="Женщина"))
        )
        group_2 = users.filter(birthday__year__lte=date.today().year - 20, birthday__year__gte=date.today().year - 30)
        group_2 = group_2.annotate(
            man=Count("sex", filter=Q(sex="Мужчина")),
            woman=Count("sex", filter=Q(sex="Женщина"))
        )
        group_3 = users.filter(birthday__year__lte=date.today().year - 30 , birthday__year__gte=date.today().year - 40)
        group_3 = group_3.annotate(
            man=Count("sex", filter=Q(sex="Мужчина")),
            woman=Count("sex", filter=Q(sex="Женщина"))
        )
        group_4 = users.filter(birthday__year__lte=date.today().year - 40, birthday__year__gte=date.today().year - 50)
        group_4 = group_4.annotate(
            man=Count("sex", filter=Q(sex="Мужчина")),
            woman=Count("sex", filter=Q(sex="Женщина"))
        )
        group_5 = users.filter(birthday__year__lte=date.today().year - 50, birthday__year__gte=date.today().year - 60)
        group_5 = group_5.annotate(
            man=Count("sex", filter=Q(sex="Мужчина")),
            woman=Count("sex", filter=Q(sex="Женщина"))
        )
        group_6 = users.filter(birthday__year__lte=date.today().year - 60, birthday__year__gte=date.today().year - 70)
        group_6 = group_6.annotate(
            man=Count("sex", filter=Q(sex="Мужчина")),
            woman=Count("sex", filter=Q(sex="Женщина"))
        )
        # print(group_1.first().woman)
        print(group_2.values())
        diseases = cache.get_or_set("disease", get_disease())
        diseases = diseases.annotate(
            most_count=Count("user")
        )
        diseases = diseases.order_by("-most_count")

        data = {
            "diseases": diseases,
            "_10_20": group_1,
            "_20_30": group_2,
            "_30_40": group_3,
            "_40_50": group_4,
            "_50_60": group_5,
            "_60_70": group_6,
            "created_today": created_today
        }
        serializer = MainPageSerializer(data)
        return Response(serializer.data, status.HTTP_200_OK)


class CityProfileViewset(viewsets.ModelViewSet):
    serializer_class = CityProfileSerializer
    lookup_field = "name"

    def get_queryset(self):
        cities = cache.get_or_set("cities", get_cities())
        cities = cities.annotate(
            quant_centers=Count("center", distinct=True),
            quant_centers_today=Count("center", distinct=True, filter=Q(center__created_at__date=date.today())),
            quant_clinics=Count("clinic", distinct=True),
            quant_clinics_today=Count("clinic", distinct=True, filter=Q(clinic__created_at__date=date.today())),
            quant_users=Count("user", distinct=True),
            quant_users_today=Count("user", distinct=True, filter=Q(user__created_at__date=date.today())),
        )
        return cities

    @method_decorator(cache_page(60 * 60))
    def list(self, request):
        return super().list(request)

    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, name):
        return super().retrieve(request, name)


class CountryProfileViewset(viewsets.ModelViewSet):
    serializer_class = CountryCitySerializer
    lookup_field = "name"

    def get_queryset(self, name=None):
        cities = cache.get_or_set("cities", get_cities())
        cities = cities.filter(country__name=name) if name else cities
        cities = cities.annotate(
            quant_centers=Count("center", distinct=True),
            quant_centers_today=Count("center", distinct=True, filter=Q(center__created_at__date=date.today())),
            quant_clinics=Count("clinic", distinct=True),
            quant_clinics_today=Count("clinic", distinct=True, filter=Q(clinic__created_at__date=date.today())),
            quant_users=Count("user", distinct=True),
            quant_users_today=Count("user", distinct=True, filter=Q(user__created_at__date=date.today())),
        )
        cities = cities.order_by(-(F("quant_centers") + F("quant_clinics") + F("quant_users")))
        countries = cache.get_or_set("countries", get_countries())
        countries = countries.filter(name=name) if name else countries
        countries = countries.annotate(
            quant_clinics=Count("clinic", distinct=True),
            quant_clinics_today=Count("clinic", distinct=True, filter=Q(clinic__created_at__date=date.today())),
            quant_users=Count("user", distinct=True),
            quant_users_today=Count("user", distinct=True, filter=Q(user__created_at__date=date.today())),
            quant_doctors=Count("doctor", distinct=True),
            quant_doctors_today=Count("doctor", distinct=True),
        )
        result = {
            "cities": cities,
            "country": countries
        }
        return result

    @method_decorator(cache_page(60 * 60))
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, name):
        queryset = self.get_queryset(name)
        serialzier = self.serializer_class(queryset)
        return Response(serialzier.data, status=status.HTTP_200_OK)
