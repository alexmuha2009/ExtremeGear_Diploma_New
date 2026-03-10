import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from gear.models import Sport, GearCategory, Gear, News

def fix_full_shop():
    print('🚀 Наповнюємо магазин...')
    
    # Чистимо, щоб не було дублікатів
    News.objects.all().delete()
    Gear.objects.all().delete()
    GearCategory.objects.all().delete()
    Sport.objects.all().delete()

    # Створюємо категорії
    cats = ['Екіпірування', 'Одяг', 'Взуття', 'Захист', 'Аксесуари', 'Електроніка', 'Кемпінг']
    cat_objs = {c: GearCategory.objects.create(name=c) for c in cats}

    # Створюємо спорт
    sports = [
        ('Сноубординг', '🏂'), ('Лижний спорт', '⛷️'), ('Скелелазіння', '🧗'),
        ('Дайвінг', '🤿'), ('Серфінг', '🏄'), ('Хайкінг', '🥾')
    ]
    sport_objs = {}
    for name, icon in sports:
        sport_objs[name] = Sport.objects.create(name=name, icon=icon)

    # Товари
    products = [
        ('Сноуборд Burton', 'Burton', 'Екіпірування', 28999, 'https://images.unsplash.com/photo-1565992441121-4367c2967103?w=600'),
        ('Намет MSR Hubba', 'MSR', 'Кемпінг', 18500, 'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?w=600'),
        ('GoPro HERO12', 'GoPro', 'Електроніка', 16999, 'https://images.unsplash.com/photo-1526657962608-f4049d53c7c2?w=600'),
        ('Лижі Atomic', 'Atomic', 'Екіпірування', 22000, 'https://images.unsplash.com/photo-1517176118179-652467d12aed?w=600'),
        ('Рюкзак Osprey', 'Osprey', 'Кемпінг', 9800, 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600'),
    ]

    for name, brand, c_name, price, img in products:
        if c_name in cat_objs:
            g = Gear.objects.create(
                name=name, brand=brand, category=cat_objs[c_name],
                price=price, description=f'Чудовий {name}.', image_url=img, in_stock=True
            )
            # Додаємо до всіх видів спорту для тесту
            for s in sport_objs.values():
                g.sports.add(s)

    print('✅ БАЗА ЗАПОВНЕНА! Онови сторінку.')

if __name__ == '__main__':
    fix_full_shop()