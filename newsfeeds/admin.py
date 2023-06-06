from django.contrib import admin
from newsfeeds.models import NewsFeed

@admin.register(NewsFeed)
class NewsFeedAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'user',
        'tweet',
        'created_at',
    )