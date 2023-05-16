from django.db import models

class Subscription(models.Model):
    name = models.CharField(max_length=40, blank=False, null=False, unique=True)
    description = models.CharField(max_length=200, blank=True)
    duration = models.IntegerField(null=False, blank=False) # duration in number of days
    price = models.IntegerField(null=False, blank=False)