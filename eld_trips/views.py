from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from .models import Trip
from .serializers import TripSerializer

class TripListCreateView(APIView):
    """
    GET: List all trips (most recent first)
    POST: Create a new trip
    """

    def get(self, request):
        trips = Trip.objects.all().order_by("-created_at")
        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TripSerializer(data=request.data)
        if serializer.is_valid():
            trip = serializer.save()
            # Optionally generate mock daily logs (for ELD)
            trip.generate_daily_logs(total_days=1)
            return Response(TripSerializer(trip).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TripRetrieveView(APIView):
    """
    GET: Retrieve a single trip by ID (for MapView)
    """

    def get(self, request, pk):
        try:
            trip = Trip.objects.get(pk=pk)
        except Trip.DoesNotExist:
            return Response({"detail": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TripSerializer(trip)
        return Response(serializer.data, status=status.HTTP_200_OK)
