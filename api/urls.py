from django.urls import path
from .views import index, ADMIN_SIGN_UP, INTERVIEW_SIGN_UP, INTERVIEW_SIGN_UP_2, USER_SIGN_UP, USER_SIGN_UP_2, LOGOUT, \
    USER_SIGN_IN, Account, Like
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),



    path('', index, name='home_url'),
    path('createadmin', ADMIN_SIGN_UP, name='create_admin_url'),
    path('registration', USER_SIGN_UP, name='create_user_url'),
    path('createinterview', INTERVIEW_SIGN_UP, name='create_interview_url'),
    path('authorization', USER_SIGN_IN, name='login_user_url'),
    path('logout', LOGOUT, name='logout_url'),
    path('userparameters/<str:parameter>', USER_SIGN_UP_2, name='create_user_2_url'),
    path('interviewparameters/<str:parameter>', INTERVIEW_SIGN_UP_2, name='create_interview_2_url'),
    path('account', Account, name='account_url'),
    path('like/<int:news_id>', Like, name='like')
]
