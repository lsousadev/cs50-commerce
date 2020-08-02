from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ModelForm

from datetime import datetime


class User(AbstractUser):
    full_name = models.CharField(max_length=32)
    watchlist = models.ManyToManyField('Listing', blank=True)

class Listing(models.Model):
    creator = models.ForeignKey('User', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=32)
    desc_short = models.CharField(max_length=64)
    price_start = models.DecimalField(max_digits=8, decimal_places=2)
    url = models.URLField(null=True, blank=True)
    desc_long = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    timestamp_start = models.DateTimeField(default=datetime.now())
    timestamp_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.item_name} - ${self.price_start} by {self.creator}"

class Bid(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name="bids")
    price_bid = models.DecimalField(max_digits=8, decimal_places=2)
    timestamp = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return f"${self.price_bid} by {self.user} at {self.timestamp}"

class Comment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return f"Comment on {self.listing.item_name} at {self.timestamp} by {self.user}"

class Category(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.title}"
