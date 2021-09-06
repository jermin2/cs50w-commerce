from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django import forms

from .models import User, Listing, Bid, Comment


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True),
        "title": "All Active Listings"
    })

def listings(request, id):
    user = User.objects.get(id=id)

    return render(request, "auctions/user_index.html", {
        "user":user
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

def listing(request, id):
    # Check if id exists
    try:
        listing = Listing.objects.get(id=id)

    except:
        return render(request, "auctions/error.html", {
            "title": "Error 404: Page not found",
            "message": f"Listing with id of {id} does not exist"
        })

    # Show listing
    return render(request, "auctions/listing.html", {
        "listing": listing,
    })

@login_required
def watchlist_add(request, id):
    # Check if ID exists in watchlist
    try:
        l = Listing.objects.get(id=id)
        request.user.watchlist.add(l)
    except:
        pass

    return HttpResponseRedirect(reverse("listing", args=(id,))) 

@login_required
def watchlist_remove(request, id):
    # Check if ID exists in watchlist
    try:
        l = Listing.objects.get(id=id)
        request.user.watchlist.remove(l)
    except:
        pass
    
    return HttpResponseRedirect(reverse("listing", args=(id,))) 

@login_required
def watchlist(request):
    return render(request, "auctions/index.html", {
        "listings": request.user.watchlist.all(),
        "title": "My Watchlist"
    })

@login_required
def new(request):
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = NewListingForm(request.POST)

        # Check if form is valid
        if form.is_valid():

            # Isolate the data from the 'cleaned' version
            name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]
            image = form.cleaned_data["image"]
            start_price = form.cleaned_data["start_price"]
            category = form.cleaned_data["category"]

            try:
                listing = Listing.objects.create(owner=request.user, 
                    name=name, 
                    description=description, 
                    start_price=start_price, 
                    image=image,
                    category=category)
                listing.save()

                # Redirect to the new listing
                return HttpResponseRedirect(reverse("listing", args=(listing.id,))) 
            except Exception as e:
                print(e)
                return render(request, "auctions/error.html", {
                    "title": "Error has occured",
                    "message": e
                })
        
        # If form is invalid
        return render(request, "auctions/new.html", {
            "form":form,
        })

    # If request is GET
    return render(request, "auctions/new.html", {
        "form": NewListingForm()
    })

@login_required
def close(request, id):
    # Get the listing
    listing = Listing.objects.get(id=id)

    # Check the user is the owner
    if listing.owner == request.user:

        # Deactive the listing and record the winner
        listing.active = False
        listing.winner = listing.bids.first().user
        listing.save()

        # Show the page
        return HttpResponseRedirect(reverse("listing", args=(id,))) 

@login_required
def bid(request, id):
    if request.method == "POST":

        # Get the listing
        listing = Listing.objects.get(id=id)

        # Check if listing is active
        if not listing.active:
            return render(request, "auctions/error.html", {
                "title": "Error: Invalid action",
                "message": "Cannot bid on an inactive auction"
            })

        # Get the bid price
        price = int(request.POST["amount"])

        # Check if the bid price is higher than the current bid, otherwise throw error
        if (price > listing.current_price()):
            b = Bid.objects.create(user=request.user, listing=listing, price=price)
            b.save()
            return HttpResponseRedirect(reverse("listing", args=(id,))) 
        else:
            return render(request, "auctions/error.html", {
                "title": "Error: Invalid action",
                "message": "New bid must be higher than current bid"
            })
    return HttpResponseRedirect(reverse("listing", args=(id,))) 

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories":Listing.CATEGORIES
    })

def category(request, category):

    try:
        #Get the proper category label
        category = [c for c in Listing.CATEGORIES if c[0]==category]
        print(category[0][1])

        return render(request, "auctions/index.html", {
            "listings":Listing.objects.all().filter(category=category[0][0]),
            "title": category[0][1]
        })
    except:
        return render(request, "auctions/error.html", {
                "title": "Error 404: Page not found",
                "message": f"Cannot find category {category}"
            })

@login_required
def comment(request, id):
    if request.method == "POST":

        # Get the listing
        listing = Listing.objects.get(id=id)

        # Get the comments
        comment = request.POST["comment"]

        c = Comment.objects.create(user=request.user, comment=comment, listing=listing)
        c.save()

    return HttpResponseRedirect(reverse("listing", args=(id,))) 

class NewListingForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description", widget=forms.Textarea)
    image = forms.CharField(label="Image URL", required=False)
    start_price = forms.IntegerField(label="Starting Price")
    category = forms.ChoiceField(label="Category", choices = Listing.CATEGORIES)

    
