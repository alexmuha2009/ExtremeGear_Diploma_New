from django.core.management.base import BaseCommand
from gear.models import Sport, GearCategory, Gear
import random

class Command(BaseCommand):
    help = 'Заповнює базу даних повним комплектом товарів (40+ позицій)'

    def handle(self, *args, **options):
        self.stdout.write('🧹 Очищення старої бази даних...')
        # Видаляємо старі записи, щоб не було дублікатів
        Review.objects.all().delete() if 'Review' in globals() else None
        Gear.objects.all().delete()
        GearCategory.objects.all().delete()
        Sport.objects.all().delete()

        self.stdout.write('🏗️ Створення категорій та видів спорту...')

        # --- 1. СПОРТ ---
        sports_data = [
            {'name': 'Сноубординг', 'icon': '🏂', 'image': 'https://images.unsplash.com/photo-1522056615691-da7b8106c665?w=800&q=80'},
            {'name': 'Лижний спорт', 'icon': '⛷️', 'image': 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=800&q=80'},
            {'name': 'Скелелазіння', 'icon': '🧗', 'image': 'https://images.unsplash.com/photo-1522163182402-834f871fd851?w=800&q=80'},
            {'name': 'Дайвінг', 'icon': '🤿', 'image': 'https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=800&q=80'},
            {'name': 'Серфінг', 'icon': '🏄', 'image': 'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800&q=80'},
            {'name': 'Парашутизм', 'icon': '🪂', 'image': 'https://images.unsplash.com/photo-1521673461240-349f76a5b7d9?w=800&q=80'},
            {'name': 'Хайкінг', 'icon': '🥾', 'image': 'https://images.unsplash.com/photo-1551632811-561732d1e306?w=800&q=80'},
        ]

        sports_map = {}
        for s in sports_data:
            obj, _ = Sport.objects.get_or_create(name=s['name'], defaults={'icon': s['icon'], 'image_url': s['image']})
            sports_map[s['name']] = obj

        # --- 2. КАТЕГОРІЇ ---
        categories_data = ['Екіпірування', 'Одяг', 'Взуття', 'Захист', 'Аксесуари', 'Електроніка', 'Кемпінг']
        cats_map = {}
        for c in categories_data:
            obj, _ = GearCategory.objects.get_or_create(name=c)
            cats_map[c] = obj

        # --- 3. ТОВАРИ (ВЕЛИКИЙ СПИСОК) ---
        gear_list = [
            # СНОУБОРДИНГ
            ('Сноуборд Burton Custom X', 'Burton', 'Екіпірування', ['Сноубординг'], 28999, 'https://images.unsplash.com/photo-1565992441121-4367c2967103?w=600'),
            ('Сноуборд Lib Tech Orca', 'Lib Tech', 'Екіпірування', ['Сноубординг'], 31500, 'https://images.unsplash.com/photo-1520207588543-1e545b20c19e?w=600'),
            ('Черевики DC Judge BOA', 'DC', 'Взуття', ['Сноубординг'], 12400, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600'),
            ('Кріплення Union Force', 'Union', 'Аксесуари', ['Сноубординг'], 9800, 'https://images.unsplash.com/photo-1459745930869-b3d0d72c3cbb?w=600'),
            ('Куртка Volcom L Gore-Tex', 'Volcom', 'Одяг', ['Сноубординг', 'Лижний спорт'], 14500, 'https://images.unsplash.com/photo-1551524559-8af4e6624178?w=600'),

            # ЛИЖІ
            ('Лижі Atomic Redster S9', 'Atomic', 'Екіпірування', ['Лижний спорт'], 22900, 'https://images.unsplash.com/photo-1517176118179-652467d12aed?w=600'),
            ('Лижі Salomon QST 98', 'Salomon', 'Екіпірування', ['Лижний спорт'], 25600, 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=600'),
            ('Шолом POC Obex Spin', 'POC', 'Захист', ['Лижний спорт', 'Сноубординг'], 6700, 'https://images.unsplash.com/photo-1565060169280-9944a159942a?w=600'),
            ('Маска Oakley Flight Deck', 'Oakley', 'Аксесуари', ['Лижний спорт', 'Сноубординг'], 6200, 'https://images.unsplash.com/photo-1515523110800-9415d13b84a8?w=600'),
            ('Лижні палиці Leki Spitfire', 'Leki', 'Аксесуари', ['Лижний спорт'], 3200, 'https://images.unsplash.com/photo-1610552050890-fe99536c2615?w=600'),

            # СКЕЛЕЛАЗІННЯ
            ('Скельники La Sportiva Solution', 'La Sportiva', 'Взуття', ['Скелелазіння'], 6900, 'https://images.unsplash.com/photo-1526662092594-e9a95616b43f?w=600'),
            ('Страхувальна система Petzl Sama', 'Petzl', 'Екіпірування', ['Скелелазіння'], 3400, 'https://images.unsplash.com/photo-1601228224727-2c976a44c9b9?w=600'),
            ('Карабін Black Diamond HotForge', 'Black Diamond', 'Інструменти', ['Скелелазіння'], 450, 'https://images.unsplash.com/photo-1579203672288-29a54a7c0397?w=600'),
            ('Магнезія Liquid Chalk', 'Mammut', 'Аксесуари', ['Скелелазіння'], 350, 'https://images.unsplash.com/photo-1618397349970-22c60e334135?w=600'),
            ('Мотузка Beal Joker 9.1mm', 'Beal', 'Екіпірування', ['Скелелазіння'], 7800, 'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=600'),

            # ДАЙВІНГ
            ('Комп\'ютер Suunto Zoop Novo', 'Suunto', 'Електроніка', ['Дайвінг'], 9500, 'https://images.unsplash.com/photo-1533618331327-023a49257c7c?w=600'),
            ('Ласти Mares Avanti Quattro', 'Mares', 'Взуття', ['Дайвінг'], 4200, 'https://images.unsplash.com/photo-1588643360435-019623d3864c?w=600'),
            ('Маска Cressi F1', 'Cressi', 'Аксесуари', ['Дайвінг'], 1800, 'https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=600'),
            ('Регулятор Apeks XTX50', 'Apeks', 'Екіпірування', ['Дайвінг'], 18500, 'https://images.unsplash.com/photo-1614730321146-b6fa6a46bcb4?w=600'),

            # СЕРФІНГ
            ('Дошка Firewire Sci-Fi 2.0', 'Firewire', 'Екіпірування', ['Серфінг'], 26000, 'https://images.unsplash.com/photo-1531722569936-825d3dd91b15?w=600'),
            ('Гідрокостюм O\'Neill Hyperfreak', 'O\'Neill', 'Одяг', ['Серфінг'], 9200, 'https://images.unsplash.com/photo-1531776597792-7f9999cd88f4?w=600'),
            ('Ліш Dakine Kaimana', 'Dakine', 'Аксесуари', ['Серфінг'], 1500, 'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=600'),
            ('Віск Sex Wax', 'Mr. Zog', 'Аксесуари', ['Серфінг'], 150, 'https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=600'),

            # ПАРАШУТИЗМ
            ('Шолом Cookie G4', 'Cookie', 'Захист', ['Парашутизм'], 14200, 'https://images.unsplash.com/photo-1505228395891-9a51e7e86e81?w=600'),
            ('Висотомір Alti-2 Galaxy', 'Alti-2', 'Електроніка', ['Парашутизм'], 7800, 'https://images.unsplash.com/photo-1529524962638-349f76a5b7d9?w=600'),
            ('Комбінезон Tony Suits', 'Tony Suits', 'Одяг', ['Парашутизм'], 11000, 'https://images.unsplash.com/photo-1500595046891-b34b68d6dda9?w=600'),

            # ЕЛЕКТРОНІКА ТА ІНШЕ
            ('GoPro HERO12 Black', 'GoPro', 'Електроніка', ['Сноубординг', 'Серфінг', 'Лижний спорт', 'Дайвінг'], 16999, 'https://images.unsplash.com/photo-1526657962608-f4049d53c7c2?w=600'),
            ('Дрон DJI Mini 4 Pro', 'DJI', 'Електроніка', ['Хайкінг', 'Сноубординг'], 34000, 'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=600'),
            ('Годинник Garmin Fenix 7', 'Garmin', 'Електроніка', ['Хайкінг', 'Лижний спорт', 'Скелелазіння'], 28000, 'https://images.unsplash.com/photo-1518135114421-4d1eb4c6c51c?w=600'),
            ('Намет MSR Hubba Hubba', 'MSR', 'Кемпінг', ['Хайкінг', 'Альпінізм'], 18500, 'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?w=600'),
            ('Рюкзак Osprey Atmos 65', 'Osprey', 'Кемпінг', ['Хайкінг'], 9800, 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600'),
            ('Спальник North Face Inferno', 'The North Face', 'Кемпінг', ['Альпінізм', 'Хайкінг'], 15000, 'https://images.unsplash.com/photo-1517840545241-c46b1feaa764?w=600'),
            ('Ліхтар Black Diamond Spot', 'Black Diamond', 'Електроніка', ['Хайкінг', 'Скелелазіння'], 1900, 'https://images.unsplash.com/photo-1508873696983-2dfd5898f08b?w=600'),
            ('Термос Stanley Classic', 'Stanley', 'Кемпінг', ['Хайкінг', 'Риболовля'], 2100, 'https://images.unsplash.com/photo-1526401281623-279b498910f5?w=600'),
            ('Ніж Victorinox Climber', 'Victorinox', 'Інструменти', ['Хайкінг', 'Кемпінг'], 1600, 'https://images.unsplash.com/photo-1588412079929-790b9f593d8e?w=600'),
        ]

        self.stdout.write('📦 Додавання товарів...')
        
        count = 0
        for name, brand, cat_name, sport_names, price, img in gear_list:
            cat = cats_map[cat_name]
            
            gear = Gear.objects.create(
                name=name,
                brand=brand,
                category=cat,
                price=price,
                description=f"Високоякісний товар {name} від бренду {brand}. Ідеальний вибір для професіоналів та любителів.",
                image_url=img,
                rating=round(random.uniform(4.0, 5.0), 1),
                in_stock=True
            )
            
            # Додаємо зв'язок зі спортом
            for s_name in sport_names:
                if s_name in sports_map:
                    gear.sports.add(sports_map[s_name])
            
            count += 1
            if count % 5 == 0:
                 self.stdout.write(f'   ...додано {count} товарів')

        self.stdout.write(self.style.SUCCESS(f'🎉 УСПІХ! Додано {count} нових товарів. Магазин заповнений!'))