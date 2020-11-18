"""
Contains view functions
"""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Bid, Category, Comment, Listing, User
from .forms import ListingForm, AddBid, AddComment


def index(request):
    """
    Default view displaying all active listings
    """
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True).order_by("-time")
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
                "message": "Invalid username and/or password.",
                "type": "danger"
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
                "message": "Passwords must match.",
                "type": "danger"

            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken.",
                "type": "danger"
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def new_listing(request):
    """
    Displays and handels form to create a new listing    
    """
    # If reached by form submission
    if request.method == "POST":
        # Initialize new listing
        listing = Listing(owner=request.user)
        # Store submitted values
        form = ListingForm(request.POST)
        # Validate form
        if form.is_valid():
            # Set required values
            listing.title = form.cleaned_data["title"]
            listing.description = form.cleaned_data["description"]
            listing.startingBid = form.cleaned_data["startingBid"]
            # Set optional values
            if form.cleaned_data["imageURL"]:
                listing.imageURL = form.cleaned_data["imageURL"]
            if form.cleaned_data["category"]:
                listing.category = form.cleaned_data["category"]
            # Save listing
            listing.save()
            
        # If form is invalid, rerender page with current form values
        else:
            return render(request, "auctions/new_listing.html", {
                "form": form,
                "message": "Your submission was invalid, please check again.",
                "type": "danger"
            })
        # Render index page
        return render(request, "auctions/index.html", {
            "listings": Listing.objects.filter(active=True).order_by("-time"),
            "message": "Your listing has been added",
            "type": "success"
            })
    # If reached by GET request, display empty form
    else:
        form = ListingForm()
        return render(request, "auctions/new_listing.html", {
            "form": form
        })


def listings(request, pk):
    """
    Displays listing details and allows interacting
    with a listing: bidding, adding/removing from watchlist,
    and leaving comments. Also allows the owner to close the
    auction.

    Args:
        pk: Primary key of a listing
    """
    # Get matching listing object
    listing = Listing.objects.get(pk=pk)
    # Handle various POST requests
    if request.method == "POST":
        # Get current user
        user = request.user
        # Initialize messaging variables
        message = None
        message_type = None
        # Handle adding to/removing from watchlist
        if "watchlist" in request.POST:
            watchlist = request.POST["watchlist"]
            if watchlist == "checked":
                user.watchlist.remove(listing)
                message = "The listing has been removed from your watchlist."
                message_type = "success"
            else:
                user.watchlist.add(listing)
                message = "The listing has been added to your watchlist."
                message_type = "success"
        # Handle new bid        
        elif "new_bid" in request.POST:
            # Get bid value
            new_bid = float(request.POST["bid"])
            # If bid is too low, set respective message variables
            if (listing.currentBid is not None and new_bid < listing.currentBid.bid):
                message = "Your bid must be higher than the current bid."
                message_type = "danger"
            elif new_bid < listing.startingBid:
                message = "Your bid must be higher than the starting bid."
                message_type = "danger"
            # If bid is valid
            else:
                # Create and save the bid
                bid = Bid()
                bid.bidder = user
                bid.listing = listing
                bid.bid = new_bid
                bid.save()
                # Update listing
                listing.currentBid = bid
                listing.save()
                # Set message variables
                message = "Your bid has been added to the auction."
                message_type = "success"
        # Handle new comment
        elif "new_comment" in request.POST:
            # Create and save comment
            comment = Comment()
            comment.commenter = user
            comment.listing = listing
            comment.content = request.POST["comment"]
            comment.save()
            # Set message variables
            message = "Your comment has been added"
            message_type = "success"
        # Handle closing of auction by the owner
        elif "close" in request.POST:
            # If there has been a bid, set the winner
            if listing.currentBid:
                listing.winner = listing.currentBid.bidder
            # Set listing to inactive and save
            listing.active = False
            listing.save()
            # Set message variables
            message = "Your auction has been closed"
            message_type = "success"
            # Render index page with appropriate message
            return render (request, "auctions/index.html", {
                "listings": Listing.objects.filter(active=True).order_by("-time"),
                "message": message,
                "type": message_type
            })
        # Render listing page passing message variables, comments, and forms
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "message": message,
            "type": message_type,
            "comments": listing.comments.all().order_by("-time"),
            "bid_form": AddBid(auto_id=False),
            "comment_form": AddComment(auto_id=False)
        })
    # On GET request, render listing page passing comments and forms
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": listing.comments.all().order_by("-time"),
            "bid_form": AddBid(auto_id=False),
            "comment_form": AddComment(auto_id=False)
        })


@login_required
def watchlist(request, username):
    """
    Displays all listings on a user's watchlist

    Args:
        username: Username of the logged in user.
                  Only for aesthetic purpose.
    """
    listings = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


def categories(request, name=None):
    """
    Handles both displaying a list of all categories,
    as well as pages for the individual categories.

    Args:
        name (optional): Category name. Defaults to None.
    """
    # If no argument is passed, render a list of categories
    if name is None:
        categories = Category.objects.all().order_by("name")
        return render(request, "auctions/categories.html", {
            "categories": categories
        })
    # If a category name is passed, render all listings of that category
    else:
        category = Category.objects.get(name=name)
        listings = category.listings.filter(active=True).order_by("-time")
        return render(request, "auctions/category.html", {
            "category": category,
            "listings": listings
        })
