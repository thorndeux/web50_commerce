from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Category, Listing, User
from .my_forms import ListingForm

def index(request):
    listings = Listing.objects.all().order_by("-time")
    return render(request, "auctions/index.html", {
        "listings": listings
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def new_listing(request):
    if request.method == "POST":
        # Initialize new listing
        listing = Listing(owner=request.user)
        # Store submitted values
        form = ListingForm(request.POST)
        if form.is_valid():
            listing.title = form.cleaned_data["title"]
            listing.description = form.cleaned_data["description"]
            listing.startingBid = form.cleaned_data["startingBid"]
            listing.currentBid = listing.startingBid
            listing.imageURL = form.cleaned_data["image"]
            if form.cleaned_data["category"] == '0':
                listing.category = None
            else:
                listing.category = Category.objects.get(pk=int(form.cleaned_data["category"]))
            listing.winner = None
            listing.save()
        else:
            return render(request, "auctions/new_listing.html", {
                "form": form
            })
        return HttpResponseRedirect(reverse("index"))

    else:
        form = ListingForm()
        return render(request, "auctions/new_listing.html", {
            "form": form
        })

def listings(request, pk):
    listing = Listing.objects.get(pk=pk)
    if request.method == "POST":
        if "watchlist" in request.POST:
            watchlist = request.POST["watchlist"]
            user = request.user
            if watchlist == "checked":
                user.watchlist.remove(listing)
            else:
                user.watchlist.add(listing)
        return render(request, "auctions/listing.html", {
            "listing": listing
        })

    else:
        return render(request, "auctions/listing.html", {
            "listing": listing
        })
