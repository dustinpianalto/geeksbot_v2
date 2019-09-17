from django.contrib import admin

from .models import Message
from .models import GuildInfo
from .models import AdminRequest

# Register your models here.
admin.site.register(Message)
admin.site.register(GuildInfo)
admin.site.register(AdminRequest)