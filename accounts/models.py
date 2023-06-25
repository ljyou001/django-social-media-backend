from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """
    This is the model only to save the user's profile
    Auth information is still stored in the default User model

    Learning Note
    While storing the user profiles
    You can also use this file to create the User model extending the django.contrib.auth.User model
    However, this is a bad practice:
    1. You need to go to the AbstractUser to see the all the fields
    2. You need to add AUTH_USER_MODEL in settings.py to use the User model you defined
    3. Data incapability while migrating from the dedfault User model

    The Advantage of seperation
    1. Fit for different use cases: User for auth, Profile for profile
    2. User model generally don't change that much, but profile will: differnt cache
    """

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    # What is OneToOneField?
    # It will create a unique index, to ensure one UserProfile only have one User instance
    # It is unique index + foreign key

    avatar = models.FileField(null=True)
    # Suggest to use FileField
    # ImageField in Django could lead to some problems
    # FileField will store avatar in the filesystem as file, then you can access them through URL
    # FileField have a "url" property already provided

    nickname = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return '{} {}'.format(self.user, self.nickname)
    
def get_profile(user):
    """
    This function is used to get the user's profile by user

    Why this function?
    We would like to use the User model to access its profile, however,
    we cannot directly modify User's file since it is an imported dependency

    In this case, we need to add a property for the User model:
    User.profile = property(get_profile)
    This is basically the same as:
    class User:
        @property
        def profile(self):
            ...
    This line of code will only apply after you start executing code, since it is not inside any class

    Moreover
    If you want to add property to dependent models
    you can use this method
    """
    if hasattr(user, '_cached_user_profile'):
    # We added a instance level cache here (user, '_cached_user_profile')
    # which means _cached_user_profile is following the user instance(object)
    # If the user instance has not changed, the cached value will be there and can be returned
        return getattr(user, '_cached_user_profile')
        # return user._cached_user_profile 
        # same but not recommended, as it is a protected variable, normally don't access directly
    profile, _ = UserProfile.objects.get_or_create(user=user)
    # Otherwise, go to the database, get_or_create the data for this user
    # Considering some user may have no profile, that's why we need to create
    setattr(user, '_cached_user_profile', profile)
    # Then, setattr according to the profile from the database
    return profile
    # Why use cache?
    # If we want to access the profile for multiple times, we don't need to access DB for each time


User.profile = property(get_profile)