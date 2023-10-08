import logging

from rest_framework import status
from rest_framework.response import Response

from auth_user.serializers import EmailBindingSerializer, VerifyEmailCodeSerializer
from auth_user.service import generate_verification_code, send_verification_email

logger = logging.getLogger(__name__)


def email_bind_service(request):
    serializer = EmailBindingSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = request.user
        email_code = generate_verification_code()
        send_verification_email(email_code=email_code, user_email=email)
        logger.debug(email_code)
        user.email_verification_code = email_code
        user.save()

        logger.debug("email has sent successfully")
        logger.debug(request.path)
        return Response({'message': 'email has sent successfully'}, status=status.HTTP_200_OK)

    logger.warning(serializer.errors)
    logger.warning(request.path)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def verify_email_bind_service(request):
    serializer = VerifyEmailCodeSerializer(data=request.data)
    if serializer.is_valid():
        email_code = serializer.validated_data['email_verification_code']
        email = serializer.validated_data["email"]
        logger.debug(email_code)
        user = request.user
        if email_code == user.email_verification_code:
            user.email = email
            user.save()
            logger.debug("User verified successfully")
            logger.debug(request.path)
            return Response({"message": "User verified successfully"}, status=status.HTTP_200_OK)
        else:
            user.email = None
            user.save()

            logger.warning("Invalid verification code")
            logger.warning(request.path)
            return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
