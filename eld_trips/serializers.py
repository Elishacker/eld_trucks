from rest_framework import serializers # type: ignore
from .models import Trip

class TripSerializer(serializers.ModelSerializer):
    # Optional stops/rests during creation or update
    stops = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True
    )
    rests = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Trip
        fields = "__all__"
        read_only_fields = ("route_info", "daily_logs", "map_data", "created_at")

    def create(self, validated_data):
        stops_list = validated_data.pop("stops", [])
        rests_list = validated_data.pop("rests", [])

        # Create the Trip instance
        trip = super().create(validated_data)

        # Generate route/map points for MapView
        trip.generate_route(stops=stops_list, rests=rests_list)

        # Optionally generate mock daily logs
        trip.generate_daily_logs()

        return trip

    def update(self, instance, validated_data):
        stops_list = validated_data.pop("stops", None)
        rests_list = validated_data.pop("rests", None)

        # Update basic fields
        trip = super().update(instance, validated_data)

        # Update route/map points if stops or rests are provided
        if stops_list is not None or rests_list is not None:
            trip.generate_route(
                stops=stops_list or [],
                rests=rests_list or []
            )

        return trip
