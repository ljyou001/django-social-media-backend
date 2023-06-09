from rest_framework.permissions import BasePermission

class IsObjectOwner(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    This permission class is fairly generic, so you can put it into some share folder

    What is self defined permssion based on BasePermission?
    It requires you to implement the following objects (vars/functions):
    * message: what you want to show to the user if they don't have permission
    * has_object_permission: check if the user has permission. It is for the detail=True actions.
    * has_permission: check if the user has permission. It is for the detail=False actions.

    HERE comes the trick part: HOW to evaluate the user's permission
    1. If action is a detail=False action, only has_permission() checck the user's permission
    2. If action is a detail=True action, persmission check is True only when both function return True
    
    """

    message = 'You are not the owner of this object'

    def has_permission(self, request, view):
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the owner of the object for detail=True functions
        request: request from the client
        view: the view calling the 
        obj: the object to check

        How does this function obtain the object? 
        It will call the self.get_object
        """
        return obj.user == request.user