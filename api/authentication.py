from rest_framework import HTTP_HEADER_ENCODING, authentication
from django.utils.translation import gettext_lazy as _
import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import Center
from rest_framework import authentication
from rest_framework import exceptions
from db.queries import get_doctors


class DoctorAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_X_USERNAME')
        # decode variable
        # decode.doctor   "+79313123132"
        # query for number
        # return 
        if not username:
            return None
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Doctor not found')

        return (user, None)


class ClinicAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        pass
