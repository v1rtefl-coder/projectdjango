from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Настройка отображения пользователей в админке"""

    list_display = ('email', 'username', 'phone_number', 'country', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'country')
    search_fields = ('email', 'username', 'phone_number')

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('avatar', 'phone_number', 'country'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('avatar', 'phone_number', 'country'),
        }),
    )
