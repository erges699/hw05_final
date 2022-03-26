# from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# from .models import PasswordReset

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


# class PasswordResetForm(forms.ModelForm):
#    class Meta:
#        model = PasswordReset
#        fields = ('email', 'old_password', 'new_password')
