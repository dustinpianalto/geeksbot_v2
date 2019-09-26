from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ChannelsConfig(AppConfig):
    name = 'geeksbot_v2.channels'
    verbose_name = _("Channels")
