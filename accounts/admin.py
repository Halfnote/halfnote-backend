from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Add custom fields to the admin interface
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('bio', 'avatar_url', 'favorite_genres', 'following')
        }),
    )
    
    # Display these fields in the user list
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    
    # Add filters
    list_filter = BaseUserAdmin.list_filter + ('date_joined',)
    
    # Add search functionality
    search_fields = ('username', 'email', 'first_name', 'last_name', 'bio')
    
    # Make following field display nicely
    filter_horizontal = ('following',) 