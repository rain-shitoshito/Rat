from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(BotNet)
admin.site.register(Command)
admin.site.register(UpFile)
admin.site.register(DownFile)
