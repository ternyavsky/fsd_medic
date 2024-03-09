from django.urls import path

from auth_doctor.views import *

urlpatterns = [
    path(
        "api/create_clinic/<str:clinic_hash>/",
        ClinicInterviewCreate.as_view(),
        name="clinic_interview",
    ),
    path(
        "api/create_doctor/<str:doctor_hash>/",
        DoctorInterviewCreate.as_view(),
        name="doctor_interview",
    ),
    path("api/clinic/create/", ClinicDataPast.as_view(), name="clinic_create"),
    path(
        "api/doctor/create/", DoctorDataPast.as_view(), name="doctor_create"
    ),  # Сохранение данных в кэше
    path(
        "api/reset-password-doctor/",
        DoctorPasswordResetView.as_view(),
        name="reset-password-doctor",
    ),
    path(
        "api/verify-reset-password-doctor/",
        DoctorVerifyResetCodeView.as_view(),
        name="verify-reset-password-doctor",
    ),
    path(
        "api/change-password-doctor/",
        DoctorSetNewPasswordView.as_view(),
        name="change-password-doctor",
    ),
    path(
        "api/resend-sms-doctor/",
        DoctorResendSmsView.as_view(),
        name="resend-sms-doctor",
    ),
    path(
        "api/reset-password-clinic/",
        ClinicPasswordResetView.as_view(),
        name="reset-password-clinic",
    ),
    path(
        "api/verify-reset-password-clinic/",
        ClinicVerifyResetCodeView.as_view(),
        name="verify-reset-password-clinic",
    ),
    path(
        "api/change-password-clinic/",
        ClinicSetNewPasswordView.as_view(),
        name="change-password-clinic",
    ),
    path(
        "api/resend-sms-clinic/",
        ClinicResendSmsView.as_view(),
        name="resend-sms-clinic",
    ),
    # LOGIN INSTANCES
    path("api/doctor_token/", LoginDoctor.as_view(), name="token-doctor"),
    path("api/center_token/", LoginCenter.as_view(), name="token-center"),
    path("api/clinic_token/", LoginClinic.as_view(), name="token-clinic"),
    path("api/notes/doctors/", DoctorsListView.as_view(), name="get_doctors_url"),
    path("api/inter/", InterviewView.as_view(), name="test")
    # Сохранение данных в кэше
]
