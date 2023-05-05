from auction.models import Auction, Category, Tags
from django.contrib import admin
from auction.models import Auction, Tags, Category, Score, City


# Register your models here.

admin.site.register(Auction)
admin.site.register(Tags)
admin.site.register(Category)
admin.site.register(Score)
admin.site.register(City)
