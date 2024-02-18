from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from social.views import ChatCreate
from auth_user.views import LoginView
from .views import *

router = DefaultRouter()
router.register(r'api/news', NewsViewSet, basename='news')
router.register(r'api/notes', NoteViewSet, basename='notes')
router.register(r'api/saved', SaveViewSet, basename='saved')
router.register(r'api/likes', LikeViewSet, basename='likes')
router.register(r'api/subscribes', SubscribeViewSet, basename='subscribes')

urlpatterns = [
    path('api/token/', LoginView.as_view(), name='token_obtain_pair_url'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh_url'),
    path('api/search/', SearchView.as_view(), name='search_view_url'),
    path('api/countries/', CountryListView.as_view(), name="get_countries_url"),
    path('api/cities/', CityListView.as_view(), name="get_cities_url"),
    path('api/chat/create', ChatCreate.as_view(), name='chat_create')
]
urlpatterns += router.urls
