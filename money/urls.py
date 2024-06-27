from django.urls import path

from .views import MoneyView

urlpatterns = [
    path("api/money", MoneyView.as_view(), name="money"),
]

# urlpatterns += router.urls
