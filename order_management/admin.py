from django.contrib import admin

from order_management import models


class AddressAdmin(admin.ModelAdmin):
    list_display = []