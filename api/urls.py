from django.urls import path, include

from .views import *
from social.views import ChatView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from auth_doctor.views import DoctorDataPast, RegSmsCodeSend, IsDoctorVerCodeRight, UpdateDateTimeViewDoctor, \
    UpdateDateTimeViewClinic, ClinicDataPast, IsClinicVerCodeRight

router = DefaultRouter()
router.register(r'api/news', NewsViewSet, basename='news')
router.register(r'api/notes', NoteViewSet, basename='notes')
router.register(r'api/saved', SaveViewSet, basename='saved')
router.register(r'api/likes', LikeViewSet, basename='likes')

urlpatterns = [

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair_url'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh_url'),
    path('api/search/', SearchView.as_view(), name='search_view_url'),
    path('api/notes/doctors/', DoctorsListView.as_view(), name="get_doctors_url"),
    path("__debug__/", include("debug_toolbar.urls")),
    path('api/doctor_clinic/send_code/<str:user_hash>', RegSmsCodeSend.as_view(), name='create_send_code'),
    # отправка кода на смс и сохранение его в кэше

    path('api/doctor/create', DoctorDataPast.as_view(), name='doctor_create'),  # Сохранение данных в кэше

    path('api/doctor/compare_code', IsDoctorVerCodeRight.as_view(), name='doctor_verification_code'),
    # ввод кода из смс и создание пользователя в БД
    path('api/doctor/set_interview_date', UpdateDateTimeViewDoctor.as_view(), name='doctor_set_date'),
    # устанавливаем дату интервью

    path('api/clinic/create', ClinicDataPast.as_view(), name='clinic_create'),  # Сохранение данных в кэше
    path('api/clinic/compare_code', IsClinicVerCodeRight.as_view(), name='clinic_verification_code'),
    # ввод кода из смс и создание пользователя в БД
    path('api/clinic/set_interview_date', UpdateDateTimeViewClinic.as_view(), name='clinic_set_date'),
    # устанавливаем дату интервью
]
urlpatterns += router.urls
