from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'avatar', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'


class UserProfileInline(admin.StackedInline):
    """
    Why this class?
    You can change the user profile content while you are modifying the User model
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'user_profiles'


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'date_joined')
    date_hierarchy = 'date_joined'
    inlines = (UserProfileInline, )


admin.site.unregister(User)
# This is to unregister the existing User model in the admin panel 
admin.site.register(User, UserAdmin)
# This is to register our own User model in the admin panel