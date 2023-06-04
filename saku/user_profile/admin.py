from django.contrib import admin

from .models import Profile, FollowRelationship, Ticket

admin.site.register(Profile)
admin.site.register(FollowRelationship)
admin.site.register(Ticket)
