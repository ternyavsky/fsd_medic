from auth_doctor.views import *

from django.urls import path, include

urlpatterns = [
      path('api/create_clinic/<str:clinic_hash>/', ClinicInterviewCreate.as_view(), name="clinic_interview"),
      path('api/create_doctor/<str:doctor_hash>/', DoctorInterviewCreate.as_view(), name="doctor_interview"),


      path('api/clinic/create/', ClinicDataPast.as_view(), name='clinic_create'),
      path('api/doctor/create/', DoctorDataPast.as_view(), name='doctor_create'),  # Сохранение данных в кэше


      path('api/reset-password-doctor/', DoctorPasswordResetView.as_view(), name='reset-password-doctor'),
      path('api/verify-reset-password-doctor/', DoctorVerifyResetCodeView.as_view(), name='verify-reset-password-doctor'),
      path('api/change-password-doctor/', DoctorSetNewPasswordView.as_view(), name='change-password-doctor'),


      path('api/reset-password-clinic/', ClinicPasswordResetView.as_view(), name='reset-password-clinic'),
      path('api/verify-reset-password-clinic/', ClinicVerifyResetCodeView.as_view(), name='verify-reset-password-clinic'),
      path('api/change-password-clinic/', ClinicSetNewPasswordView.as_view(), name='change-password-clinic'),

      # Сохранение данных в кэше
]