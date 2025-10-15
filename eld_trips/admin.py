from django.contrib import admin # type: ignore
from .models import Trip

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('pickup_location', 'dropoff_location', 'current_location', 'start_time', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('pickup_location', 'dropoff_location', 'current_location')
