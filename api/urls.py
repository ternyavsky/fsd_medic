from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *
from social.views import ChatView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



urlpatterns = [

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair_url'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh_url'),
    path('api/news/', NewsView.as_view(), name='news_view_url'),
    path('api/news/<int:id>/', NewsDetailView.as_view(), name='news_detail_url'),
    path('api/like/', LikeView.as_view(), name='like_view_url'),
    path('api/saved/', SaveView.as_view(), name='save_view_url'),



    path('api/users/centers/', CenterRegistrationView.as_view(), name='center_reg_url'),
    path('api/search/', SearchView.as_view(), name='search_view_url'),
    path('api/users/diseases/', GetDiseasesView.as_view(), name='diseases_view_url'),



    path('api/notes/', NoteView.as_view(), name='note_create_view_url'),
    path('api/notes/<int:note_id>/', NoteDetailView.as_view(), name='note_detail_view_url'),

    path('api/users/', UserView.as_view(), name='user_list'),
    path('api/users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('api/create/admin/', CreateAdminView.as_view(), name='create_admin_url'),
    path('registration/<str:parameter>/', registration, name='registration_url'),


    ## sms, email block ##
    path('api/verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('api/resend-sms/', ResendSmsView.as_view(), name='resend-sms'),
    path('api/reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('api/verify-reset-password/', VerifyResetCodeView.as_view(), name='verify-reset-password'),
    path('api/change-password/', SetNewPasswordView.as_view(), name='change-password'),
    path('api/verify-email/<int:user_id>/', EmailBindingView.as_view(), name='verify_email'),
    path('api/verify-email-code/<int:user_id>/', VerifyEmailCodeView.as_view(), name='verify_email_code'),
    ## endblock ##
    path('', index, name='home_url'),

    path('logout', LOGOUT, name='logout_url'),
    path('account', Account, name='account_url'),
    # path('api/update/user/', UpdateUserView.as_view(), name='update_user_url'),
    # path('api/update/admin/', UpdateUserView.as_view(), name='update_admin_url'),
]
