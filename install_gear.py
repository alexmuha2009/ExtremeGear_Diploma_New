import os
import django
import random

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from gear.models import Sport, GearCategory, Gear, News

def run_import():
    print('🚀 Починаємо оновлення контенту...')

    try:
        # 1. Очищення бази (щоб не було дублікатів)
        print('🧹 Очищуємо стару базу...')
        News.objects.all().delete()
        Gear.objects.all().delete()
        GearCategory.objects.all().delete()
        Sport.objects.all().delete()

        # 2. Створення НОВИН (ФОТО + ТЕКСТ)
        print('📰 Додаємо новини та досягнення...')
        
        news_data = [
            {
                'title': 'Відкриття зимового сезону 2026! 🏂',
                'content': 'Ми раді повідомити, що всі гірськолижні курорти Карпат офіційно відкриті! Рівень снігу ідеальний для фрірайду. У нашому магазині з\'явилася нова колекція лиж Atomic та сноубордів Burton. Поспішайте оновити спорядження перед поїздкою!',
                'tag': 'news', # Це новина
                'image': 'https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=800'
            },
            {
                'title': 'Наш клієнт підкорив Монблан! 🏔️',
                'content': 'Вітаємо Олександра з успішним сходженням на Монблан (4807м)! Він готувався до цього 6 місяців і використовував спорядження Petzl та намет MSR, придбані у нас. Пишаємося твоїми досягненнями, Алексе!',
                'tag': 'achievement', # Це досягнення
                'image': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800'
            },
            {
                'title': 'Як обрати перші скельники? 🧗',
                'content': 'Новачкам не варто брати занадто тісне взуття. Пам\'ятайте: скельники мають щільно облягати ногу, пальці повинні бути трохи зігнуті, але це не має викликати пекельного болю. Модель La Sportiva Tarantula — ідеальний вибір для старту.',
                'tag': 'tip', # Це порада
                'image': 'https://images.unsplash.com/photo-1522163182402-834f871fd851?w=800'
            },
            {
                'title': 'Нова поставка GoPro HERO 12 📷',
                'content': 'Знімайте свої пригоди у 5.3K! Нова стабілізація HyperSmooth 6.0 дозволяє знімати ідеально плавне відео навіть під час найактивнішого спуску. Вже в наявності в розділі Електроніка.',
                'tag': 'news',
                'image': 'https://images.unsplash.com/photo-1526657962608-f4049d53c7c2?w=800'
            },
            {
                'title': 'ТОП-5 місць для дайвінгу в Єгипті 🤿',
                'content': 'Блакитна діра в Дахабі, затонулий корабель Тістлегорм та рифи Шарм-ель-Шейха. Читайте наш повний гід по найкращих локаціях Червоного моря в нашому блозі.',
                'tag': 'tip',
                'image': 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800'
            },
            {
                'title': 'Перемога у змаганнях з серфінгу 🏄‍♂️',
                'content': 'Наша команда Extreme Gear посіла перше місце на змаганнях "Odessa Surf Open"! Дякуємо всім за підтримку. Хвилі були неймовірні!',
                'tag': 'achievement',
                'image': 'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800'
            }
        ]

        for item in news_data:
            News.objects.create(
                title=item['title'],
                content=item['content'],
                tag=item['tag'],
                image_url=item['image']
            )

        # 3. Відновлення ТОВАРІВ (щоб магазин не був порожнім)
        print('📦 Відновлюємо товари...')
        
        # Спорт
        sports_data = [
            {'name': 'Сноубординг', 'icon': '🏂', 'img': 'https://images.unsplash.com/photo-1522056615691-da7b8106c665?w=800'},
            {'name': 'Лижний спорт', 'icon': '⛷️', 'img': 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=800'},
            {'name': 'Скелелазіння', 'icon': '🧗', 'img': 'https://images.unsplash.com/photo-1522163182402-834f871fd851?w=800'},
            {'name': 'Дайвінг', 'icon': '🤿', 'img': 'https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=800'},
            {'name': 'Серфінг', 'icon': '🏄', 'img': 'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800'},
            {'name': 'Парашутизм', 'icon': '🪂', 'img': 'https://images.unsplash.com/photo-1521673461240-349f76a5b7d9?w=800'},
            {'name': 'Хайкінг', 'icon': '🥾', 'img': 'https://images.unsplash.com/photo-1551632811-561732d1e306?w=800'},
        ]
        sports_map = {}
        for s in sports_data:
            sports_map[s['name']] = Sport.objects.create(name=s['name'], icon=s['icon'], image_url=s['img'])

        # Категорії
        cats = ['Екіпірування', 'Одяг', 'Взуття', 'Захист', 'Аксесуари', 'Електроніка', 'Кемпінг', 'Інструменти']
        cats_map = {c: GearCategory.objects.create(name=c) for c in cats}

        # Товари
        gear_list = [
            ('Сноуборд Burton Custom X', 'Burton', 'Екіпірування', ['Сноубординг'], 28999, 'https://images.unsplash.com/photo-1565992441121-4367c2967103?w=600'),
            ('Черевики DC Judge BOA', 'DC', 'Взуття', ['Сноубординг'], 12400, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600'),
            ('Кріплення Union Force', 'Union', 'Аксесуари', ['Сноубординг'], 9800, 'https://images.unsplash.com/photo-1459745930869-b3d0d72c3cbb?w=600'),
            ('Лижі Atomic Redster S9', 'Atomic', 'Екіпірування', ['Лижний спорт'], 22900, 'https://images.unsplash.com/photo-1517176118179-652467d12aed?w=600'),
            ('Шолом POC Obex Spin', 'POC', 'Захист', ['Лижний спорт', 'Сноубординг'], 6700, 'https://images.unsplash.com/photo-1565060169280-9944a159942a?w=600'),
            ('Скельники La Sportiva', 'La Sportiva', 'Взуття', ['Скелелазіння'], 6900, 'https://images.unsplash.com/photo-1526662092594-e9a95616b43f?w=600'),
            ('Система Petzl Sama', 'Petzl', 'Екіпірування', ['Скелелазіння'], 3400, 'https://images.unsplash.com/photo-1601228224727-2c976a44c9b9?w=600'),
            ('Комп\'ютер Suunto Zoop', 'Suunto', 'Електроніка', ['Дайвінг'], 9500, 'https://images.unsplash.com/photo-1533618331327-023a49257c7c?w=600'),
            ('Дошка Firewire Sci-Fi', 'Firewire', 'Екіпірування', ['Серфінг'], 26000, 'https://images.unsplash.com/photo-1531722569936-825d3dd91b15?w=600'),
            ('Дрон DJI Mini 4', 'DJI', 'Електроніка', ['Хайкінг'], 34000, 'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=600'),
            ('Намет MSR Hubba', 'MSR', 'Кемпінг', ['Хайкінг'], 18500, 'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?w=600'),
            ('Рюкзак Osprey Atmos', 'Osprey', 'Кемпінг', ['Хайкінг'], 9800, 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600'),
        ]

        for name, brand, cat_name, sport_names, price, img in gear_list:
            if cat_name in cats_map:
                gear = Gear.objects.create(
                    name=name, brand=brand, category=cats_map[cat_name],
                    price=price, description=f'Товар {name} від {brand}.',
                    image_url=img, rating=5.0, in_stock=True
                )
                for s_name in sport_names:
                    if s_name in sports_map:
                        gear.sports.add(sports_map[s_name])

        print('🎉 ГОТОВО! Новини та товари успішно додано.')

    except Exception as e:
        print(f'❌ ПОМИЛКА: {e}')

if __name__ == '__main__':
    run_import()