import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from gear.models import Gear

def get_photo(name, brand):
    name = name.lower()
    brand = brand.lower()

    if 'сноуборд' in name:
        return 'https://images.unsplash.com/photo-1565992441121-4367c2967103?w=600&q=80&fit=crop'
    if 'кріплення' in name or 'крiplення' in name:
        return 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=600&q=80&fit=crop'
    if 'шолом' in name:
        if any(x in brand for x in ['fox', 'bell', 'alpinestars', 'troy', 'fly', 'cookie', 'tonfly']):
            return 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80&fit=crop'
        return 'https://images.unsplash.com/photo-1510155096015-5a63da2b1df4?w=600&q=80&fit=crop'
    if 'скельники' in name:
        return 'https://images.unsplash.com/photo-1526662092594-e9a95616b43f?w=600&q=80&fit=crop'
    if 'черевики' in name:
        if any(x in brand for x in ['fox', 'alpinestars', 'gaerne', 'sidi']):
            return 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600&q=80&fit=crop'
        if any(x in brand for x in ['salomon', 'la sportiva', 'scarpa']):
            return 'https://images.unsplash.com/photo-1551632811-561732d1e306?w=600&q=80&fit=crop'
        return 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80&fit=crop'
    if 'боти' in name:
        return 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80&fit=crop'
    if 'куртка' in name:
        return 'https://images.unsplash.com/photo-1544923246-77307dd654cb?w=600&q=80&fit=crop'
    if 'штани' in name or 'бордшорти' in name:
        if any(x in brand for x in ['fox', 'alpinestars']):
            return 'https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=600&q=80&fit=crop'
        return 'https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=600&q=80&fit=crop'
    if 'рукавиці' in name:
        return 'https://images.unsplash.com/photo-1586348943529-beaae6c28db9?w=600&q=80&fit=crop'
    if 'маска' in name:
        if any(x in brand for x in ['cressi', 'mares', 'scubapro']):
            return 'https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=600&q=80&fit=crop'
        return 'https://images.unsplash.com/photo-1510155096015-5a63da2b1df4?w=600&q=80&fit=crop'
    if 'окуляри' in name:
        if any(x in brand for x in ['fox', '100%', 'oakley', 'skyfall', 'parasport']):
            return 'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=600&q=80&fit=crop'
        return 'https://images.unsplash.com/photo-1510155096015-5a63da2b1df4?w=600&q=80&fit=crop'
    if 'рюкзак' in name:
        return 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&q=80&fit=crop'
    if 'намет' in name:
        return 'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=600&q=80&fit=crop'
    if 'спальник' in name or 'килимок' in name:
        return 'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?w=600&q=80&fit=crop'
    if 'мотузка' in name:
        return 'https://images.unsplash.com/photo-1601228224727-2c976a44c9b9?w=600&q=80&fit=crop'
    if any(x in name for x in ['система', 'карабін', 'відтяжки', 'закладки', 'камалот', 'страхувальний']):
        return 'https://images.unsplash.com/photo-1601228224727-2c976a44c9b9?w=600&q=80&fit=crop'
    if 'каска' in name:
        return 'https://images.unsplash.com/photo-1510155096015-5a63da2b1df4?w=600&q=80&fit=crop'
    if 'ліхтар' in name:
        return 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80&fit=crop'
    if 'альтиметр' in name or 'комп' in name:
        return 'https://images.unsplash.com/photo-1533618331327-023a49257c7c?w=600&q=80&fit=crop'
    if 'gps' in name or 'garmin' in brand:
        return 'https://images.unsplash.com/photo-1533618331327-023a49257c7c?w=600&q=80&fit=crop'
    if 'gopro' in name or 'камера' in name or 'drift' in name:
        return 'https://images.unsplash.com/photo-1526657962608-f4049d53c7c2?w=600&q=80&fit=crop'
    if 'дрон' in name or 'dji' in brand:
        return 'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=600&q=80&fit=crop'
    if 'дошка' in name or 'лонгборд' in name:
        return 'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=600&q=80&fit=crop'
    if 'гідрокостюм' in name or 'сухий костюм' in name:
        return 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=600&q=80&fit=crop'
    if any(x in name for x in ['парашут', 'контейнер', 'вінгсьют', 'комбінезон']):
        return 'https://images.unsplash.com/photo-1521673461240-349f76a5b7d9?w=600&q=80&fit=crop'
    if any(x in name for x in ['захист', 'наколінники', 'налокітники', 'бронежилет']):
        return 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&q=80&fit=crop'
    if any(x in name for x in ['магнезія', 'мішечок']):
        return 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&q=80&fit=crop'
    if any(x in name for x in ['термобілизна', 'флісова', 'рашгард', 'джерсі']):
        return 'https://images.unsplash.com/photo-1503341504253-dff4815485f1?w=600&q=80&fit=crop'
    if any(x in name for x in ['балаклава', 'шапка']):
        return 'https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&q=80&fit=crop'
    if 'ласти' in name:
        return 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=600&q=80&fit=crop'
    if any(x in name for x in ['регулятор', 'bcd', 'балон', 'жилет', 'буй', 'пояс', 'трубка']):
        return 'https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=600&q=80&fit=crop'
    if 'палки' in name:
        return 'https://images.unsplash.com/photo-1551632811-561732d1e306?w=600&q=80&fit=crop'
    if any(x in name for x in ['пальник', 'казанок', 'фільтр']):
        return 'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?w=600&q=80&fit=crop'
    if any(x in name for x in ['ніж', 'молоток', 'інструментарій', 'підставка']):
        return 'https://images.unsplash.com/photo-1504148455328-c376907d081c?w=600&q=80&fit=crop'
    if any(x in name for x in ['сумка', 'чохол', 'логбук']):
        return 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&q=80&fit=crop'
    if any(x in name for x in ['ліш', 'кіль', 'трекпад', 'парафін', 'воскочистка', 'крем']):
        return 'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=600&q=80&fit=crop'
    if any(x in name for x in ['шкарпетки', 'гетри', 'підтяжки', 'ремінь']):
        return 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80&fit=crop'
    if 'аптечка' in name:
        return 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&q=80&fit=crop'
    
    return 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=600&q=80&fit=crop'

updated = 0
for gear in Gear.objects.all():
    gear.image_url = get_photo(gear.name, gear.brand)
    gear.save()
    updated += 1

print(f'Оновлено фото для {updated} товарів!')
