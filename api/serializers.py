from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError

from django.core.exceptions import ValidationError as DjangoValidationError

from hotels.models import Hotel
from rooms.models import Room
from bookings.models import Booking
from bookings import services



class HotelListSerializer(serializers.ModelSerializer):
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, allow_null=True)
    rooms_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'city', 'address', 'rating', 'min_price', 'rooms_count']


class RoomListSerializer(serializers.ModelSerializer):
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'hotel', 'hotel_name', 'number', 'room_type', 'description', 'price_night', 'capacity',]


class BookingListSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.number', read_only=True)
    hotel_name = serializers.CharField(source='room.hotel.name', read_only=True)
    nights = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True,)

    class Meta:
        model = Booking
        fields = ['id', 'room', 'room_number', 'hotel_name', 'check_in', 'check_out', 'guests', 'status', 'nights',
                  'total_price', 'created_at']
        read_only_fields = ['id', 'status', 'created_at', 'nights', 'total_price']


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['room', 'check_in', 'check_out', 'guests']   

    def create(self, validated_data):
        user = self.context['request'].user
        room = validated_data.pop('room')
        check_in = validated_data['check_in']
        check_out = validated_data['check_out']
        guests = validated_data.get('guests', 1)    

        try:
            return services.create_booking(
                user=user,
                room=room,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
            )
        except DjangoValidationError as exc:
            raise DRFValidationError({
                'booking': exc.messages,
            }) from exc
