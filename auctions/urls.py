from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("<int:listing_id>", views.listing_page, name="listing_page"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/<int:listing_id>", views.watchlist_move, name="watchlist_move"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("auctions_won", views.auctions_won, name="auctions_won"),
    path("categories", views.categories, name="categories"),
    path("category_page/<int:cat_id>", views.category_page, name="category_page" ),
    path("comment/<int:listing_id>", views.comment, name="comment")
]
