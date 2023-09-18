from django.urls import path
from .views import DoctorDataPast, DoctorRegSmsCodeSend, IsDoctorVerCodeRight

urlpatterns = [
    path('doctor/create', DoctorDataPast.as_view(), name='doctor_create'), # Сохранение данных в кэше
    path('doctor/send_code/<str:user_hash>', DoctorRegSmsCodeSend.as_view(), name='doctor_create_send_code'), # отправка кода на смс и сохранение его в кэше
    path('doctor/compare_code', IsDoctorVerCodeRight.as_view(), name='doctor_verification_code'), #ввод кода из смс и создание пользователя в БД
]
