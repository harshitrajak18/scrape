from django.urls import path
from .views import scrape_site

urlpatterns = [
    path('scrape/', scrape_site, name='scrape'),  # Register scrape endpoint
]