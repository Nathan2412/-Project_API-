from django.core.management.base import BaseCommand
from backend_py.products.models import Product

SAMPLE = [
    {
        "title": "MacBook Pro 14\"",
        "description": "Ordinateur portable Apple avec puce M3 Pro, 18 Go RAM, 512 Go SSD. Parfait pour les professionnels créatifs.",
        "price": "2499.00",
        "stock": 15,
        "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500"
    },
    {
        "title": "iPhone 15 Pro",
        "description": "Le smartphone le plus avancé d'Apple avec puce A17 Pro, appareil photo 48MP et titane.",
        "price": "1229.00",
        "stock": 25,
        "image": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500"
    },
    {
        "title": "AirPods Pro 2",
        "description": "Écouteurs sans fil avec réduction de bruit active, audio spatial et boîtier MagSafe.",
        "price": "279.00",
        "stock": 50,
        "image": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=500"
    },
    {
        "title": "Sony WH-1000XM5",
        "description": "Casque audio premium avec la meilleure réduction de bruit du marché. 30h d'autonomie.",
        "price": "379.00",
        "stock": 30,
        "image": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=500"
    },
    {
        "title": "Samsung Galaxy S24 Ultra",
        "description": "Smartphone Android haut de gamme avec S Pen, écran 6.8\" AMOLED et caméra 200MP.",
        "price": "1469.00",
        "stock": 20,
        "image": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500"
    },
    {
        "title": "iPad Air M2",
        "description": "Tablette polyvalente avec puce M2, écran Liquid Retina 10.9\" et compatibilité Apple Pencil.",
        "price": "769.00",
        "stock": 35,
        "image": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500"
    },
    {
        "title": "Nintendo Switch OLED",
        "description": "Console de jeu hybride avec écran OLED 7 pouces. Jouez à la maison ou en déplacement.",
        "price": "349.00",
        "stock": 40,
        "image": "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=500"
    },
    {
        "title": "Apple Watch Ultra 2",
        "description": "Montre connectée robuste pour les aventuriers. GPS double fréquence, 36h d'autonomie.",
        "price": "899.00",
        "stock": 18,
        "image": "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=500"
    },
    {
        "title": "Clavier MX Keys S",
        "description": "Clavier sans fil Logitech avec rétroéclairage intelligent et touches parfaites pour la frappe.",
        "price": "119.00",
        "stock": 60,
        "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500"
    },
    {
        "title": "Souris MX Master 3S",
        "description": "Souris ergonomique silencieuse avec molette MagSpeed et capteur 8000 DPI.",
        "price": "109.00",
        "stock": 55,
        "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500"
    },
    {
        "title": "Écran Dell 27\" 4K",
        "description": "Moniteur professionnel UltraSharp avec USB-C, 100% sRGB et pivot réglable.",
        "price": "549.00",
        "stock": 12,
        "image": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500"
    },
    {
        "title": "Sac à dos Peak Design",
        "description": "Sac à dos photo 30L avec accès latéral rapide, compartiment laptop 16\" et étanche.",
        "price": "289.00",
        "stock": 3,
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500"
    },
]

class Command(BaseCommand):
    help = "Seed sample products with realistic data"

    def handle(self, *args, **options):
        # Supprimer les anciens produits de test
        Product.objects.all().delete()
        self.stdout.write("Anciens produits supprimés...")
        
        for item in SAMPLE:
            Product.objects.create(**item)
            self.stdout.write(f"  ✓ {item['title']}")
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ {len(SAMPLE)} produits créés avec succès!"))
