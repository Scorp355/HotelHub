# Скрипт-наполнитель
from hotels.models import Hotel
from rooms.models import Room


# Отели
grand = Hotel(name='Гранд Алтай', city='Усть-Каменогорск', rating=4)
grand.save()

irtysh = Hotel(name='Иртыш', city='Усть-Каменогорск', rating=5)
irtysh.save()

# Номера
r1 = Room(hotel=grand, nuber='101', room_type='single', price_night=35000, capacity=1, description='Уютный одноместный номер с видом на двор')
r1.save()

r2 = Room(hotel=grand, nuber='205', room_type='double', price_night=25000, capacity=2, description='Уютный двухместный номер с балконом и ' \
'панорамным окном')
r2.save()

r3 = Room(hotel=irtysh, nuber='103', room_type='family', price_night=32000, capacity=4, description='Семейный номер с двумя спальнями у набережной')
r3.save()

print(f'Готово: {Hotel.objects.count()} отелей, {Room.objects.count()} номеров')
