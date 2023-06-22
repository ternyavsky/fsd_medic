from django.urls import path
from .views import index, ADMIN_SIGN_UP, INTERVIEW_SIGN_UP, INTERVIEW_SIGN_UP_2, USER_SIGN_UP, USER_SIGN_UP_2, LOGOUT, \
    USER_SIGN_IN, Account, LikeView, NewsView, NewsDetailView, CreateUserView, SaveView, CreateAdminView, \
    UpdateUserView, SearchView, registration

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair_url'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh_url'),
    path('api/news/', NewsView.as_view(), name='news_view_url'),
    path('api/like/<int:id>/', LikeView.as_view(), name='like_view_url'),
    path('api/news/<int:id>/', NewsDetailView.as_view(), name='news_detail_url'),
    path('api/save/<int:id>/', SaveView.as_view(), name='save_view_url'),
    path('api/search/', SearchView.as_view(), name='search_view_url'),

    path('api/create/user', CreateUserView.as_view(), name='create_user_url'),
    path('api/update/user', UpdateUserView.as_view(), name='update_user_url'),
    path('api/create/admin', CreateAdminView.as_view(), name='create_admin_url'),
    path('api/update/admin', UpdateUserView.as_view(), name='update_admin_url'),

    path('registration/<str:parameter>', registration, name='registration_url'),
    path('', index, name='home_url'),

    path('registration', USER_SIGN_UP, name='create_user_url'),
    path('createinterview', INTERVIEW_SIGN_UP, name='create_interview_url'),
    path('authorization', USER_SIGN_IN, name='login_user_url'),
    path('logout', LOGOUT, name='logout_url'),
    path('account', Account, name='account_url'),
]
