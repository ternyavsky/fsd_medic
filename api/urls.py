from django.urls import path, include

from .views import *
from social.views import ChatView, ChatCreate
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'api/news', NewsViewSet, basename='news')
router.register(r'api/notes', NoteViewSet, basename='notes')
router.register(r'api/saved', SaveViewSet, basename='saved')
router.register(r'api/likes', LikeViewSet, basename='likes')

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(),name='token_obtain_pair_url'),
    path('api/token/refresh/', TokenRefreshView.as_view(),name='token_refresh_url'),
    path('api/search/', SearchView.as_view(), name='search_view_url'),
    path('api/notes/doctors/', DoctorsListView.as_view(), name="get_doctors_url"),
    path('api/countries', CountryListView.as_view(), name="get_countries_url"),
    path('chat/create', ChatCreate.as_view(),  name='chat_create')
]
urlpatterns += router.urls
