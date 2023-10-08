import logging

from rest_framework import status
from rest_framework.response import Response

from api.models import User
from auth_user.serializers import CreateUserSerializer, VerifyCodeSerializer, ResendCodeSerializer, \
    PasswordResetSerializer, VerifyResetCodeSerializer, NewPasswordSerializer
from auth_user.service import generate_verification_code, send_sms, send_reset_sms, send_reset_email, set_new_password

logger = logging.getLogger(__name__)


def create_user_service(data, context):
    code = generate_verification_code()
    serializer = CreateUserSerializer(data, context["request"])
    if serializer.is_valid():
        user = serializer.save()
        if int(data['stage']) == 3:
            send_sms.delay(user.number, code)
            user.verification_code = code
            user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def verify_code_service(request):
    serializer = VerifyCodeSerializer(data=request.data)
    if serializer.is_valid():
        number = serializer.validated_data['number']
        verification_code = serializer.validated_data['verification_code']
        # print(verification_code, ' current code from serializer')
        logger.debug(serializer.validated_data)
        try:
            user = User.objects.get(number=number)

        except User.DoesNotExist:
            logger.warning("User does not exist")
            logger.warning(request.path)
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if verification_code == user.verification_code:
            user.is_required = True
            user.save()
            return Response({"message": "User verified successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)


def resend_sms_service(request):
    serializer = ResendCodeSerializer(data=request.data)
    if serializer.is_valid():
        number = serializer.validated_data['number']

        try:
            user = User.objects.get(number=number)
        except User.DoesNotExist:
            logger.warning("User not found")
            logger.warning(request.path)
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        code = generate_verification_code()
        logger.debug(code)
        send_sms(user.number, code)
        user.verification_code = code
        user.save()
        logger.debug(request.path)
        return Response({'detail': 'SMS resent successfully'}, status=status.HTTP_200_OK)
    logger.warning(serializer.errors)
    logger.warning(request.path)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def password_reset_service(data):
    serializer = PasswordResetSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        code = generate_verification_code()
        if 'number' in data:
            num = data['number']
            send_reset_sms.delay(num, code)
        if 'email' in data:
            email = data['email']
            send_reset_email(email, code)
        user.reset_code = code
        user.save()
        logger.debug(code)
        logger.info(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    logger.warning(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def verify_reset_code_service(request):
    serializer = VerifyResetCodeSerializer(data=request.data)
    if serializer.is_valid():
        reset_code = serializer.validated_data['reset_code']
        if 'email' in serializer.validated_data:
            user = User.objects.get(
                email=serializer.validated_data['email'])
        else:
            user = User.objects.get(
                number=serializer.validated_data["number"])
        if reset_code == user.reset_code:
            user.save()
            logger.debug("User got the access to his account")
            logger.debug(request.path)
            return Response({"message": "User got the access to his account"}, status=status.HTTP_200_OK)

        else:
            logger.warning("User didn't get the access to his account")
            logger.warning(request.path)
            return Response({"message": "User didn't get the access to his account"},
                            status=status.HTTP_404_NOT_FOUND)
    else:
        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors)


def set_new_password_service(request):
    serializer = NewPasswordSerializer(data=request.data)
    if serializer.is_valid():
        password1 = serializer.validated_data['password1']
        password2 = serializer.validated_data['password2']

        if "email" in serializer.validated_data:
            user = User.objects.get(
                email=serializer.validated_data["email"])

        if "number" in serializer.validated_data:
            user = User.objects.get(
                number=serializer.validated_data["number"])

        else:
            logger.warning("User not found")
            logger.warning(request.path)
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if password1 == password2:
            set_new_password(user, password2)
            logger.debug("Password changed successfully")
            logger.debug(request.path)
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        else:
            logger.warning("Password do not match")
            logger.warning(request.path)
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
