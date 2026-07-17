from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    """Отображает пользователей с полным именем, ролью и email в Админке."""

    list_display = (
        'full_name',
        'role',
        'email',
    )
    search_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('full_name', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Роль', {'fields': ('role',)}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'full_name', 'email', 'password1', 'password2', 'role'),
            },
        ),
    )
