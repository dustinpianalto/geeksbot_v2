from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_username, user_field
from allauth.utils import valid_email_or_none
from django.conf import settings
from django.http import HttpRequest


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", False)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest, sociallogin: Any):
        return getattr(settings, "SOCIAL_ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(self, request, sociallogin, data):
#        print(sociallogin.account.extra_data)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        name = data.get('name')
        id = sociallogin.account.extra_data.get('id')
        user = sociallogin.user
        user_username(user, data.get('username', ''))
        user_email(user, valid_email_or_none(data.get('email')) or '')
        name_parts = (name or '').partition(' ')
        user_field(user, 'first_name', first_name or name_parts[0])
        user_field(user, 'last_name', last_name or name_parts[2])
        user_field(user, 'id', id or '')
        user_field(user, 'avatar', sociallogin.account.extra_data.get('avatar', ''))
        user_field(user, 'discriminator', sociallogin.account.extra_data.get('discriminator', ''))
        return user
