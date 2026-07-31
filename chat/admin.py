from django.contrib import admin

# Register your models here.
from .models import Session, Message

admin.site.register(Session)
admin.site.register(Message)
