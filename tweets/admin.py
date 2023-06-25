from django.contrib import admin
from tweets.models import Tweet, TweetPhoto
# Register your models here.

@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'user', 
        'content', 
        'created_at', 
        'updated_at',
    )

@admin.register(TweetPhoto)
class TweetPhotoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'tweet',
        'order',
        'file',
        'status',
        'created_at',
        'has_deleted',
        'deleted_at',
    )
    list_filter = (
        'status',
        'has_deleted',
    )
    date_hierarchy = 'created_at'