from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from django.utils.timesince import timesince
from django.utils.timezone import datetime, now
from django.utils.translation import gettext_lazy as _

from .models import Review

from users.serializers import PublicUserSerializer


class ReviewSerializer(serializers.ModelSerializer):
    added_since = serializers.SerializerMethodField()
    modified_since=serializers.SerializerMethodField()
    user = PublicUserSerializer(read_only=True)
    absolute_url = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'product',
            'rating',
            'comment',
            'date_added',
            'date_modified',
            'added_since',
            'modified_since',
            'absolute_url'
        ]
    
    def get_added_since(self, obj: Review):
        return timesince(obj.date_added, now())

    def get_modified_since(self, obj: Review):
        return timesince(obj.date_modified, now())
    
    def get_absolute_url(self, obj):
        request = self.context['request']
        return f"{request.scheme}://{request.get_host()}" + obj.get_absolute_url()
    
    
    
class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'user',
            'product',
            'rating',
            'comment',
        ]

    validators = [
        UniqueTogetherValidator(
            queryset=Review.objects.all(),
            fields=['user', 'product'],
            message=_("You cannot have duplicate Reviews for Products")
        ),
    ]

class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'rating',
            'comment',
        ]