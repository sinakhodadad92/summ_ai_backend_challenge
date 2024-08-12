from .views import documentation_view
from django.urls import path

# URL patterns define the routing for the landing page.
urlpatterns = [
    path('', documentation_view, name='documentation'),
]