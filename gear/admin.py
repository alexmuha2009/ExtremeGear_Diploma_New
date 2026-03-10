from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import GearCategory, Gear, Sport, News, Order

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('name', 'gear_count_display')
    search_fields = ('name',)

    def gear_count_display(self, obj):
        # Відображаємо кількість товарів для цього виду спорту
        return obj.gears.count()
    gear_count_display.short_description = "Кількість товарів"

@admin.register(Gear)
class GearAdmin(admin.ModelAdmin):
    # Додано 'image_tag' для перегляду фото та 'brand'
    list_display = ('image_tag', 'name', 'brand', 'category', 'price', 'in_stock')
    
    # Дозволяє змінювати ціну та наявність прямо у списку!
    list_editable = ('price', 'in_stock')
    
    list_filter = ('category', 'sports', 'in_stock')
    search_fields = ('name', 'brand', 'description')
    filter_horizontal = ('sports',) 

    def image_tag(self, obj):
        # Виводить маленьку прев'юшку фото в адмінці
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit:cover; border-radius:5px;" />')
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
    # Більш детальний список замовлень
    list_display = ('id', 'customer_name', 'customer_email', 'gear', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('created_at',) # Дата замовлення не редагується