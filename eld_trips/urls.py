from django.urls import path # type: ignore
from .views import TripListCreateView

urlpatterns = [
    path('', TripListCreateView.as_view(), name='trip-list-create'),
]
