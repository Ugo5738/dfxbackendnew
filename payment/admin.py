from django.contrib import admin

from payment import models


class PaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "verified", "date_created"]


admin.site.register(models.Payment, PaymentAdmin)
