from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import User


class MyUserAdmin(UserAdmin):
    list_display = ['phone_number', 'first_name', 'last_name']
    search_fields = ['phone_number', 'first_name', 'last_name']
    ordering = ['last_name']
    fieldsets = (
        (_('Personal information'), {
            'fields': ('phone_number', 'first_name', 'last_name', 'date_of_birth', 'image', 'password')
        }),
        (_('Date information'), {
            'fields': ('date_joined', 'last_login')
        }),
        (_('Other information'), {
            'fields': ('is_staff', 'is_active', 'is_superuser', 'is_verified', 'user_permissions')
        })
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number', 'first_name', 'last_name', 'date_of_birth', 'image', 'password1', 'password2', 'user_permissions'
            )
        }),
    )


admin.site.register(User, MyUserAdmin)
