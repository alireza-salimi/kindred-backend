from django.contrib import admin
from .models import *


class KindredMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'kindred', 'is_admin']


class KindredMemberInline(admin.TabularInline):
    model = KindredMember


class KindredAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [KindredMemberInline]


admin.site.register(Kindred, KindredAdmin)
admin.site.register(KindredMember, KindredMemberAdmin)
