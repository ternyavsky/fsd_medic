import re

from rest_framework.generics import UpdateAPIView, RetrieveAPIView

from django.core.mail import send_mail
from rest_framework import generics
from rest_framework import serializers
from django.shortcuts import render, redirect

from .models import User, Countries, Centers, Url_Params, EmailCodes, Interviews, News, Saved, Groups, Clinics, Notes, \
    Disease

from .serializers import *

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Like
from django.contrib.auth import login, logout
from .service import Send_email, generate_email_code, create_or_delete, generate_verification_code, send_sms, \
    send_reset_email, send_reset_sms, send_verification_email
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import check_password
from .permissions import IsAdminOrReadOnly
import os
from django.contrib.auth import get_user_model
import json
import requests
import random
from django.shortcuts import get_object_or_404
from django.db.models import Q
# REST IMPORTS
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes, action, api_view


def index(request):
    return render(request, template_name='api/index.html')


# def generate_verification_code():
#     code = random.randint(1000, 9999)
#     return str(code)


def registration(request, parameter):
    if Url_Params.objects.filter(parameter=parameter).exists():
        group_id = Url_Params.objects.get(parameter=parameter).group_id
        group_name = Groups.objects.get(id=group_id).name
        if group_name == 'Администраторы':
            return HttpResponse('Здесь будет форма регистрации админа')
        elif group_name == 'Администраторы Центров':
            return HttpResponse('Здесь будет форма регистрации центра и его админа')
        elif group_name == 'Администраторы Клиник':
            return HttpResponse('Здесь будет форма регистрации клиники и его админа')
        elif group_name == 'Врачи':
            return HttpResponse('Здесь будет форма регистрации врача')
    raise Http404



### NEWS BLOCK ###


class SaveView(generics.ListCreateAPIView):
    permission_classes  = [IsAuthenticated]
    queryset = Saved.objects.all()

    def get(self, request):
        saved = self.queryset.filter(user=request.user)
        serializer = SavedSerializer(saved, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            return create_or_delete(Saved, SavedSerializer, user=request.user, news=News.objects.get(id=request.data["news"]))
        except:
            return Response({'error': 'Запись не найдена!'}, status=status.HTTP_404_NOT_FOUND)



class LikeView(APIView):  # Append and delete like
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        like = self.queryset.filter(user=request.user)
        serializer = LikeSerializer(like, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            return create_or_delete(Like, LikeSerializer, user=request.user, news=News.objects.get(id=request.data["news"]))
        except:
            return Response({'error': 'Запись не найдена!'}, status=status.HTTP_404_NOT_FOUND)


class NewsDetailView(APIView):  # Single news view
    permission_classes = [IsAdminOrReadOnly]
    error_response = {'error': 'Новость не найдена!'}

    def get(self, request, id):  # get single news
        news = get_object_or_404(News, id=id)
        serializer = CreateNewsSerializer(news)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):  # delete single news
        news = get_object_or_404(News, id=id)
        news.delete()
        return Response({'result': 'Новость удалена!'}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, id):  # update single news
        news = get_object_or_404(News, id=id)
        serializer = CreateNewsSerializer(news, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response(self.error_response, status=status.HTTP_404_NOT_FOUND)
        return super().handle_exception(exc)


class NewsView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]  # Only authenticated users can access all news
    serializer_class = NewsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return News.objects.all()

        if user.is_authenticated:
            try:
                center_news = News.objects.filter(center__in=user.center.all())
                disease_news = News.objects.filter(disease__in=user.disease.all())
                return center_news.union(disease_news)
            except:
                raise serializers.ValidationError('Для доступа к новостям, вам следует указать центр или заболевание')

        else:
            return News.objects.all()[:3]


    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = NewsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


### SEARCH ###


class SearchView(APIView):
    def get(self, request, *args, **kwargs):
        clinics = Clinics.objects.all()
        centers = Centers.objects.all()
        users = User.objects.filter()
        search_results = {
            'clinics': clinics,
            'centers': centers,
            'users': users,
        }
        serializer = SearchSerializer(search_results)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NoteView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        notes = Notes.objects.all().filter(user=request.user)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NoteDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, note_id):
        obj = Notes.objects.get(id=note_id)
        serializer = NoteSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, note_id):
        obj = Notes.objects.get(id=note_id)
        serializer = NoteUpdateSerializer(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(NoteSerializer(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, note_id):
        obj = Notes.objects.get(id=note_id)
        obj.delete()
        return Response({'result': 'deleted'}, status=status.HTTP_204_NO_CONTENT )


### USER BLOCK ###

### RESET PASSWORD BLOCK ###
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


def set_new_password(user, new_password):

    user.set_password(new_password)
    user.save()
### END RESET PASSWORD BLOCK###


### USERS' CLASSES ###
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
            # print(code, '-code')
            if int(request.data['stage']) == 3:
                send_sms(user.number, code)
                user.verification_code = code
                user.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

class UserDetailView(generics.RetrieveUpdateAPIView):
    """Получение, редактирование отдельного пользователя по id"""
    serializer_class = UserGetSerializer
    queryset = User.objects.all()




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
            print(f'На почту {email}, был отправлен код {email_code}')
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
                print('код прошел проверку')
                user.save()
                return Response({"message": "User verified successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

## END USERS' CLASSES ###
class CenterRegistrationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        centers = Centers.objects.all().filter(city=request.data["city"])
        return Response(CenterSerializer(centers, many=True).data, status=status.HTTP_200_OK)


class GetDiseasesView(APIView):
    def get(self, request):
        diseases = Disease.objects.all()
        serializer = DiseaseSerializer(diseases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class UpdateUserView(generics.ListCreateAPIView):
#
#     permission_classes = [AllowAny]
#     model = User
#     serializer_class = CreateUserSerializer
#
#     def post(self, request):
#         serializer = CreateUserSerializer()
#         # serializer.update(instance=request.user, validated_data=request.data)
#         serializer.update(validated_data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


def LOGOUT(request):
    logout(request)
    return redirect('home_url')


@csrf_exempt
def LIKE(request, news_id):
    if request.user.is_active:
        if request.method == 'POST':
            create_or_delete(Like, news=news_id, user=request.user)
            return redirect('home_url')
        else:
            messages.error(request, 'Ошибка!')
    else:
        raise Http404


def Account(request):
    if request.user.is_active:
        return render(request, template_name='api/AccountView.html',
                      context={'title': 'Аккаунт', 'user': request.user})
    else:
        raise Http404
