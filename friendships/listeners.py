def invalidate_following_cache(sender, instance, **kwargs):
    """
    Invalidate cache function while triggered by a signal

    Args:
        sender: The sender of the signal, same as the sender in the connect function
        instance: The instance being saved/deleted, dependes on the signal condition
        **kwargs: Any additional keyword arguments
    """
    from friendships.services import FriendshipService
    # Why import here? 
    # If it is outside of this function, there will be an error of circular import
    # Cuz FriendshipService will import friendships.models, and 
    # friendships.models will import this invalidate_following_cache
    # That's why we normally put this import into the function.
    # Force it import only when the function is executed
    FriendshipService.invalidate_following_cache(instance.from_user_id)