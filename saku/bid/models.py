from django.contrib.auth.models import User
from django.db import models


class Bid(models.Model):
    time = models.DateTimeField(auto_now=True)
    price = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(to="auction.Auction", on_delete=models.CASCADE)
