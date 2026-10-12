from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.core.cache import cache
from django.urls import reverse

from bookings.models import Booking
from hotels.models import Hotel
from rooms.models import Room
from reviews.models import Review
from reviews.services import create_review, get_hotel_avg_rating


User = get_user_model()


class ReviewServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='review_guest',
            password='test-password-123',
        )
        self.hotel = Hotel.objects.create(
            name='Тестовый отель',
            city='Алматы',
            address='Тестовый адрес',
            price_night=Decimal('15000.00'),
        )
        self.room = Room.objects.create(
            hotel=self.hotel,
            number='101',
            room_type='double',
            price_night=Decimal('15000.00'),
            capacity=2,
            is_available=True,
        )

    def create_booking(self, *, status, check_out):
        return Booking.objects.create(
            user=self.user,
            room=self.room,
            check_in=check_out - timedelta(days=2),
            check_out=check_out,
            guests=1,
            status=status,
        )

    def test_guest_without_completed_booking_cannot_review(self):
        with self.assertRaises(ValidationError):
            create_review(
                user=self.user,
                hotel=self.hotel,
                rating=5,
                text='Отличный отель!',
            )

        self.assertFalse(
            Review.objects.filter(
                user=self.user,
                hotel=self.hotel,
            ).exists()
        )

    def test_confirmed_completed_booking_allows_review(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        self.create_booking(status='confirmed', check_out=yesterday)

        review = create_review(
            user=self.user,
            hotel=self.hotel,
            rating=5,
            text='Отличный отель!',
        )

        self.assertEqual(review.user, self.user)
        self.assertEqual(review.hotel, self.hotel)
        self.assertEqual(review.rating, 5)
        self.assertFalse(review.is_approved)

    def test_pending_booking_does_not_allow_review(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        self.create_booking(status='pending', check_out=yesterday)

        with self.assertRaises(ValidationError):
            create_review(
                user=self.user,
                hotel=self.hotel,
                rating=4,
                text='Хороший отель.',
            )

    def test_cancelled_booking_does_not_allow_review(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        self.create_booking(status='cancelled', check_out=yesterday)

        with self.assertRaises(ValidationError):
            create_review(
                user=self.user,
                hotel=self.hotel,
                rating=4,
                text='Хороший отель.',
            )

    def test_booking_with_checkout_today_does_not_allow_review(self):
        self.create_booking(
            status='confirmed',
            check_out=timezone.localdate(),
        )

        with self.assertRaises(ValidationError):
            create_review(
                user=self.user,
                hotel=self.hotel,
                rating=4,
                text='Хороший отель.',
            )

    def test_repeated_review_updates_existing_record(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        self.create_booking(status='confirmed', check_out=yesterday)

        first_review = create_review(
            user=self.user,
            hotel=self.hotel,
            rating=3,
            text='Всё неплохо.',
        )

        second_review = create_review(
            user=self.user,
            hotel=self.hotel,
            rating=5,
            text='После уточнения впечатления отличные!',
        )

        self.assertEqual(first_review.pk, second_review.pk)
        self.assertEqual(
            Review.objects.filter(
                user=self.user,
                hotel=self.hotel,
            ).count(),
            1,
        )
        self.assertEqual(second_review.rating, 5)
        self.assertEqual(
            second_review.text,
            'После уточнения впечатления отличные!',
        )


class ReviewAverageRatingTests(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(
            name='Отель для проверки рейтинга',
            city='Алматы',
            address='Тестовый адрес',
            price_night=Decimal('15000.00'),
            rating=4.8,
        )

        self.user1 = User.objects.create_user(username='rating_user1')
        self.user2 = User.objects.create_user(username='rating_user2')

        Review.objects.create(
            hotel=self.hotel,
            user=self.user1,
            rating=5,
            text='Отлично!',
            is_approved=True,
        )
        Review.objects.create(
            hotel=self.hotel,
            user=self.user2,
            rating=1,
            text='Не одобренный отзыв',
            is_approved=False,
        )

    def test_average_rating_uses_approved_reviews_only(self):
        hotel = Hotel.objects.with_stats().get(pk=self.hotel.pk)

        self.assertEqual(hotel.avg_rating, 5.0)


class ReviewRatingCacheTests(TestCase):
    def setUp(self):
        cache.clear()

        self.hotel = Hotel.objects.create(
            name='Кешируемый отель',
            city='Алматы',
            address='Тестовый адрес',
            price_night=Decimal('12000.00'),
        )
        self.user = User.objects.create_user(username='cache_user')

    def test_average_rating_is_cached(self):
        Review.objects.create(
            hotel=self.hotel,
            user=self.user,
            rating=4,
            text='Хорошо',
            is_approved=True,
        )

        self.assertEqual(get_hotel_avg_rating(self.hotel.pk), 4.0)

        # После одобрения нового отзыва старый кеш должен сброситься.
        another_user = User.objects.create_user(username='cache_user2')
        review = Review.objects.create(
            hotel=self.hotel,
            user=another_user,
            rating=2,
            text='Нормально',
            is_approved=False,
        )

        self.assertEqual(get_hotel_avg_rating(self.hotel.pk), 4.0)

        review.is_approved = True
        review.save(update_fields=['is_approved'])

        self.assertEqual(get_hotel_avg_rating(self.hotel.pk), 3.0)

    def test_deleting_review_invalidates_cache(self):
        review = Review.objects.create(
            hotel=self.hotel,
            user=self.user,
            rating=4,
            text='Хорошо',
            is_approved=True,
        )

        self.assertEqual(get_hotel_avg_rating(self.hotel.pk), 4.0)

        review.delete()

        self.assertIsNone(get_hotel_avg_rating(self.hotel.pk))



class ReviewViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='view_guest',
            password='test-password-123',
        )
        self.other_user = User.objects.create_user(
            username='other_view_guest',
            password='test-password-123',
        )
        self.hotel = Hotel.objects.create(
            name='Отель для тестирования представлений',
            city='Алматы',
            address='Тестовый адрес',
            price_night=Decimal('15000.00'),
        )
        self.room = Room.objects.create(
            hotel=self.hotel,
            number='201',
            room_type='double',
            price_night=Decimal('15000.00'),
            capacity=2,
            is_available=True,
        )

        self.submit_url = reverse(
            'reviews:submit_review',
            kwargs={'hotel_id': self.hotel.pk},
        )
        self.detail_url = reverse(
            'hotels:hotel_detail',
            kwargs={'pk': self.hotel.pk},
        )

    def create_completed_booking(self, user=None):
        user = user or self.user
        yesterday = timezone.localdate() - timedelta(days=1)

        return Booking.objects.create(
            user=user,
            room=self.room,
            check_in=yesterday - timedelta(days=2),
            check_out=yesterday,
            guests=1,
            status='confirmed',
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.submit_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)
        self.assertIn('next=', response.url)

    def test_user_without_completed_booking_cannot_submit_review(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.submit_url,
            {
                'rating': '5',
                'text': 'Отличный отель, всё понравилось!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Review.objects.filter(
                hotel=self.hotel,
                user=self.user,
            ).exists()
        )

    def test_completed_guest_can_submit_unapproved_review(self):
        self.create_completed_booking()
        self.client.force_login(self.user)

        response = self.client.post(
            self.submit_url,
            {
                'rating': '5',
                'text': 'Отличный отель, всё понравилось!',
            },
        )

        self.assertRedirects(response, self.detail_url)

        review = Review.objects.get(
            hotel=self.hotel,
            user=self.user,
        )
        self.assertEqual(review.rating, 5)
        self.assertFalse(review.is_approved)

    def test_repeated_submission_updates_existing_review(self):
        self.create_completed_booking()
        self.client.force_login(self.user)

        first_response = self.client.post(
            self.submit_url,
            {
                'rating': '3',
                'text': 'В целом проживание нормальное.',
            },
        )
        self.assertRedirects(first_response, self.detail_url)

        review = Review.objects.get(
            hotel=self.hotel,
            user=self.user,
        )
        review.is_approved = True
        review.save(update_fields=['is_approved'])
        review_id = review.pk

        second_response = self.client.post(
            self.submit_url,
            {
                'rating': '5',
                'text': 'После уточнения впечатления отличные!',
            },
        )

        self.assertRedirects(second_response, self.detail_url)

        review.refresh_from_db()
        self.assertEqual(review.pk, review_id)
        self.assertEqual(review.rating, 5)
        self.assertEqual(
            review.text,
            'После уточнения впечатления отличные!',
        )
        self.assertFalse(review.is_approved)
        self.assertEqual(
            Review.objects.filter(
                hotel=self.hotel,
                user=self.user,
            ).count(),
            1,
        )

    def test_existing_review_is_loaded_into_form(self):
        self.create_completed_booking()

        review = Review.objects.create(
            hotel=self.hotel,
            user=self.user,
            rating=4,
            text='Очень приятное проживание.',
        )
        self.client.force_login(self.user)

        response = self.client.get(self.submit_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].instance.pk, review.pk)
        self.assertEqual(response.context['form']['rating'].value(), 4)
        self.assertEqual(
            response.context['form']['text'].value(),
            'Очень приятное проживание.',
        )

    def test_user_cannot_delete_another_users_review(self):
        review = Review.objects.create(
            hotel=self.hotel,
            user=self.other_user,
            rating=4,
            text='Хорошее проживание.',
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'reviews:delete_review',
                kwargs={'review_id': review.pk},
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())

    def test_user_can_delete_own_review_with_post(self):
        review = Review.objects.create(
            hotel=self.hotel,
            user=self.user,
            rating=4,
            text='Хорошее проживание.',
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'reviews:delete_review',
                kwargs={'review_id': review.pk},
            )
        )

        self.assertRedirects(response, self.detail_url)
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())

    def test_delete_review_does_not_accept_get(self):
        review = Review.objects.create(
            hotel=self.hotel,
            user=self.user,
            rating=4,
            text='Хорошее проживание.',
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                'reviews:delete_review',
                kwargs={'review_id': review.pk},
            )
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())

