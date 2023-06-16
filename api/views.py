import re
from rest_framework import generics
from django.shortcuts import render, redirect
from .forms import AdminRegistrationForm, UserRegistrationForm, UserAuthorizationForm, \
    InterviewRegistrationForm, InterviewRegistrationForm2
from .models import User, Countries, Centers, Url_Params, Email_Codes, Interviews, News
from .serializers import NewsSerializer, CreateUserSerializer
from django.contrib import messages
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from .models import User, Like
from django.contrib.auth import login, logout
from .service import Send_email, generate_email_code, create_or_delete
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import check_password
from .permissions import IsStaffUser

# REST IMPORTS
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes


# NEWS BLOCK
class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            news = News.objects.get(id=id)
            return create_or_delete(Like, user=request.user, news=news)
        except:
            return Response({'error': 'Запись не найдена!'}, status=status.HTTP_404_NOT_FOUND)



class NewsDetailView(APIView):

    @permission_classes([IsAuthenticated])
    def get(self, request, id):
        try:
            serializer = NewsSerializer(News.objects.get(id=id))
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Новость не найдена!'}, status=status.HTTP_404_NOT_FOUND)

    @permission_classes([IsAdminUser, IsStaffUser])
    def delete(self, request, id):
        try:
            news = News.objects.get(id=id)
            news.delete()
            return Response({'result': 'Новость удалена!'}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'error': 'Новость не найдена!'}, status=status.HTTP_404_NOT_FOUND)

    @permission_classes([IsAdminUser, IsStaffUser])
    def put(self, request, id):
        try:
            news = News.objects.get(id=id)
            serializer = NewsSerializer(news, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Новость не найдена!'}, status=status.HTTP_404_NOT_FOUND)


class NewsView(generics.ListCreateAPIView):

    @permission_classes([IsAuthenticated])
    def get(self, request):
        user = User.objects.get(id=request.user.id)
        if user.desease is not None:
            news = News.objects.filter(desease=user.desease)
        elif user.center is not None:
            news = News.objects.filter(center=user.center)
        else:
            return Response({'result': 'Для доступа к новостям, вам следует указать центр или заболевание'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = NewsSerializer(news, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # add doctor permission too
    @permission_classes([IsAdminUser, IsStaffUser])
    def post(self, request):
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateUserView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    model = User
    serializer_class = CreateUserSerializer

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def index(request):
    return render(request, template_name='api/index.html', context={'user': request.user, })


def LOGOUT(request):
    logout(request)
    return redirect('home_url')


@csrf_exempt
def ADMIN_SIGN_UP(request):
    # if request.user.is_staff:
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            number = data['number']
            form_is_valid = True
            number_pattern = re.compile('^[+]+[0-9]+$')
            email_pattern = re.compile('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            name_pattern = re.compile('^[а-яА-Я]+$')
            password_pattern = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]+$')
            # Проверка Имени
            if not name_pattern.match(data['first_name']):
                form_is_valid = False
                messages.error(request, 'Имя может состоять только из букв кирилицы')
            if len(data['first_name']) < 3:
                form_is_valid = False
                messages.error(request, 'Имя не может быть кароче 3 символов')
            if len(data['first_name']) > 20:
                form_is_valid = False
                messages.error(request, 'Имя не может быть длинее 20 символов')
            # Проверка Фамилии
            if not name_pattern.match(data['last_name']):
                form_is_valid = False
                messages.error(request, 'Фамилия может состоять только из букв кирилицы')
            if len(data['last_name']) < 3:
                form_is_valid = False
                messages.error(request, 'Фамилия не может быть кароче 3 символов')
            if len(data['last_name']) > 30:
                form_is_valid = False
                messages.error(request, 'Фамилия не может быть длинее 30 символов')
            # Проверка Номера
            if not number_pattern.match(data['number']):
                form_is_valid = False
                messages.error(request, 'Введен неоректный номер телефона')
            if User.objects.filter(number=number).exists() or Interviews.objects.filter(
                    number=number).exists():
                form_is_valid = False
                messages.error(request, 'Номер уже используется')
            # Проверка Почты
            if not email_pattern.match(data['email']):
                form_is_valid = False
                messages.error(request, 'Введена некоректная почта')
            if User.objects.filter(email=data['email']).exists() or Interviews.objects.filter(
                    email=data['email']).exists():
                form_is_valid = False
                messages.error(request, 'Почта уже используется')
            # Проверка паролей
            if not password_pattern.match(data['password1']):
                form_is_valid = False
                messages.error(request, 'Пароль должен состоять из цифр и букв обоих регистров')
            if len(data['password1']) < 8:
                form_is_valid = False
                messages.error(request, 'Пароль не может быть кароче 8 символов')
            if data['password1'] != data['password2']:
                form_is_valid = False
                messages.error(request, 'Пароли должны совподвать')

            if form_is_valid:
                User.objects.create_superuser(first_name=data['first_name'], last_name=data['last_name'],
                                              email=data['email'], number=number, password=data['password1'])
                messages.success(request, "Вы успешно создали учетную запись админа")
                return redirect('home_url')
        else:
            messages.error(request, 'Неизвестная ошибка на сервере')
    else:
        form = AdminRegistrationForm
    return render(request, template_name='api/CreateAdminForm.html',
                  context={'form': form, 'title': 'Sign up admin account'})


# raise Http404

@csrf_exempt
def USER_SIGN_UP(request):
    if not request.user.is_active:
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.cleaned_data
                country_number_code = data['number_code'].strip().rsplit("/", 1)
                number_code = country_number_code[0]
                number_length = country_number_code[1]
                number = number_code + data['number']
                form_is_valid = True
                number_pattern = re.compile('^\d{' + number_length + '}$')
                email_pattern = re.compile('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
                password_pattern = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]+$')
                # Проверка Номера
                if not number_pattern.match(data['number']):
                    form_is_valid = False
                    messages.error(request, 'Введен неоректный номер телефона')
                if User.objects.filter(number=number).exists() or Interviews.objects.filter(
                        number=number).exists():
                    form_is_valid = False
                    messages.error(request, 'Номер уже используется')
                # Проверка Почты
                if not email_pattern.match(data['email']):
                    form_is_valid = False
                    messages.error(request, 'Введена некоректная почта')
                if User.objects.filter(email=data['email']).exists() or Interviews.objects.filter(
                        email=data['email']).exists():
                    form_is_valid = False
                    messages.error(request, 'Почта уже используется')
                # Проверка паролей
                if not password_pattern.match(data['password1']):
                    form_is_valid = False
                    messages.error(request, 'Пароль должен состоять из цифр и букв обоих регистров')
                if len(data['password1']) < 8:
                    form_is_valid = False
                    messages.error(request, 'Пароль не может быть кароче 8 символов')
                if data['password1'] != data['password2']:
                    form_is_valid = False
                    messages.error(request, 'Пароли должны совподвать')
                # Проверка Соглашения
                if not data['agree_terms']:
                    form_is_valid = False
                    messages.error(request, 'Вы обязательно должны принять условия соглашения')
                if form_is_valid:
                    user = User.objects.create_user(number=number, email=data['email'], password=data['password1'])
                    parameter = get_random_string(length=50)
                    par_obj = Url_Params(parameter=parameter, user_id=user.id)
                    par_obj.save()

                    message = f"Здравствуйте! Для того чтобы продолжить регистрацию вам необходимо заполнить поля перейдя по этой ссылкe http://127.0.0.1:8000/userparameters/{parameter} и ссылка на нашу почту для контакта с нами"
                    Send_email(user_email=data['email'], message=message)
                    # send_sms(number, message)

                    messages.success(request,
                                     "Вам пришло письмо на номер телефона.Перейдите по ссылке в нем для продолжения регистрации")
                    return redirect('home_url')
            else:
                messages.error(request, 'Ошибка при заполнении формы')
        else:
            form = UserRegistrationForm
        return render(request, template_name='api/CreateUserForm.html',
                      context={'form': form, 'title': 'Регистрация'})
    raise Http404


@csrf_exempt
def USER_SIGN_UP_2(request, parameter):
    if not request.user.is_active and Url_Params.objects.filter(
            parameter=parameter).exists():
        user_id = Url_Params.objects.get(parameter=parameter).user_id
        user = User.objects.get(id=user_id)
        if not Email_Codes.objects.filter(user_id=user_id).exists():
            email_code = generate_email_code()
            code_obj = Email_Codes(code=email_code, user_id=user_id)
            code_obj.save()
            Send_email(user_email=user.email,
                       message=f'Ваш код для подтверждения:{email_code}')
        if request.method == 'POST':
            form = ''
            if form.is_valid():
                user_code = Email_Codes.objects.get(user_id=user_id)
                data = form.cleaned_data
                form_is_valid = True
                if user_code.code != data['code']:
                    form_is_valid = False
                    messages.error(request, 'Неверный код')
                if form_is_valid:
                    User.objects.update_user(user=user, center=Centers.objects.get(name=data['center']),
                                             is_patient=data['is_patient'])
                    login(request, user)
                    Url_Params.objects.get(parameter=parameter).delete()
                    user_code.delete()
                    return redirect('home_url')
            else:
                messages.error(request, 'Ошибка при заполнении формы')
        else:
            form = ''
        return render(request, template_name='api/CreateUserForm2.html',
                      context={'title': 'Регистрация',
                               'form': form, 'parameter': parameter})
    raise Http404


def LIKE(request, news_id):
    if request.user.is_active:
        if request.method == 'POST':
            create_or_delete(Like, news=news_id, user=request.user)
            return redirect('home_url')
        else:
            messages.error(request, 'Ошибка!')
    else:
        raise Http404


def INTERVIEW_SIGN_UP(request):
    if request.method == 'POST':
        form = InterviewRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Проверка уникальности почты
            data = form.cleaned_data
            number = data['number_code'] + data['number']
            country_number_code = data['number_code'].strip().rsplit("/", 1)
            number_code = country_number_code[0]
            number_length = country_number_code[1]
            number = number_code + data['number']
            form_is_valid = True
            number_pattern = re.compile('^\d{' + number_length + '}$')
            email_pattern = re.compile('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            password_pattern = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]+$')
            name_pattern = re.compile('^[а-яА-Я]+$')
            # Проверка Имени
            if not name_pattern.match(data['first_name']):
                form_is_valid = False
                messages.error(request, 'Имя может состоять только из букв кирилицы')
            if len(data['first_name']) < 3:
                form_is_valid = False
                messages.error(request, 'Имя не может быть кароче 3 символов')
            if len(data['first_name']) > 20:
                form_is_valid = False
                messages.error(request, 'Имя не может быть длинее 20 символов')
            # Проверка Фамилии
            if not name_pattern.match(data['last_name']):
                form_is_valid = False
                messages.error(request, 'Фамилия может состоять только из букв кирилицы')
            if len(data['last_name']) < 3:
                form_is_valid = False
                messages.error(request, 'Фамилия не может быть кароче 3 символов')
            if len(data['last_name']) > 30:
                form_is_valid = False
                messages.error(request, 'Фамилия не может быть длинее 30 символов')
            # Проверка Номера
            if not number_pattern.match(data['number']):
                form_is_valid = False
                messages.error(request, 'Введен неоректный номер телефона')
            if User.objects.filter(number=number).exists() or Interviews.objects.filter(
                    number=number).exists():
                form_is_valid = False
                messages.error(request, 'Номер уже используется')
            # Проверка Почты
            if not email_pattern.match(data['email']):
                form_is_valid = False
                messages.error(request, 'Введена некоректная почта')
            if User.objects.filter(email=data['email']).exists() or Interviews.objects.filter(
                    email=data['email']).exists():
                form_is_valid = False
                messages.error(request, 'Почта уже используется')
            if form_is_valid:
                interview = Interviews(type=data['type'],
                                       first_name=data['first_name'],
                                       last_name=data['last_name'], number=number,
                                       email=data['email'])
                interview.save()

                parameter = get_random_string(length=50)
                par_obj = Url_Params(parameter=parameter, interview_id=interview.id)
                par_obj.save()

                message = f"Здравствуйте! Для того чтобы продолжить регистрацию вам необходимо назначить собеседовние заполнив поля перейдя по этой ссылкe http://127.0.0.1:8000/interviewparameters/{parameter}"
                Send_email(user_email=interview.email, message=message)
                # send_sms(obj.number, message)

                messages.success(request,
                                 "Вам пришло письмо на номер телефона.Перейдите по ссылке для назначения собеседования")
                return redirect('home_url')
        else:
            messages.error(request, 'Ошибка при заполнении формы')
    else:
        form = InterviewRegistrationForm
    return render(request, template_name='api/CreateInterviewForm1.html',
                  context={'title': 'Регистрация интервью',
                           'form': form, })


@csrf_exempt
def INTERVIEW_SIGN_UP_2(request, parameter):
    if Url_Params.objects.filter(
            parameter=parameter).exists():
        interview_id = Url_Params.objects.get(parameter=parameter).interview_id
        interview = Interviews.objects.get(id=interview_id)
        if not Email_Codes.objects.filter(interview_id=interview_id).exists():
            email_code = generate_email_code()
            code_obj = Email_Codes(code=email_code, interview_id=interview_id)
            code_obj.save()
            Send_email(user_email=interview.email,
                       message=f'Ваш код для подтверждения:{email_code}')
        if request.method == 'POST':
            form = InterviewRegistrationForm2(request.POST, request.FILES)
            if form.is_valid():
                interview_code = Email_Codes.objects.get(interview_id=interview_id)
                data = form.cleaned_data
                form_is_valid = True
                if interview_code.code != data['code']:
                    form_is_valid = False
                    messages.error(request, 'Неверный код')
                if form_is_valid:
                    interview.date = data['date']
                    interview.application = data['application']
                    interview.is_required = True
                    interview.save(update_fields=['date', 'application', 'is_required', 'updated_at'])
                    messages.success(request,
                                     "Заявка была успешно отправлена.В указанное время вам придет письмо на номер телефона с приглашением на собеседование")
                    Url_Params.objects.get(parameter=parameter).delete()
                    interview_code.delete()
                    return redirect('home_url')
            else:
                messages.error(request, 'Ошибка при заполнении формы')
        else:
            form = InterviewRegistrationForm2
        return render(request, template_name='api/CreateInterviewForm2.html',
                      context={'title': 'Регистрация интервью',
                               'form': form, 'parameter': parameter})
    else:
        raise Http404


def USER_SIGN_IN(request):
    if not request.user.is_active:
        if request.method == "POST":
            form = UserAuthorizationForm(request.POST, request.FILES)
            if form.is_valid():
                email_or_number = form.cleaned_data.get('email_or_number')
                password = form.cleaned_data.get('password')
                users = User.objects.filter(is_required=True)
                # Проверка по номеру
                if users.filter(number=email_or_number).exists():
                    user = users.get(number=email_or_number).exists()
                    if user.check_password(password):
                        login(request, user)
                        return redirect('home_url')
                    else:
                        messages.error(request, 'Неверно введены данные для регистрации')
                # Проверка по почте
                if users.filter(
                        email=email_or_number).exists():
                    user = users.get(email=email_or_number)
                    if user.check_password(password):
                        login(request, user)
                        return redirect('home_url')
                    else:
                        messages.error(request, 'Неверно введены данные для регистрации')
                else:
                    messages.error(request, 'Неверно введены данные для регистрации')
            else:
                messages.error(request, "Ошибка при заполнении формы")
        else:
            form = UserAuthorizationForm
        return render(request, template_name='api/LoginUserForm.html',
                      context={'title': 'Авторизация', 'form': form})
    else:
        raise Http404


def Account(request):
    if request.user.is_active:
        return render(request, template_name='api/AccountView.html',
                      context={'title': 'Аккаунт', 'user': request.user})
    else:
        raise Http404
