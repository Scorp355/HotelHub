from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# 1. Модель спецпредложений (промоакции)
class PromoOffer(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название акции')     # Заголовок акции
    description = models.TextField(verbose_name='Описание')     # Описание
    discount_percent = models.PositiveIntegerField(null=True, blank=True, verbose_name='Скидка %')      # Размер скидки в процентах    
    valid_until = models.DateField(null=True, blank=True, verbose_name='Действует до')       # Срок действия - до какой даты
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Спецпредложение'            # в единственном числе
        verbose_name_plural = 'Спецпреложения'      # в множественном числе
        ordering = ['-created_at']                  # сортировка по дате создания записи - обратная

    def __str__(self):
        return self.title


# 2. Инфраструктура отеля. Хранит информацию об услугах и объектах отеля (SPA, бассейн и т.д.)
class Facility(models.Model):
    name = models.CharField(max_length=100, verbose_name='Услуга')
    short_desc = models.CharField(max_length=255, verbose_name='Краткое описание')    
    icon_class = models.CharField(max_length=50, help_text='Класс иконки, например: fa-spa')        # Иконка услуги

    class Meta:
        verbose_name = 'Услуга отеля'            # в единственном числе
        verbose_name_plural = 'Инфраструктура'      # в множественном числе

    def __str__(self):
        return self.name


# 3. Отзывы гостей.
class Review(models.Model):    
    author = models.CharField(max_length=100, verbose_name='Имя гостя')     # Имя гостя, который оставил отзыв
    text = models.TextField(verbose_name='Текст отзыва')
    # Рейтинг отеля по шкале от 1 до 5
    ratting = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)],
                                          default=5, verbose_name='Оценка')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'            # в единственном числе
        verbose_name_plural = 'Отзывы'      # в множественном числе


    def __str__(self):
        return f'{self.author} - {self.ratting}'


# 4. Модель - Часто задаваемые вопросы (FAQ)
class FAQItem(models.Model):
    question = models.CharField(max_length=255, verbose_name='Вопрос')      # Вопрос гостя
    answer = models.TextField(verbose_name='Ответ')     # Ответ на вопрос
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок вывода')        # Нумерация вопросов (индексы)

    class Meta:
        verbose_name = 'Вопрос FAQ'            # в единственном числе
        verbose_name_plural = 'FAQ'            # в множественном числе
        ordering = ['order']

    def __str__(self):
        return self.question


# 5. Сообщение из Формы обратной связи
class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    subject = models.CharField(max_length=150, verbose_name='Тема')
    message = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False, verbose_name='Обработано')

    class Meta:
        verbose_name = 'Сообщение обратной связи'            # в единственном числе
        verbose_name_plural = 'Сообщения'            # в множественном числе
        ordering = ['-created_at']

    def __str__(self):
        return f'Сообщение от {self.name} ({self.subject})'
    