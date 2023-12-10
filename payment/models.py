import secrets

from django.db import models

from account.models import User


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    charge_id = models.CharField(max_length=200)
    status = models.CharField(max_length=7)
    ref = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(null=True, blank=True)
    channel = models.CharField(max_length=20, null=True, blank=True)
    currency = models.CharField(max_length=3, null=True, blank=True)
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-date_created',)
    
    def __str__(self):
        return self.user.email
    
    def save(self, *args, **kwargs):
        if not self.ref:
            ref = secrets.token_urlsafe(50)
            while Payment.objects.filter(ref=ref).exists():
                ref = secrets.token_urlsafe(50)
            self.ref = ref
        super().save(*args, **kwargs)
    
    def amount_value(self):
        return int(self.amount)

