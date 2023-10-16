from rest_framework import HTTP_HEADER_ENCODING, authentication
from django.utils.translation import gettext_lazy as _
import jwt

from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError



class DoctorJWTAuth(authentication.BasicAuthentication):
    def authenticate(self, request):
        header, token = request.headers.get("Authorization").split(" ")
        print(header)
        if header != "Bearer":
            raise AuthenticationFailed(_("Invalid basic header"))
        a = jwt.decode(token, header, algorithms=["HS256"])
            # print(a)
            # if len(token) == 1:
            #     msg = _('Invalid basic header. No credentials provided.')
            #     raise AuthenticationFailed(msg)
    