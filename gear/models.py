from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class GearCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва категорії")

    class Meta:
        verbose_name = "Тип товару"
        verbose_name_plural = "Gears (Типи товарів)"

    def __str__(self):
        return self.name


class Sport(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва напрямку")
    icon = models.CharField(max_length=100, verbose_name="Іконка (клас або символ)")
    image = models.ImageField(upload_to='sports/', blank=True, null=True, verbose_name="Фото")

    @property
    def gear_count(self):
        return self.gears.count()

    class Meta:
        verbose_name = "Напрямок"
        verbose_name_plural = "Напрямки (Категорії)"

    def __str__(self):
        return self.name


class Gear(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва")
    brand = models.CharField(max_length=100, verbose_name="Бренд")
    sports = models.ManyToManyField(Sport, blank=False, related_name='gears', verbose_name="Популярні напрямки")
    category = models.ForeignKey(GearCategory, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Тип товару")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    description = models.TextField(blank=True, verbose_name="Опис")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Зображення")
    image_url = models.URLField(blank=True, null=True, verbose_name="Посилання на фото")
    in_stock = models.BooleanField(default=True, verbose_name="В наявності")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0, verbose_name="Рейтинг")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата створення")

    # 🏍️ ОРЕНДА — нові поля
    is_rentable = models.BooleanField(default=False, verbose_name="Доступний для оренди")
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Ціна оренди за добу (грн)")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Список товарів"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.brand})"


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Фото новини")
    description = models.TextField(verbose_name="Короткий опис", default="")
    content = models.TextField(blank=True, verbose_name="Повний текст")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    class Meta:
        verbose_name = "Новина"
        verbose_name_plural = "Новини"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Order(models.Model):
    gear = models.ForeignKey(Gear, on_delete=models.CASCADE, verbose_name="Товар")
    customer_name = models.CharField(max_length=100, verbose_name="Ім'я клієнта")
    customer_phone = models.CharField(max_length=20, verbose_name="Телефон")
    customer_email = models.EmailField(verbose_name="Email", blank=True, null=True)
    customer_telegram = models.CharField(max_length=100, verbose_name="Telegram", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата замовлення")

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ['-created_at']

    def __str__(self):
        return f"Замовлення від {self.customer_name}"


class RentalItem(models.Model):
    """Прив'язаний до товару Gear — не окремий інвентар"""
    gear = models.OneToOneField(
        Gear, on_delete=models.CASCADE,
        related_name='rental_item',
        verbose_name="Товар зі списку"
    )
    is_available = models.BooleanField(default=True, verbose_name="Доступне для оренди")

    class Meta:
        verbose_name = "Позиція для оренди"
        verbose_name_plural = "Інвентар для оренди"

    # Беремо всі дані з Gear
    @property
    def name(self):
        return self.gear.name

    @property
    def description(self):
        return self.gear.description

    @property
    def price_per_day(self):
        return self.gear.price_per_day

    @property
    def image(self):
        return self.gear.image

    @property
    def image_url(self):
        return self.gear.image_url

    @property
    def sport(self):
        return self.gear.sports.first()

    def __str__(self):
        return f"{self.gear.name} — {self.gear.price_per_day} грн/доба"


class Rental(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує підтвердження'),
        ('confirmed', 'Підтверджено'),
        ('active', 'Активна'),
        ('completed', 'Завершена'),
        ('cancelled', 'Скасована'),
    ]

    gear = models.ForeignKey(Gear, on_delete=models.CASCADE, verbose_name="Товар")
    customer_name = models.CharField(max_length=100, verbose_name="Ім'я клієнта")
    customer_phone = models.CharField(max_length=20, verbose_name="Телефон")
    customer_email = models.EmailField(verbose_name="Email", blank=True, null=True)
    customer_telegram = models.CharField(max_length=100, verbose_name="Telegram", blank=True, null=True)
    start_date = models.DateField(verbose_name="Дата початку")
    end_date = models.DateField(verbose_name="Дата закінчення")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сума оренди", default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Stripe Session ID")

    class Meta:
        verbose_name = "Оренда"
        verbose_name_plural = "Оренди"
        ordering = ['-created_at']

    def __str__(self):
        return f"Оренда {self.rental_item.name} — {self.customer_name} ({self.start_date} — {self.end_date})"

    @property
    def days(self):
        return (self.end_date - self.start_date).days or 1