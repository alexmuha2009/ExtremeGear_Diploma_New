from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import GearCategory, Gear, Sport, News, Order, RentalItem, Rental


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('name', 'gear_count_display')
    search_fields = ('name',)

    def gear_count_display(self, obj):
        return obj.gears.count()
    gear_count_display.short_description = "Кількість товарів"


class RentalItemInline(admin.StackedInline):
    model = RentalItem
    extra = 0
    fields = ('is_available',)
    verbose_name = "Оренда"
    verbose_name_plural = "Налаштування оренди"


@admin.register(Gear)
class GearAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'name', 'brand', 'category', 'price', 'in_stock', 'is_rentable', 'price_per_day')
    list_editable = ('price', 'in_stock', 'is_rentable', 'price_per_day')
    list_filter = ('category', 'sports', 'in_stock', 'is_rentable')
    search_fields = ('name', 'brand', 'description')
    filter_horizontal = ('sports',)
    inlines = [RentalItemInline]

    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'brand', 'category', 'sports', 'description', 'image', 'image_url')
        }),
        ('Продаж', {
            'fields': ('price', 'in_stock', 'rating')
        }),
        ('🏍️ Оренда', {
            'fields': ('is_rentable', 'price_per_day'),
            'description': "Увімкни оренду і вкажи ціну за добу — товар з'явиться на /rental/"
        }),
    )

    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit:cover;border-radius:5px;" />')
        return "Немає фото"
    image_tag.short_description = 'Фото'


@admin.register(GearCategory)
class GearCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_email', 'gear', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('created_at',)


@admin.register(RentalItem)
class RentalItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'price_per_day', 'is_available')
    list_editable = ('is_available',)
    search_fields = ('gear__name',)


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_phone', 'gear', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date')
    search_fields = ('customer_name', 'customer_phone', 'customer_email')
    readonly_fields = ('total_price',)