from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError

from rooms.models import Room
from bookings.models import Booking
from .forms import BookingForm
from . import services

