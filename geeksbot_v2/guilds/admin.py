from django.contrib import admin

from geeksbot_v2.guilds.models import Guild
from geeksbot_v2.guilds.models import Role

# Register your models here.
admin.site.register(Guild)
admin.site.register(Role)