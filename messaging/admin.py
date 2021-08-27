from django.contrib import admin
from .models import Message, DefaultMessage


class MessageAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'sent_from', 'sent_to']


class DefaultMessageAdmin(admin.ModelAdmin):
    list_display = ['content', 'kindred']


admin.site.register(Message, MessageAdmin)
admin.site.register(DefaultMessage, DefaultMessageAdmin)
