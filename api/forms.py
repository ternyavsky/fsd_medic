from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .service import get_number_code_list


class AdminRegistrationForm(forms.Form):
    number = forms.CharField(label=_('Номер:'))
    email = forms.CharField(label=_('Почта:'))
    first_name = forms.CharField(label=_('Имя:'))
    last_name = forms.CharField(label=_('Фамилия:'))
    password1 = forms.CharField(label=_('Пароль:'))
    password2 = forms.CharField(label=_('Подтверждение паролья:'))


class UserRegistrationForm(forms.Form):
    number_code = forms.ChoiceField(choices=get_number_code_list())
    number = forms.CharField(label=_('Номер:'))
    password1 = forms.CharField(label=_('Пароль:'))
    password2 = forms.CharField(label=_('Подтверждение паролья:'))
    center = forms.ModelChoiceField(label=_('Центр:'), queryset=Centers.objects.all(), empty_label='Выберите центр')
    is_patient = forms.BooleanField(label=_('Пациент?'), required=False, initial=True)
    code = forms.IntegerField(label=_('Код, который пришел вам на почту:'))
    agree_terms = forms.BooleanField(label=_('Согласен с условиями пользования:'), required=False, initial=True)

class InterviewRegistrationForm(forms.Form):
    type = forms.ChoiceField(choices=(('Врач', 'Врач'), ('Центр', 'Центр'), ('Клиника', 'Клиника')))
    first_name = forms.CharField(label=_('Имя:'))
    last_name = forms.CharField(label=_('Фамилия:'))
    number_code = forms.ChoiceField(choices=get_number_code_list())
    number = forms.CharField(label=_('Номер:'))
    email = forms.EmailField(label=_('Почта:'))


class InterviewRegistrationForm2(forms.Form):
    date = forms.DateTimeField(label=_('Дата провидения интервью:'))
    application = forms.ChoiceField(label='Приложение:',
                                    choices=(('Skipe', 'Skipe'), ('Zoom', 'Zoom'), ('В нашем', 'В шашем')))
    code = forms.IntegerField(label=_('Код, который пришел вам на почту:'))


class UserAuthorizationForm(forms.Form):
    email_or_number = forms.CharField(label=_('Почта или Номер:'))
    password = forms.CharField(label=_('Пароль:'))
