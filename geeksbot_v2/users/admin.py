from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from .forms import UserChangeForm, UserCreateForm
from .models import User


class UserAdmin(auth_admin.UserAdmin):
    model = User
    form = UserChangeForm
    add_form = UserCreateForm
    add_fieldsets = auth_admin.UserAdmin.add_fieldsets + (
            (None, {'fields': ('id')}),
    )


admin.site.register(User, UserAdmin)
