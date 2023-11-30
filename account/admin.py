from django.contrib import admin

from account import models


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_full_name', 'username', 'email', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']
        

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'bio', 'address', 'country', 'zip_code', 'address_verified']
    search_fields = ['country', 'address_verified']
      

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Profile, ProfileAdmin)