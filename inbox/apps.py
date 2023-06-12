from django.apps import AppConfig


class InboxConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inbox'

# Why use inbox but not indexes?
# Index is not a instancelized model.
# It is a common model used for the whole site
# Different users will have their own inbox based on their user id

# Why no models.py?
# Django-notification package has already provided the notification model
# We can directly import it

# Why not named "notification" app?
# Django-notification package has already provided the notification model using the name "notification"
# It also occupied the app called "notification"