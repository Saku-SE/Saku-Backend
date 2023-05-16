import os
import random
import string

from django.contrib.auth.models import User
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from subscription.models import Subscription

phone_validator = RegexValidator(
    regex=r"^09\d{9}$", message="Phone number is invalid (.eg '09123456789')"
)
national_id_validator = RegexValidator(
    regex=r"^\d{10}$", message="natinal id is invalid (.eg '1111111111')"
)


def photo_path(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    randomstr = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(10)
    )
    return "images/profile_images/{randomstring}{ext}".format(
        randomstring=randomstr, ext=file_extension
    )


class Profile(models.Model):
    TYPE_CHOICES = (("N", "natural"), ("L", "legal"))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    person_type = models.CharField(choices=TYPE_CHOICES, max_length=1, default="N")
    name = models.CharField(max_length=40, blank=True)
    # national_id = models.IntegerField(validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)])
    national_id = models.CharField(
        validators=[national_id_validator], max_length=10, blank=True
    )
    phone = models.CharField(validators=[phone_validator], max_length=11, blank=True)
    email = models.EmailField()
    city = models.CharField(max_length=20, blank=True)
    province = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=50, blank=True)
    profile_image = models.ImageField(upload_to=photo_path, null=True, blank=True)
    wallet = models.IntegerField(default=0, null=False, blank=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, default=None, null=True)

    def __str__(self):
        return self.name
    
class FollowRelationship(models.Model):
    follower = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="following")
    followed = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="followers")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower','followed'], name='follow_relation_pk')
        ]
