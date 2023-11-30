from django import forms


class CouponForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control ms-2 mb-3",
                "placeholder": "Enter coupon code here",
            }
        ),
        max_length=50,
    )