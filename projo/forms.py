from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import PasswordResetForm
from django import forms

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'})
    )
    new_password2 = forms.CharField(
        label="Confirm new password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Enter your email address", 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email'})
    )
