from django.core.management.base import BaseCommand
from backend_py.products.models import Product

SAMPLE = [
    {"title": "Sneakers", "description": "Comfortable sneakers", "price": "59.99", "stock": 100},
    {"title": "Backpack", "description": "Durable backpack", "price": "39.99", "stock": 50},
]

class Command(BaseCommand):
    help = "Seed sample products"

    def handle(self, *args, **options):
        for item in SAMPLE:
            Product.objects.get_or_create(title=item["title"], defaults=item)
        self.stdout.write(self.style.SUCCESS("Seeded products"))
