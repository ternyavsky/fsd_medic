from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'api/admin/center', CenterProfileViewset, basename='admin_center'),
router.register(r'api/admin/clinic', ClinicProfileViewset, basename="admin_clinic")

urlpatterns = [ 
    path("api/admin/mainpage", MainPage.as_view(), name="asd")
]
urlpatterns += router.urls