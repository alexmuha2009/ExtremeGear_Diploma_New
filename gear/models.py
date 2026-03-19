from django.db import models
from django.utils import timezone

# 1. ТИПИ ТОВАРІВ (Технічні категорії: Рюкзаки, Шоломи тощо)
class GearCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва категорії")

    class Meta:
        verbose_name = "Тип товару"
        verbose_name_plural = "Gears (Типи товарів)"

    def __str__(self):
        return self.name


# 2. НАПРЯМКИ / ВИДИ СПОРТУ (Відображаються у сайдбарі та картках по центру)
class Sport(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва напрямку")
    icon = models.CharField(max_length=100, verbose_name="Іконка (клас або символ)", help_text="Наприклад: fa-hiking")
    image = models.ImageField(upload_to='sports/', blank=True, null=True, verbose_name="Фото для картки")

    @property
    def gear_count(self):
        """Рахує кількість товарів, прив'язаних до цього спорту для карток по центру"""
        return self.gears.count()

    class Meta:
        verbose_name = "Напрямок"
        verbose_name_plural = "Напрямки (Категорії)"

    def __str__(self):
        return self.name


# 3. СПОРЯДЖЕННЯ (Самі товари)
class Gear(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва")
    brand = models.CharField(max_length=100, verbose_name="Бренд")

    # ГОЛОВНЕ ПОЛЕ ДЛЯ ПІДВАНТАЖЕННЯ В ПОПУЛЯРНІ НАПРЯМКИ
    sports = models.ManyToManyField(
        Sport,
        blank=False,
        related_name='gears',
        verbose_name="Популярні напрямки (Для виводу по центру)",
        help_text="Оберіть напрямок, щоб товар з'явився у відповідній картці на головній"
    )

    # Прив'язка до технічної категорії (ліва панель адмінки)
    category = models.ForeignKey(
        GearCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Тип товару (Технічна категорія)"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    description = models.TextField(blank=True, verbose_name="Опис")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Зображення")
    image_url = models.URLField(blank=True, null=True, verbose_name="Посилання на фото")
    in_stock = models.BooleanField(default=True, verbose_name="В наявності")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0, verbose_name="Рейтинг")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата створення")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Список товарів"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.brand})"


# 4. НОВИНИ
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


# 5. ЗАМОВЛЕННЯ
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