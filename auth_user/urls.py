from django.urls import path

from .views import *

urlpatterns = [

    #regiistration steps 

    # path('api/c', CreateUserView.as_view(), name='create_user_1'),
    # path('api/create_user_2/', CreateUserSecondStepView.as_view(), name='create_user_2'),

    path('api/login', LoginView.as_view(), name='login'),
    path('api/users/', UserView.as_view(), name='user-list'),
    path('api/access/', AccessViewSet.as_view(), name="user-access"),
    path('api/create/admin/', CreateAdminView.as_view(), name='create_admin_url'),
    path('api/users-detail/', UserDetailView.as_view(), name="put-view"),
    path('api/verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('api/resend-sms/', ResendSmsView.as_view(), name='resend-sms'),
    path('api/reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('api/verify-reset-password/', VerifyResetCodeView.as_view(), name='verify-reset-password'),
    path('api/change-password/', SetNewPasswordView.as_view(), name='change-password'),

    path('api/verify-email/', EmailBindingView.as_view(), name='verify_email'),
    path('api/verify-email-code/', VerifyEmailCodeView.as_view(), name='verify_email_code'),
    path('api/users/diseases/', GetDiseasesView.as_view(), name='diseases_view_url'),
    path('api/users/centers/<str:city>/', CenterRegistrationView.as_view(), name='center_reg_url'),
]

# urlpatterns += router.urls
