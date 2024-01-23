import logging

from rest_framework import status
from rest_framework.response import Response
from django.core.cache import cache

from api.models import User
from auth_user.serializers import  VerifyCodeSerializer, ResendCodeSerializer, \
      VerifyResetCodeSerializer, NewPasswordSerializer
from auth_user.service import generate_verification_code, send_sms, send_reset_sms, send_reset_email, set_new_password
from db.queries import get_users
from corsheaders.defaults import default_headers


logger = logging.getLogger(__name__)


def create_user_service(request, context):
    pass
        # code = generate_verification_code()
        # serializer = CreateUserSerializer(data=request.data, context={"request": request})
        # if serializer.is_valid():
        #     user = serializer.save()
        #     if int(request.data['stage']) == 3:
        #         send_sms.delay(user.number, code)
        #         user.verification_code = code
        #         user.save()
        #     response = Response(serializer.data, status=status.HTTP_201_CREATED)
        #     response.headers["Access-Control-Allow-Headers"] = default_headers, "access-control-allow-methods"
        #     return response
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        send_sms.delay(user.number, code)
        user.verification_code = code
        user.save()
        logger.debug(request.path)
        return Response({'detail': 'SMS resent successfully'}, status=status.HTTP_200_OK)
    logger.warning(serializer.errors)
    logger.warning(request.path)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def password_reset_service(data):
    if 'number' not in data and 'email' not in data:
        return Response({"error": "Not email or number"})
    code = generate_verification_code()
    users = cache.get_or_set("users", get_users())
    if 'number' in data:
        user = users.filter(number=data['number']).first()
        if user != None:
            num = data['number']
            send_reset_sms.delay(num, code)
            user.reset_code = code
            user.save()
            return Response({"message": "success"}, 200)
        else:
            return Response({"error": "Doctor not found"}, 400)
    if 'email' in data:
        user = users.filter(number=data['number']).first()
        if user != None:
            email = data['email']
            send_reset_email.delay(email, code)
            user.reset_code = code
            user.save()
            return Response({"message": "success"}, 200)
        else:
            return Response({"error": "Doctor not found"}, 400)


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
        
        set_new_password(user, serializer.validated_data["password2"])
        logger.debug("Password changed successfully")
        logger.debug(request.path)
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
    else:
        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
