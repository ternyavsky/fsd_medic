from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r"api/admin/center", CenterProfileViewset, basename="admin_center"),
router.register(r"api/admin/clinic", ClinicProfileViewset, basename="admin_clinic"),
router.register(r"api/admin/user", UserProfileViewset, basename="admin_user")
# router.register(r'api/admin/city', CityProfileViewset, basename="admin_city")
# router.register(r'api/admin/country', CountryProfileViewset, basename="admin_country")

urlpatterns = [path("api/admin/mainpage", MainPage.as_view(), name="asd")]
urlpatterns += router.urls
