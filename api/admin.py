from django.contrib import admin
from django.utils.html import format_html

from .models import *


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'email', 'first_name', 'last_name', 'birthday', 'group', 'center', 'disease',
                    'country', 'city', 'is_staff',
                    'is_required', 'created_at', 'updated_at', ]
    search_fields = ['login', 'number', 'email', 'first_name', 'last_name', ]
    list_editable = ['is_required', ]
    list_filter = ['group', 'country', 'disease', 'center', 'is_staff', 'is_required', ]
    fields = ['id', 'number', 'email', 'first_name', 'last_name', 'birthday', 'group', 'center', 'disease', 'country',
              'city', 'is_staff',
              'is_required', 'created_at', 'updated_at', ]
    readonly_fields = ['id', 'number', 'email', 'first_name', 'last_name', 'birthday', 'group', 'center', 'is_staff',
                       'created_at', 'updated_at', 'country', 'city']


class GroupsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'number_of_people']


class CountriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'number_code', 'number_length']
    search_fields = ['name']
    fields = ['name', 'number_code', 'number_length']
    readonly_fields = ['id']


class CentersAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_required', 'employees_number', 'country', 'address', 'coordinate_latitude',
                    'coordinate_longitude', 'created_at', 'updated_at', ]
    search_fields = ['name', 'address']
    list_editable = ['is_required']
    list_filter = ['is_required', 'country', 'created_at', 'updated_at']
    fields = ['name', 'is_required', 'employees_number', 'country', 'address', 'coordinate_latitude',
              'coordinate_longitude']
    readonly_fields = ['id', 'created_at', 'updated_at']


class UrlParamsAdmin(admin.ModelAdmin):
    list_display = ['id','get_parameter','group_id']
    list_filter = ['group_id']
    fields = ['group_id']

    @admin.display
    def get_parameter(self, obj):
        return format_html(f'<a href="/registration/{obj}">registration/{obj}</a>')

    get_parameter.short_description = 'Ссылка'

admin.site.register(Centers, CentersAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Groups, GroupsAdmin)
admin.site.register(Interviews)
admin.site.register(Countries, CountriesAdmin)
admin.site.register(News)
admin.site.register(Like)
admin.site.register(Disease)
admin.site.register(Saved)
admin.site.register(Url_Params, UrlParamsAdmin)
