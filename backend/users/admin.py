from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class ProfileInline(admin.StackedInline):
    model = Profile
    fk_name = 'user'
    can_delete = False
    verbose_name_plural = 'Дополнительные данные пользователя'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role_id', 'full_name', 'status', 'created_at', 'created_by')
    list_editable = ('role_id', 'full_name', 'status', 'created_by')
    search_fields = ('user__username', 'user__email', 'full_name', 'role_id__name')
    list_filter = ('status', 'role_id')


admin.site.unregister(User)


@admin.register(User)
class ExtendedUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
