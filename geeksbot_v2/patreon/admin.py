from django.contrib import admin


from .models import PatreonCreator
from .models import PatreonTier

# Register your models here.
admin.site.register(PatreonCreator)
admin.site.register(PatreonTier)