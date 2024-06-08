import logging
from os import stat
from drf_yasg.utils import serializers

from rest_framework import status
from rest_framework.response import Response
from django.core.cache import cache

from api.models import User
from auth_user.serializers import (
    VerifyCodeSerializer,
    ResendCodeSerializer,
    VerifyResetCodeSerializer,
    NewPasswordSerializer,
)
from auth_user.service import (
    generate_verification_code,
    send_email,
    send_sms,
    send_reset_sms,
    send_reset_email,
    set_new_password,
)
from db.queries import get_users
from corsheaders.defaults import default_headers


logger = logging.getLogger(__name__)


def verify_code_service(request):
    serializer = VerifyCodeSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        verification_code = serializer.validated_data["verification_code"]
        logger.debug(serializer.validated_data)
        try:
            user = User.objects.filter(email=email).first()
        except User.DoesNotExist:
            logger.warning("User does not exist")
            logger.warning(request.path)
            return Response(
                {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        if verification_code == user.verification_code:
            user.is_required = True
            user.save()
            return Response(
                {"message": "User verified successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid verification code"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def resend_sms_service(request):
    serializer = ResendCodeSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        try:
            user = User.objects.filter(email=email).first()
        except User.DoesNotExist:
            logger.warning("User not found")
            logger.warning(request.path)
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        code = generate_verification_code()
        send_email.delay(user.email, code)
        user.verification_code = code
        user.save()
        logger.debug(request.path)
        return Response(
            {"detail": "SMS resent successfully"}, status=status.HTTP_200_OK
        )
    logger.warning(serializer.errors)
    logger.warning(request.path)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def password_reset_service(data):
    if "number" not in data and "email" not in data:
        return Response({"error": "Not email or number"})
    code = generate_verification_code()
    users = cache.get_or_set("users", get_users())
    if "number" in data:
        user = users.filter(number=data["number"]).first()
        if user != None:
            num = data["number"]
            send_reset_sms.delay(num, code)
            user.reset_code = code
            user.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Doctor not found"}, status=status.HTTP_400_BAD_REQUEST
            )
    if "email" in data:
        user = users.filter(email=data["email"]).first()
        if user != None:
            email = data["email"]
            send_reset_email.delay(email, code)
            user.reset_code = code
            user.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Doctor not found"}, status=status.HTTP_400_BAD_REQUEST
            )


def verify_reset_code_service(request):
    serializer = VerifyResetCodeSerializer(data=request.data)
    if serializer.is_valid():
        reset_code = serializer.validated_data["reset_code"]
        if "email" in serializer.validated_data:
            user = User.objects.filter(email=serializer.validated_data["email"]).first()
        else:
            user = User.objects.filter(
                number=serializer.validated_data["number"]
            ).first()
        if reset_code == user.reset_code:
            user.save()
            logger.debug("User got the access to his account")
            logger.debug(request.path)
            return Response(
                {"message": "User got the access to his account"},
                status=status.HTTP_200_OK,
            )

        else:
            logger.warning("User didn't get the access to his account")
            logger.warning(request.path)
            return Response(
                {"message": "User didn't get the access to his account"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors)


def set_new_password_service(request):
    serializer = NewPasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = None
        if "email" in serializer.validated_data:
            user = User.objects.filter(email=serializer.validated_data["email"]).first()
        elif "number" in serializer.validated_data:
            user = User.objects.filter(
                number=serializer.validated_data["number"]
            ).first()
        else:
            logger.warning("User not found")
            logger.warning(request.path)
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        set_new_password(user, serializer.validated_data["password"])
        logger.debug("Password changed successfully")
        logger.debug(request.path)
        return Response(
            {"message": "Password changed successfully"}, status=status.HTTP_200_OK
        )
    else:
        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
