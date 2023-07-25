
from rest_framework import generics
from rest_framework.permissions import AllowAny

from db.queries import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from api.serializers import UserGetSerializer, CenterSerializer
from auth_user.service import generate_verification_code, send_sms, send_reset_sms, send_reset_email, set_new_password, \
    send_verification_email
from auth_user.serializers import *


class UserView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    """Список пользоватлей"""
    serializer_class = UserGetSerializer
    queryset = User.objects.all()

    def post(self, request):
        code = generate_verification_code()
        serializer = CreateUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            if int(request.data['stage']) == 3:
                send_sms(user.number, code)
                user.verification_code = code
                user.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# sms-code block ##
class VerifyCodeView(APIView):
    """Проверка кода во время регистрации"""
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            number = serializer.validated_data.get('number')
            verification_code = serializer.validated_data.get('verification_code')
            # print(verification_code, ' current code from serializer')
            try:
                user = User.objects.get(number=number)

            except User.DoesNotExist:
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
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            code = generate_verification_code()
            # print(code, 'code from res')
            send_sms(user.number, code)
            user.verification_code = code
            user.save()

            return Response({'detail': 'SMS resent successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# password-reset block#
class PasswordResetView(APIView):
    """Сброс пароля. Этап отправки"""
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()

            if request.POST.get('number', False):
                code = generate_verification_code()
                num = request.data['number']
                send_reset_sms(num, code)
                user.reset_code = code
                user.save()

            if request.POST.get('email', False):
                code = generate_verification_code()
                email = request.data['email']
                send_reset_email(email, code)
                user.reset_code = code
                user.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyResetCodeView(APIView):
    """Проверка кода для сброса пароля"""
    def post(self, request):
        serializer = VerifyResetCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            number = serializer.validated_data.get('number')
            reset_code = serializer.validated_data.get('reset_code')

            try:
                if email:
                    user = User.objects.get(email=email)
                else:
                    user = User.objects.get(number=number)

            except User.DoesNotExist:
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if reset_code == user.reset_code:
                user.save()
                return Response({"message": "User got the access to his account"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "User didnt get the access to his account"},
                                status=status.HTTP_404_NOT_FOUND)

class SetNewPasswordView(APIView):
    """Установка нового пароля"""
    def post(self, request):
        serializer = NewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            number = serializer.validated_data.get('number')
            password1 = serializer.validated_data.get('password1')
            password2 = serializer.validated_data.get('password2')

            try:
                if email:
                    user = User.objects.get(email=email)


                else:
                    user = User.objects.get(number=number)

            except User.DoesNotExist:
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if password1 == password2:
                set_new_password(user, password2)
                return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


## email block
class EmailBindingView(APIView):
    """Привязка почты к аккаунту. Шаг 1 - отправка письма"""
    def post(self,request, user_id):
        serializer = EmailBindingSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get('email')

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

            email_code = generate_verification_code()
            send_verification_email(email_code=email_code, user_email=email)
            user.email_verification_code = email_code
            user.email = email
            user.save()
            # print(f'На почту {email}, был отправлен код {email_code}')
            return Response({'detail': 'email has sent successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailCodeView(APIView):
    """Проверка кода из email , для привязки почты"""
    def post(self, request, user_id):
        serializer = VerifyEmailCodeSerializer(data=request.data)

        if serializer.is_valid():
            email_code = serializer.validated_data.get('email_verification_code')
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error':'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
            if email_code == user.email_verification_code:
                user.save()
                return Response({"message": "User verified successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CenterRegistrationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, city):
        centers = get_centers().filter(city=city)
        return Response(CenterSerializer(centers, many=True).data, status=status.HTTP_200_OK)
