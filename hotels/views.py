import csv
import io

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

from . models import Hotel
from . forms import HotelImportForm


class HotelListView(ListView):

    model = Hotel
    template_name = 'hotels/list.html'
    context_object_name = 'hotels'
    paginate_by = 6

    SORTS = {
        'price': 'min_price',
        '-price': '-min_price',
        'rating': '-rating'
    }

    def get_queryset(self):
        hotels = Hotel.objects.active().with_stats()
        city = self.request.GET.get('city', '')
        if city:
            hotels = hotels.annotate(city_lower=Lower('city')).filter(city_lower__contains=city.lower())
        sort_by = self.request.GET.get('sort', '')
        return hotels.order_by(self.SORTS.get(sort_by, '-rating'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['city'] = self.request.GET.get('city', '')
        context['sort'] = self.request.GET.get('sort', '')
        return context        


def hotel_detail(request, pk):
    hotel = get_object_or_404(Hotel.objects.with_stats(), pk=pk, is_active=True)
    rooms = hotel.rooms.on_sale().with_today_status()
    return render(request, 'hotels/hotel_detail.html', {
        'hotel': hotel,
        'rooms': rooms
    })


# Обязательные колонки в файле импорта, в этом порядке.
IMPORT_COLUMNS = ['name', 'city', 'address', 'price', 'rating']


def _rows_from_csv(uploaded_file):
    """Строки из CSV как список словарей {колонка: значение}."""
    decoded = io.TextIOWrapper(uploaded_file.file, encoding='utf-8-sig')
    return list(csv.DictReader(decoded))


def _rows_from_xlsx(uploaded_file):    
    from openpyxl import load_workbook

    workbook = load_workbook(uploaded_file, read_only=True, data_only=True)
    sheet = workbook.active
    rows_iter = sheet.iter_rows(values_only=True)

    header = [str(cell).strip() if cell is not None else '' for cell in next(rows_iter)]
    rows = []
    for values in rows_iter:
        if all(v is None for v in values):  # пропускаем полностью пустые строки
            continue
        row = dict(zip(header, values))
        rows.append({k: ('' if v is None else str(v)) for k, v in row.items()})
    return rows


@permission_required('hotels.add_hotel', raise_exception=True)
def import_hotels(request):
    if request.method == 'POST':
        form = HotelImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['import_file']
            if uploaded_file.name.lower().endswith('.xlsx'):
                rows = _rows_from_xlsx(uploaded_file)
            else:
                rows = _rows_from_csv(uploaded_file)

            created_rows = []
            errors = []
            try:
                with transaction.atomic():
                    for line_number, row in enumerate(rows, start=2):  # строка 1 — заголовок
                        missing = [c for c in IMPORT_COLUMNS if not row.get(c)]
                        if missing:
                            errors.append(f'Строка {line_number}: не хватает полей {", ".join(missing)}')
                            continue
                        try:
                            hotel = Hotel(
                                name=row['name'].strip(),
                                city=row['city'].strip(),
                                address=row['address'].strip(),
                                price_night=row['price'],
                                rating=row['rating'],
                            )
                            hotel.full_clean()  # прогоняет те же валидаторы, что и форма/админка
                        except Exception as exc:
                            errors.append(f'Строка {line_number}: {exc}')
                            continue
                        hotel.save()
                        created_rows.append(hotel.name)

                    if errors:
                        # Откатываем всю транзакцию — либо всё, либо ничего.
                        raise ValueError('import aborted: validation errors')
            except ValueError:
                for err in errors:
                    messages.error(request, err)
                messages.error(request, 'Импорт отменён: ни один отель не создан из-за ошибок выше.')
            else:
                messages.success(request, f'Импортировано отелей: {len(created_rows)}.')
                return redirect('hotels:hotel_list')
    else:
        form = HotelImportForm()

    return render(request, 'hotels/import.html', {'form': form})


    

# === Старая дедакция - отменено ===============================================================
# def hotel_list(request):
#     city = request.GET.get('city', '')
#     hotels = Hotel.objects.filter(is_active=True)

#     # Фильтрация по городу

#     # if city:
#     #     hotels = [h for h in hotels if city.lower() in h.city.lower()]
    
#     if city:
#         hotels = hotels.filter(city__icontains=city)

#     return render(request, 'hotels/list.html', {
#         'hotels': hotels,   # список найденных отелей
#         'city': city        # текст поиска для отображения в форме
#         })


# # Функция отображения информации об одном отеле
# def hotel_detail(request, pk):
#     # Ищем отель по id
#     hotel = get_object_or_404(
#             Hotel,
#             pk=pk,
#             is_active=True
#         )
#     # получаем свободные номера выбранного отеля
#     rooms = hotel.rooms.filter(is_available=True)
#     return render(request, 'hotels/hotel_detail.html', {
#         'hotel': hotel, 'rooms': rooms
#         })
    

