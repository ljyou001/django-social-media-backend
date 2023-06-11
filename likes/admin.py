from django.contrib import admin
from likes.models import Like

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'user',
        'content_type',
        'object_id',
        'created_at',
    )
    list_filter = ('content_type',)