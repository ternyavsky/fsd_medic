from django.contrib import admin
from django.utils.html import format_html

from .models import *


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'email', 'first_name', 'last_name', 'birthday', 'group',
                    'country', 'city', 'is_staff',
                    'is_required', 'created_at', 'updated_at', 'verification_code', 'email_verification_code']
    search_fields = ['login', 'number', 'email', 'first_name', 'last_name', ]
    list_editable = ['is_required', ]
    list_filter = ['group', 'country', 'disease',
                   'centers', 'is_staff', 'is_required', ]
    fields = ['id', 'number', 'email', 'first_name', 'last_name', 'birthday', 'group', 'centers', 'disease', 'country',
              'city', 'is_staff',
              'is_required', 'created_at', 'updated_at', 'verification_code', 'reset_code', 'email_verification_code']
    readonly_fields = ['id', 'number',  'first_name', 'last_name', 'birthday', 'group', 'is_staff',
                       'created_at', 'updated_at', 'country', 'city',]


class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'number_of_people']


class CountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name',]
    search_fields = ['name']
    fields = ['name']
    readonly_fields = ['id']


class CenterAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_required',  'country', 'address', 'lng', 'lat',
                    'created_at', 'updated_at']
    search_fields = ['name', 'address']
    list_editable = ['is_required']
    list_filter = ['is_required', 'country', 'created_at', 'updated_at']
    fields = ['name', 'is_required',  'country', 'address',
              ]
    readonly_fields = ['id', 'created_at', 'updated_at']


class UrlParamsAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_parameter', 'group']
    list_filter = ['group']
    fields = ['group']

    @admin.display
    def get_parameter(self, obj):
        return format_html(f'<a href="/registration/{obj}">registration/{obj}</a>')

    get_parameter.short_description = 'Ссылка'


admin.site.register(Center, CenterAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Interview)
admin.site.register(Country, CountryAdmin)
admin.site.register(News)
admin.site.register(Like)
admin.site.register(Disease)
admin.site.register(Saved)
admin.site.register(Clinic)
admin.site.register(Note)
admin.site.register(Url_Params, UrlParamsAdmin)
