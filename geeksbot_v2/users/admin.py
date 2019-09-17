from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from .forms import UserChangeForm
from .models import User


class UserAdmin(auth_admin.UserAdmin):
    model = User
    form = UserChangeForm


admin.site.register(User, UserAdmin)
