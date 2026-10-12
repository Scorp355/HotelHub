from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from hotels.models import Hotel
from rooms.models import Room
from bookings.models import Booking
from rest_framework.test import APIClient


class HotelListAPITests(TestCase):
    """Автотесты GET /api/hotels/."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api:hotel-list')

        self.hotel = Hotel.objects.create(
            name='Grand Astana',
            city='Астана',
            address='ул. Тест, 1',
            price_night=45000,
            rating=4.7,
            is_active=True,
        )

        self.empty_hotel = Hotel.objects.create(
            name='Empty Hotel',
            city='Алматы',
            address='ул. Тест, 2',
            price_night=30000,
            rating=4.0,
            is_active=True,
        )

        self.inactive_hotel = Hotel.objects.create(
            name='Old Hotel',
            city='Астана',
            address='ул. Тест, 3',
            price_night=10000,
            is_active=False,
        )

        Room.objects.create(
            hotel=self.hotel,
            number='101',
            room_type='single',
            price_night=20000,
        )
        Room.objects.create(
            hotel=self.hotel,
            number='102',
            room_type='double',
            price_night=15000,
        )

    def test_list_returns_200(self):
        """Список отелей доступен без авторизации."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_list_contains_only_active_hotels(self):
        """Неактивные отели не попадают в API."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        names = [
            hotel['name']
            for hotel in response.data['results']
        ]

        self.assertIn('Grand Astana', names)
        self.assertIn('Empty Hotel', names)
        self.assertNotIn('Old Hotel', names)

    def test_min_price_is_calculated_from_rooms(self):
        """Минимальная цена рассчитывается по стоимости номеров."""
        response = self.client.get(self.url)

        hotel_data = next(
            item
            for item in response.data['results']
            if item['id'] == self.hotel.pk
        )

        self.assertEqual(str(hotel_data['min_price']), '15000.00')

    def test_rooms_count_is_correct(self):
        """Количество номеров соответствует данным в базе."""
        response = self.client.get(self.url)

        hotel_data = next(
            item
            for item in response.data['results']
            if item['id'] == self.hotel.pk
        )

        self.assertEqual(hotel_data['rooms_count'], 2)

    def test_hotel_without_rooms_has_null_min_price(self):
        """У отеля без номеров min_price равен null, rooms_count равен 0."""
        response = self.client.get(self.url)

        hotel_data = next(
            item
            for item in response.data['results']
            if item['id'] == self.empty_hotel.pk
        )

        self.assertIsNone(hotel_data['min_price'])
        self.assertEqual(hotel_data['rooms_count'], 0)

    def test_response_has_pagination_fields(self):
        """Ответ содержит стандартную структуру пагинации DRF."""
        response = self.client.get(self.url)

        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

    def test_second_page_returns_remaining_hotels(self):
        """Вторая страница содержит оставшиеся записи."""
        # Уже есть два активных отеля. Добавляем ещё девять:
        # всего 11 активных отелей при PAGE_SIZE = 10.
        for i in range(9):
            Hotel.objects.create(
                name=f'Extra Hotel {i}',
                city='Астана',
                address=f'ул. Тест, {i + 10}',
                price_night=12000,
                is_active=True,
            )

        first_page = self.client.get(self.url)

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(first_page.data['count'], 11)
        self.assertEqual(len(first_page.data['results']), 10)
        self.assertIsNotNone(first_page.data['next'])

        second_page = self.client.get(self.url, {'page': 2})

        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(len(second_page.data['results']), 1)
        self.assertIsNone(second_page.data['next'])
        self.assertIsNotNone(second_page.data['previous'])


class RoomListAPITests(TestCase):
    """Автотесты GET /api/rooms/."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api:room-list')

        self.today = date.today()
        self.check_in = self.today + timedelta(days=10)
        self.check_out = self.today + timedelta(days=13)

        self.hotel = Hotel.objects.create(
            name='API Test Hotel',
            city='Астана',
            address='ул. Тест, 10',
            price_night=30000,
            rating=4.5,
            is_active=True,
        )

        self.free_room = Room.objects.create(
            hotel=self.hotel,
            number='201',
            room_type='double',
            price_night=20000,
            capacity=2,
            is_available=True,
        )

        self.booked_room = Room.objects.create(
            hotel=self.hotel,
            number='202',
            room_type='single',
            price_night=15000,
            capacity=1,
            is_available=True,
        )

        self.unavailable_room = Room.objects.create(
            hotel=self.hotel,
            number='203',
            room_type='single',
            price_night=10000,
            capacity=1,
            is_available=False,
        )

        self.user = get_user_model().objects.create_user(
            username='api_test_user',
            password='test-password-123',
        )

        Booking.objects.create(
            user=self.user,
            room=self.booked_room,
            check_in=self.check_in,
            check_out=self.check_out,
            guests=1,
            status='confirmed',
        )

    def get_rooms(self, check_in=None, check_out=None):
        params = {}
        if check_in is not None:
            params['check_in'] = check_in
        if check_out is not None:
            params['check_out'] = check_out
        return self.client.get(self.url, params)

    def test_list_returns_only_available_rooms(self):
        response = self.get_rooms(
            self.check_in.isoformat(),
            self.check_out.isoformat(),
        )

        self.assertEqual(response.status_code, 200)
        room_ids = [room['id'] for room in response.data['results']]

        self.assertIn(self.free_room.pk, room_ids)
        self.assertNotIn(self.booked_room.pk, room_ids)
        self.assertNotIn(self.unavailable_room.pk, room_ids)

    def test_adjacent_booking_dates_do_not_overlap(self):
        response = self.get_rooms(
            self.check_out.isoformat(),
            (self.check_out + timedelta(days=2)).isoformat(),
        )

        self.assertEqual(response.status_code, 200)
        room_ids = [room['id'] for room in response.data['results']]

        self.assertIn(self.booked_room.pk, room_ids)

    def test_missing_dates_returns_400(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 400)

    def test_invalid_date_format_returns_400(self):
        response = self.get_rooms('11-01-2026', '11-05-2026')

        self.assertEqual(response.status_code, 400)

    def test_checkout_before_or_equal_checkin_returns_400(self):
        response = self.get_rooms(
            self.check_in.isoformat(),
            self.check_in.isoformat(),
        )

        self.assertEqual(response.status_code, 400)

    def test_past_checkin_returns_400(self):
        yesterday = self.today - timedelta(days=1)
        tomorrow = self.today + timedelta(days=1)

        response = self.get_rooms(
            yesterday.isoformat(),
            tomorrow.isoformat(),
        )

        self.assertEqual(response.status_code, 400)


class BookingAPITests(TestCase):
    """Автотесты GET и POST /api/bookings/."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api:booking-list')

        self.today = date.today()
        self.check_in = self.today + timedelta(days=10)
        self.check_out = self.today + timedelta(days=13)

        self.user = get_user_model().objects.create_user(
            username='booking_api_user',
            password='test-password-123',
        )
        self.other_user = get_user_model().objects.create_user(
            username='other_booking_user',
            password='test-password-123',
        )

        self.hotel = Hotel.objects.create(
            name='Booking API Hotel',
            city='Астана',
            address='ул. Тест, 20',
            price_night=30000,
            rating=4.5,
            is_active=True,
        )

        self.room = Room.objects.create(
            hotel=self.hotel,
            number='301',
            room_type='double',
            price_night=20000,
            capacity=2,
            is_available=True,
        )

        self.payload = {
            'room': self.room.pk,
            'check_in': self.check_in.isoformat(),
            'check_out': self.check_out.isoformat(),
            'guests': 2,
        }

    def test_anonymous_user_cannot_create_booking(self):
        response = self.client.post(
            self.url,
            self.payload,
            format='json',
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Booking.objects.count(), 0)

    def test_authenticated_user_can_create_booking(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            self.payload,
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Booking.objects.count(), 1)

        booking = Booking.objects.get()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.room, self.room)
        self.assertEqual(booking.guests, 2)
        self.assertEqual(booking.status, 'pending')

    def test_overlapping_booking_returns_400(self):
        Booking.objects.create(
            user=self.other_user,
            room=self.room,
            check_in=self.check_in,
            check_out=self.check_out,
            guests=1,
            status='confirmed',
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            self.payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Booking.objects.count(), 1)

    def test_user_sees_only_own_bookings(self):
        own_booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            check_in=self.check_in,
            check_out=self.check_out,
            guests=1,
            status='pending',
        )

        other_booking = Booking.objects.create(
            user=self.other_user,
            room=self.room,
            check_in=self.check_out,
            check_out=self.check_out + timedelta(days=2),
            guests=1,
            status='pending',
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        returned_ids = [
            item['id'] for item in response.data['results']
        ]

        self.assertIn(own_booking.pk, returned_ids)
        self.assertNotIn(other_booking.pk, returned_ids)

    def test_anonymous_user_cannot_list_bookings(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)