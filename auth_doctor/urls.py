from django.urls import path
from .views import DoctorDataPast, DoctorRegSmsCodeSend

urlpatterns = [
    path('doctor/create', DoctorDataPast.as_view(), name='doctor_create'),
    path('doctor/send_code/<str:user_hash>', DoctorRegSmsCodeSend.as_view(), name='doctor_create_send_code'),
]
