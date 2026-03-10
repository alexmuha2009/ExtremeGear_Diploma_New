import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from gear.models import Gear, GearCategory, Sport, News


def populate():
    print("Start cleaning...")

    Gear.objects.all().delete()
    GearCategory.objects.all().delete()
    Sport.objects.all().delete()
    News.objects.all().delete()

    print("Creating categories...")
    cat_snow = GearCategory.objects.create(name="Snowboarding")
    cat_ski = GearCategory.objects.create(name="Skiing")
    cat_moto = GearCategory.objects.create(name="Moto")

    print("Creating sports...")
    sport_snow = Sport.objects.create(name="Snowboarding", icon="🏂")
    sport_ski = Sport.objects.create(name="Skiing", icon="⛷️")
    sport_moto = Sport.objects.create(name="Motocross", icon="🏍️")

    print("Adding items...")
    g1 = Gear.objects.create(
        name="Burton Custom X",
        brand="Burton",
        price=28500,
        category=cat_snow,
        description="Top board",
        in_stock=True
    )
    sport_snow.gear.add(g1)

    g2 = Gear.objects.create(
        name="Atomic Redster",
        brand="Atomic",
        price=19000,
        category=cat_ski,
        description="Fast skis",
        in_stock=True
    )
    sport_ski.gear.add(g2)

    g3 = Gear.objects.create(
        name="Shoei Helmet",
        brand="Shoei",
        price=24000,
        category=cat_moto,
        description="Safe helmet",
        in_stock=True
    )
    sport_moto.gear.add(g3)

    print("Adding news...")
    News.objects.create(
        title="We are open!",
        description="Welcome to our shop."
    )

    print("DONE! Success.")


if __name__ == "__main__":
    populate()
