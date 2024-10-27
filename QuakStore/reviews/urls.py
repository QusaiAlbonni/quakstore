from django.urls import path, include

from .views import ReviewViewSet

urlpatterns = [
    path(
        "products/<slug:category_slug>/<slug:product_slug>/reviews/<int:pk>/",
        ReviewViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch':'partial_update',
            'delete': 'destroy'
        }),
        name="reviews-details"
    ),
    path(
        "products/<slug:category_slug>/<slug:product_slug>/reviews/",
        ReviewViewSet.as_view({
           'post': 'create',
           'get': 'list'
        }),
        name="reviews-list"     
    ),
    
]
