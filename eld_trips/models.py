from django.db import models # type: ignore
from django.utils import timezone # type: ignore
import requests

class Trip(models.Model):
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    current_cycle_hours = models.FloatField(default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Stores route info: coordinates, stops, rests, distance, duration
    route_info = models.JSONField(default=dict, blank=True)

    # Stores daily ELD logs
    daily_logs = models.JSONField(default=list, blank=True)

    # Stores map points for frontend markers
    map_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Trip from {self.pickup_location} to {self.dropoff_location}"

    def geocode_location(self, name):
        """
        Converts a location name into (lat, lng) coordinates using OpenStreetMap Nominatim API.
        """
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": name, "format": "json", "limit": 1}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            print(f"Geocoding error for '{name}': {e}")
        return None

    def generate_route(self, stops=None, rests=None):
        """
        Generate route coordinates and map points for the trip.
        Optional: stops and rests as lists of location names.
        """
        stops = stops or []
        rests = rests or []

        # Geocode main points
        pickup_coord = self.geocode_location(self.pickup_location)
        dropoff_coord = self.geocode_location(self.dropoff_location)

        # Geocode stops and rests
        stops_coords = [self.geocode_location(s) for s in stops if self.geocode_location(s)]
        rests_coords = [self.geocode_location(r) for r in rests if self.geocode_location(r)]

        # Save marker data for frontend
        self.map_data = {
            "pickup": pickup_coord,
            "dropoff": dropoff_coord,
            "stops": stops_coords,
            "rests": rests_coords,
        }

        # Build coordinates for polyline route
        route_coordinates = [pickup_coord] + stops_coords + rests_coords + [dropoff_coord]
        route_coordinates = [coord for coord in route_coordinates if coord]  # remove None

        # Populate route_info
        self.route_info = {
            "coordinates": [{"lat": lat, "lng": lng} for lat, lng in route_coordinates],
            "stops": [{"type": "Stop", "miles_from_start": 0, "duration_hours": 1} for _ in stops_coords],
            "rests": [{"type": "Rest", "miles_from_start": 0, "duration_hours": 1} for _ in rests_coords],
            "distance_miles": 0,
            "duration_hours": 0,
        }

        self.save()

    def generate_daily_logs(self, start_hour=8, total_days=1):
        """
        Generate mock ELD daily logs for the trip.
        """
        self.daily_logs = []

        for day in range(total_days):
            segments = [
                {"type": "Driving", "duration_hours": 5, "start": f"{start_hour}:00"},
                {"type": "On Duty (Not Driving)", "duration_hours": 1, "start": f"{start_hour + 5}:00"},
                {"type": "Off Duty", "duration_hours": 18, "start": f"{start_hour + 6}:00"},
            ]
            totals = {
                "driving": sum(s["duration_hours"] for s in segments if s["type"] == "Driving"),
                "on_duty": sum(s["duration_hours"] for s in segments if s["type"] == "On Duty (Not Driving)"),
                "off_duty": sum(s["duration_hours"] for s in segments if s["type"] == "Off Duty"),
            }

            self.daily_logs.append({
                "date": (timezone.now() + timezone.timedelta(days=day)).strftime("%Y-%m-%d"),
                "segments": segments,
                "totals": totals
            })

        self.save()
