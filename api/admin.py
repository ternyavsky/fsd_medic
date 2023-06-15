from django.contrib import admin
from .models import *


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'email', 'first_name', 'last_name','birthday', 'group', 'center', 'desease', 'country', 'city', 'is_staff',
                       'is_required', 'created_at', 'updated_at', ]
    search_fields = ['login', 'number', 'email', 'first_name', 'last_name', ]
    list_editable = ['is_required',]
    list_filter = ['group', 'country', 'center', 'is_staff', 'is_required', ]
    fields = ['id', 'number', 'email', 'first_name', 'last_name','birthday', 'group', 'center','country', 'city', 'is_staff',
                       'is_required', 'created_at', 'updated_at', ]
    readonly_fields = ['id', 'number', 'email', 'first_name', 'last_name','birthday', 'group', 'center', 'is_staff',
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


admin.site.register(Centers, CentersAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Groups, GroupsAdmin)
admin.site.register(Interviews)
admin.site.register(Countries, CountriesAdmin)
admin.site.register(News)
admin.site.register(Like)
admin.site.register(Desease)
