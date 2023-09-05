
from api import permissions
from django.utils.autoreload import raise_last_exception
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from db.queries import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from .serializers import CustomTokenObtainPairSerializer
from rest_framework import status
from rest_framework.views import APIView
from api.serializers import UserGetSerializer, CenterSerializer, DiseaseSerializer
from auth_user.service import generate_verification_code, send_sms, send_reset_sms, send_reset_email, set_new_password, \
    send_verification_email
from auth_user.serializers import *
from api.models import User
import logging

logger = logging.getLogger(__name__) 


class CustomTokenObtainPairView(TokenObtainPairView):
    # Replace the serializer with your custom
    serializer_class = CustomTokenObtainPairSerializer


class UserView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    """Список пользоватлей"""
    serializer_class = UserGetSerializer
    queryset = get_users() 


    def post(self, request):

        code = generate_verification_code()
        serializer = CreateUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            if int(request.data['stage']) == 3:
                send_sms.delay(user.number, code)
                user.verification_code = code
                user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, редактирование отдельного пользователя по id"""
    serializer_class = UserGetSerializer
    permissions_classes = [IsAuthenticated]
    

    def get_object(self):
        data = cache.get_or_set("users", get_users())
        data = data.filter(id=self.request.user.id).first()
        logger.debug(data)
        logger.debug(self.request.path)
        return data


class GetDiseasesView(APIView):
    """Получение всех заболеваний во время этапа регистрации"""
    def get(self, request):
        diseases = cache.get_or_set(get_disease())
        serializer = DiseaseSerializer(diseases, many=True)
        logger.debug(serializer.data)
        logger.debug(self.request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)

# sms-code block ##
class VerifyCodeView(APIView):
     """Проверка кода во время регистрации"""
     def post(self, request):
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

class ResendSmsView(APIView):
    """Переотправка смс, в разделе 'получить смс снова'. Регистрация """
    def post(self, request):
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


# password-reset block#
class PasswordResetView(APIView):
    """Сброс пароля. Этап отправки"""
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()

            
            if 'number' in  request.data:
                    code = generate_verification_code()
                    num = request.data['number']
                    send_reset_sms(num, code)
                    user.reset_code = code
                    logger.debug(code)
                    user.save()

            if 'email' in  request.data:
                    code = generate_verification_code()
                    email = request.data['email']
                    send_reset_email(email, code)
                    user.reset_code = code
                    logger.debug(code)
                    user.save()
            
            logger.info(serializer.data)
            logger.debug(request.path)
            return Response(serializer.data, status=status.HTTP_200_OK)
        

        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyResetCodeView(APIView):
    """Проверка кода для сброса пароля"""
    def post(self, request):
        serializer = VerifyResetCodeSerializer(data=request.data)
        if serializer.is_valid():
            reset_code = serializer.validated_data['reset_code']
            if 'email' in serializer.validated_data:
                user = User.objects.get(email=serializer.validated_data['email'])
            else:
                user = User.objects.get(number=serializer.validated_data["number"])
            if reset_code == user.reset_code:
                user.save()
                logger.debug("User got the access to his account")
                logger.debug(request.path)
                return Response({"message": "User got the access to his account"}, status=status.HTTP_200_OK)
            
            else:
                logger.warning("User didnt get the access to his account")
                logger.warning(request.path)
                return Response({"message": "User didnt get the access to his account"},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            logger.warning(serializer.errors)
            logger.warning(request.path)
            return Response(serializer.errors)
        

class SetNewPasswordView(APIView):
    """Установка нового пароля"""
    def post(self, request):
        serializer = NewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            password1 = serializer.validated_data['password1']
            password2 = serializer.validated_data['password2']

            if "email" in serializer.validated_data:
                    user = User.objects.get(email=serializer.validated_data["email"])


            if "number" in serializer.validated_data:
                user = User.objects.get(number=serializer.validated_data["number"])

            else:
                logger.warning("User not found")
                logger.warning(request.path)
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

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


## email block
class EmailBindingView(APIView):
    """Привязка почты к аккаунту. Шаг 1 - отправка письма"""
    def post(self,request):
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
            return Response({'detail': 'email has sent successfully'}, status=status.HTTP_200_OK)

        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailCodeView(APIView):
    """Проверка кода из email , для привязки почты"""
    def post(self, request):
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
                
        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CreateAdminView(generics.ListCreateAPIView):
    """Создание админа"""
    permission_classes = [AllowAny]
    model = User
    serializer_class = AdminSerializer

    def post(self, request):
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            logger.debug(serializer.data)
            logger.debug(request.path)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CenterRegistrationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, city):
        centers = get_centers().filter(city=city)
        logger.debug(centers)
        data = CenterSerializer(centers, many=True).data
        logger.debug(data)
        logger.debug(request.path) 
        return Response(data, status=status.HTTP_200_OK)
