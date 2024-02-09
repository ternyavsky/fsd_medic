from django.contrib import admin
from django.utils.html import format_html

from .models import *


# Register your models here.





# class CenterAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name', 'is_required',  'country', 'address', 'lng', 'lat',
#                     'created_at', 'updated_at']
#     search_fields = ['name', 'address']
#     list_editable = ['is_required']
#     list_filter = ['is_required', 'country', 'created_at', 'updated_at']
#     fields = ['name', 'is_required',  'country', 'address',
#               ]
#     readonly_fields = ['id', 'created_at', 'updated_at']

admin.site.register(Center)
admin.site.register(User)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(News)
admin.site.register(Like)
admin.site.register(Disease)
admin.site.register(Saved)
admin.site.register(Clinic)
admin.site.register(Note)
admin.site.register(Subscribe)
