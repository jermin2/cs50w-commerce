from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category, name="category"),

    path("listing/<int:id>/bid", views.bid, name="bid"),
    path("listing/<int:id>/comment", views.comment, name="comment"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("listing/new", views.new, name="new"),
    path("listing/<int:id>/close", views.close, name="close"),

    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:id>/listings", views.listings, name="listings"),

    path("watchlist/add/<int:id>", views.watchlist_add, name="watchlist_add"),
    path("watchlist/remove/<int:id>", views.watchlist_remove, name="watchlist_remove"),
    path("watchlist", views.watchlist, name="watchlist")
]
