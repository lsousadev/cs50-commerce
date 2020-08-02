from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from datetime import datetime

from .models import User, Listing, Bid, Comment, Category


def index(request):
    listings = Listing.objects.filter(status=True).order_by('-timestamp_start')
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


def new_listing(request):
    categories = Category.objects.order_by('title').values_list('title', flat=True)
    if request.user.is_authenticated:
        username = request.user
    else:
        return render(request, "auctions/login.html", {
            "message": "Please log in before using this feature."
        })
    if request.method == "POST":
        if request.POST.get('url') is None:
            url = "https://i.imgur.com/OaN3lMh.jpg"
        else:
            url = request.POST.get('url')
        lst = Listing(
            creator = username,
            item_name = request.POST.get('item_name'),
            price_start = request.POST.get('price_start'),
            url = url,
            desc_short = request.POST.get('desc_short'),
            desc_long = request.POST.get('desc_long'),
            category = Category.objects.get(title=request.POST.get('category'))
        )
        lst.save()
        return render(request, "auctions/new_listing.html", {
            "categories": categories,
            "message": "Listing successfully added!"
        })
    return render(request, "auctions/new_listing.html", {
        "categories": categories
    })


def listing_page(request, listing_id):
    comments = Comment.objects.filter(listing=Listing.objects.get(id=listing_id)).order_by('-timestamp').all()
    if not request.user.is_authenticated:
        return render(request, "auctions/listing.html", {
                "listing": Listing.objects.get(id=listing_id),
                "message": "Please sign in to bid or comment.",
                "comments": comments
            })
    in_watchlist = False
    if Listing.objects.get(id=listing_id) in User.objects.get(id=request.user.id).watchlist.all():
        in_watchlist = True
    creator = False
    if Listing.objects.get(id=listing_id).creator == request.user:
        creator = True
    if request.method == "POST":
        if Listing.objects.get(id=listing_id).bids.last().price_bid > float(request.POST.get('bid')):
            return render(request, "auctions/listing.html", {
                "listing": Listing.objects.get(id=listing_id),
                "in_watchlist": in_watchlist,
                "message": "Bid must be higher than current price.",
                "creator": creator,
                "comments": comments
            })
        bid = Bid(
            user = request.user,
            listing = Listing.objects.get(id=listing_id),
            price_bid = float(request.POST.get('bid'))
        )
        bid.save()
        return render(request, "auctions/listing.html", {
            "listing": Listing.objects.get(id=listing_id),
            "in_watchlist": in_watchlist,
            "message": "Bid successfully placed.",
            "creator": creator,
            "comments": comments
        })
    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.get(id=listing_id),
        "in_watchlist": in_watchlist,
        "creator": creator,
        "comments": comments
    })


def watchlist_move(request, listing_id):
    if Listing.objects.get(id=listing_id) in request.user.watchlist.all():
        request.user.watchlist.remove(Listing.objects.get(id=listing_id))
    else:
        request.user.watchlist.add(Listing.objects.get(id=listing_id))
    return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))


def my_listings(request):
    if request.method == "POST":
        lst = Listing.objects.get(id=request.POST.get('close_listing'))
        lst.timestamp_end = datetime.now()
        lst.status = False
        lst.save()
    listings = Listing.objects.filter(creator=request.user).order_by('-timestamp_start')
    return render(request, "auctions/my_listings.html", {
        "listings": listings
    })


def auctions_won(request):
    filtered = []
    listings = Listing.objects.filter(status=False).all()
    for listing in listings:
        if listing.bids.last().user == request.user:
            filtered.append(listing)
    return render(request, "auctions/auctions_won.html", {
        "listings": filtered
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })


def category_page(request, cat_id):
    return render(request, "auctions/category_page.html", {
        "listings": Listing.objects.filter(category=Category.objects.get(id=cat_id)).filter(status=True).all(),
        "category": Category.objects.get(id=cat_id)
    })


def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "listings": request.user.watchlist.all()
    })


def comment(request, listing_id):
    if request.method == "POST":
        cmt = Comment(
            user = request.user,
            listing = Listing.objects.get(id=listing_id),
            content = request.POST.get("content")
        )
        cmt.save()
    return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))