from auth_doctor.views import DoctorDataPast, RegSmsCodeSend, IsDoctorVerCodeRight, UpdateDateTimeViewDoctor, \
    UpdateDateTimeViewClinic, ClinicDataPast, IsClinicVerCodeRight

from django.urls import path, include

urlpatterns = [
    path('api/doctor_clinic/send_code/<str:user_hash>',
         RegSmsCodeSend.as_view(), name='create_send_code'),
    # отправка кода на смс и сохранение его в кэше

    path('api/doctor/create', DoctorDataPast.as_view(),
         name='doctor_create'),  # Сохранение данных в кэше

    path('api/doctor/compare_code', IsDoctorVerCodeRight.as_view(),
         name='doctor_verification_code'),
    # ввод кода из смс и создание пользователя в БД
    path('api/doctor/set_interview_date',
         UpdateDateTimeViewDoctor.as_view(), name='doctor_set_date'),
    # устанавливаем дату интервью

    path('api/clinic/create', ClinicDataPast.as_view(),
         name='clinic_create'),  # Сохранение данных в кэше
    path('api/clinic/compare_code', IsClinicVerCodeRight.as_view(),
         name='clinic_verification_code'),
    # ввод кода из смс и создание пользователя в БД
    path('api/clinic/set_interview_date',
         UpdateDateTimeViewClinic.as_view(), name='clinic_set_date'),
    # устанавливаем дату интервью
]
