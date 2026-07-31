from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Agent, Tool, Conversation, AgentTool

admin.site.register(Agent)
admin.site.register(Tool)
admin.site.register(Conversation)
admin.site.register(AgentTool)
