"""
Contains model definitions
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Modifies the default user model
    """
    time = models.DateTimeField(auto_now_add=True)
    watchlist = models.ManyToManyField("Listing", blank=True, related_name="watchers")

    def __str__(self):
        return self.username

class Listing(models.Model):
    """
    Models a listed item
        - 'currentBid' only gets updated once the first bid is made
        - 'active' stores whether the auction is ongoing - could be
          determined through 'winner', but is more readable this way
    """
    owner = models.ForeignKey(User, on_delete=models.SET("deleted"), related_name="listings")
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    startingPrice = models.DecimalField(max_digits=8, decimal_places=2)
    currentBid = models.ForeignKey("Bid", null=True, blank=True, on_delete=models.SET_NULL, related_name="highestBid")
    imageURL = models.URLField(max_length=200, blank=True)
    category = models.ForeignKey("Category", null=True, blank=True, on_delete=models.SET_NULL, related_name="listings")
    time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="winnings")

    def __str__(self):
        return f"{self.title} - {self.owner}"

class Bid(models.Model):
    """
    Models a bid on an item
    """
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bid = models.DecimalField(max_digits=8, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder}, {self.listing}, {self.bid}"

class Comment(models.Model):
    """
    Models a comment on an item listing
    """
    commenter = models.ForeignKey(User, on_delete=models.SET("deleted"), related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=500)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter}, {self.time}, {self.content}"

class Category(models.Model):
    """
    A category of listings
    """
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name
