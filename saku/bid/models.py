from django.db import models
from django.contrib.auth.models import User

  
def get_default_user_id():
    filter = User.objects.filter(username="unkown_reserved_user")
    if filter.exists():
        return filter.first().id
    else:
        default = User.objects.create(username="unkown_reserved_user")
        return default.id


class Bid(models.Model):
    time = models.DateTimeField(auto_now=True)
    price = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET(get_default_user_id))
    auction = models.ForeignKey(to="auction.Auction", on_delete=models.CASCADE)
