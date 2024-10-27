from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import HttpRequest

class OwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view): 
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return True
        
        return False
        
    def has_object_permission(self, request: HttpRequest, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if (request.method in ('PUT', 'PATCH')) and request.user.is_authenticated and (request.user == obj.user):
            return True
        
        return False