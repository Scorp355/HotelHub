from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from hotels.models import Hotel

from .forms import ReviewForm
from .models import Review
from .services import create_review


@login_required

@login_required
def submit_review(request, hotel_id):
    hotel = get_object_or_404(Hotel, pk=hotel_id, is_active=True)

    existing_review = Review.objects.filter(
        hotel=hotel,
        user=request.user,
    ).first()

    if request.method == 'POST':
        form = ReviewForm(
            request.POST,
            instance=existing_review,
        )

        if form.is_valid():
            try:
                create_review(user=request.user, hotel=hotel, rating=int(form.cleaned_data['rating']),
                              text=form.cleaned_data['text'])
            except ValidationError as exc:
                form.add_error(None, exc.messages)
            else:
                messages.success(request, 'Отзыв отправлен на модерацию.')
                return redirect(reverse('hotels:hotel_detail', kwargs={'pk': hotel.pk})
                )
    else:
        form = ReviewForm(instance=existing_review)

    return render(request, 'reviews/review_form.html', {
            'hotel': hotel,
            'form': form,
        },
    )




@login_required
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(
        Review,
        pk=review_id,
        user=request.user,
    )
    hotel_id = review.hotel_id
    review.delete()

    messages.success(request, 'Ваш отзыв удалён.')

    return redirect(
        reverse(
            'hotels:hotel_detail',
            kwargs={'pk': hotel_id},
        )
    )

