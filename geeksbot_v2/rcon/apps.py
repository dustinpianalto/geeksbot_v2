from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RconConfig(AppConfig):
    name = 'geeksbot_v2.rcon'
    verbose_name = _("Rcon")
