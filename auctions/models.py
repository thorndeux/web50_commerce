from django.contrib.auth.models import AbstractUser
from django.db import models
from djmoney.models.fields import MoneyField



class User(AbstractUser):
    time = models.DateTimeField(auto_now_add=True)
    watchlist = models.ManyToManyField("Listing", blank=True, related_name="watchers")

    def __str__(self):
        return self.username

class Listing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET("deleted"), related_name="listings")
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    startingBid = MoneyField(max_digits=8, decimal_places=2, default_currency='USD')
    currentBid = MoneyField(max_digits=8, decimal_places=2, default_currency='USD', null=True, default=None)
    imageURL = models.URLField(max_length=200, blank=True)
    category = models.ForeignKey("Category", null=True, on_delete=models.SET("deleted"), related_name="listings")
    time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, null=True, on_delete=models.SET("deleted"), related_name="winnings")

    def __str__(self):
        return f"{self.title} - {self.owner}"

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.SET("deleted"), related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bid = models.DecimalField(max_digits=8, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder}, {self.listing}, {self.bid}"

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.SET("deleted"), related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=500)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter}, {self.listing}, {self.content}"

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name
