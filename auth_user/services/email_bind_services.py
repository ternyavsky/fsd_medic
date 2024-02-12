import logging

from rest_framework import status
from rest_framework.response import Response

from auth_user.serializers import NumberBindingSerializer, VerifyNumberCodeSerializer 
from auth_user.service import generate_verification_code, send_sms, send_verification_email

logger = logging.getLogger(__name__)


def number_bind_service(request):
    serializer = NumberBindingSerializer(data=request.data)
    if serializer.is_valid():
        number = serializer.validated_data['number']
        user = request.user
        number_code = generate_verification_code()
        send_sms(user.number, number_code)
        user.number_verification_code = number_code 
        user.save()

        logger.debug("code sended")
        logger.debug(request.path)
        return Response({'message': 'code has sent successfully'}, status=status.HTTP_200_OK)

    logger.warning(serializer.errors)
    logger.warning(request.path)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def verify_number_bind_service(request):
    serializer = VerifyNumberCodeSerializer(data=request.data)
    if serializer.is_valid():
        number_code = serializer.validated_data['number_verification_code']
        number = serializer.validated_data["number"]
        user = request.user
        if number_code == user.number_verification_code:
            user.number = number 
            user.save()
            logger.debug("User verified successfully")
            logger.debug(request.path)
            return Response({"message": "User verified successfully"}, status=status.HTTP_200_OK)
        else:
            user.number = None
            user.save()

            logger.warning("Invalid verification code")
            logger.warning(request.path)
            return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
