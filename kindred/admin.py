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
    readonly_fields = ['unique_id']


class LocationAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at']
    list_display = ['user', 'coordinate', 'created_at']


class ShoppingItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_bought']
    readonly_fields = ['added_at']


admin.site.register(Kindred, KindredAdmin)
admin.site.register(KindredMember, KindredMemberAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(ShoppingItem, ShoppingItemAdmin)
