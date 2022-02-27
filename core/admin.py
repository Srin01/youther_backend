from django.contrib import admin

# Register your models here.
from core import models


admin.site.register(models.User)
admin.site.register(models.Post)
admin.site.register(models.Comment)