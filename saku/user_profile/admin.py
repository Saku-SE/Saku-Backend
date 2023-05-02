from django.contrib import admin

from .models import Profile, FollowRelationship

admin.site.register(Profile)
admin.site.register(FollowRelationship)
