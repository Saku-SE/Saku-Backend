from auction.models import Auction, Category, Tags
from django.contrib import admin

# Register your models here.

admin.site.register(Auction)
admin.site.register(Tags)
admin.site.register(Category)
