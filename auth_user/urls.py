from django.urls import path
from .views import *

from rest_framework.routers import DefaultRouter
# router = DefaultRouter()
# router.register(r'api/access', AccessViewSet, basename='access')
urlpatterns = [

    path('api/users/', UserView.as_view(), name='user_list'),
    path('api/access/', AccessViewSet.as_view(), name="user_access"),
    path('api/create/admin/', CreateAdminView.as_view(), name='create_admin_url'),
    path('api/users-detail/', UserDetailView.as_view(), name="put_view"),
    path('api/verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('api/resend-sms/', ResendSmsView.as_view(), name='resend-sms'),
    path('api/reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('api/verify-reset-password/', VerifyResetCodeView.as_view(),
         name='verify-reset-password'),
    path('api/change-password/', SetNewPasswordView.as_view(),
         name='change-password'),

    path('api/verify-email/', EmailBindingView.as_view(), name='verify_email'),
    path('api/verify-email-code/', VerifyEmailCodeView.as_view(),
         name='verify_email_code'),
    path('api/users/diseases/', GetDiseasesView.as_view(),
         name='diseases_view_url'),
    path('api/users/centers/<str:city>/',
         CenterRegistrationView.as_view(), name='center_reg_url'),
]

# urlpatterns += router.urls
