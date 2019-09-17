from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PatreonConfig(AppConfig):
    name = 'geeksbot_v2.patreon'
    verbose_name = _("Patreon")
