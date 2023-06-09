from django.contrib import admin

from comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tweet', 'content', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)