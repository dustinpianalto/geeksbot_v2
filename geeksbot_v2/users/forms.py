from django.contrib.auth import forms
from django.forms import CharField
from allauth.account.forms import SignupForm

from .models import User


class UserCreateForm(SignupForm):
    id = CharField(max_length=30, label='Discord ID')

    def save(self, request):
        user = super(UserCreateForm, self).save(request)
        user.id = self.cleaned_data['id']
        user.save()
        return user


class UserChangeForm(forms.UserChangeForm):
    class Meta(forms.UserChangeForm.Meta):
        model = User
