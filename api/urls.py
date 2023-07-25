from django.urls import path, include

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

    

    path('api/search/', SearchView.as_view(), name='search_view_url'),
    path('api/users/diseases/', GetDiseasesView.as_view(), name='diseases_view_url'),


    path('api/notes/doctors/', DoctorsListView.as_view(), name="get_doctors_url"),
    path('api/notes/', NoteView.as_view(), name='note_create_view_url'),
    path('api/notes/<int:note_id>/', NoteDetailView.as_view(), name='note_detail_view_url'),


    path('api/users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('registration/<str:parameter>/', registration, name='registration_url'),



    path('', index, name='home_url'),

    path('logout', LOGOUT, name='logout_url'),
    path('account', Account, name='account_url'),
    # path('api/update/user/', UpdateUserView.as_view(), name='update_user_url'),
    # path('api/update/admin/', UpdateUserView.as_view(), name='update_admin_url'),
]
