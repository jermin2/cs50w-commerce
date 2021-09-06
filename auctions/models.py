from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="watchlists")

    def get_active_listings(self):
        return self.listings.all().filter(active=True)

    def get_closed_listings(self):
        return self.listings.all().filter(active=False)
    pass
    
class Listing(models.Model):
    # Todo
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255)
    start_price = models.IntegerField(default=0)
    image = models.CharField(max_length=255)
    category = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="won")
    CATEGORIES = [
        ('arts', 'Arts'),
        ('electronics', 'Electronics'),
        ('farming', 'Farming'),
        ('fashion', 'Fashion'),
        ('home', 'Home'),
        ('sports', 'Sports'),
        ('toys', 'Toys'),
        ]
    category = models.CharField(max_length=64, choices=CATEGORIES)
    

    def __str__(self):
        return f"{self.current_price()} : {self.name} - {self.description}"

    # Return the current highest price
    def current_price(self):
        if (self.bids.first() != None):
            return self.bids.first().price
        return self.start_price


class Bid(models.Model):
    price = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.price} : {self.user}"

    class Meta:
        ordering = ['-price']

class Comment(models.Model):
    comment = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} says: {self.comment}"



