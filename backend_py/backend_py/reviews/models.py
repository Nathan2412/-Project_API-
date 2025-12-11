from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from backend_py.products.models import Product


class Review(models.Model):
    """Modele pour les avis produits"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Note entre 1 et 5"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Un utilisateur ne peut laisser qu'un seul avis par produit
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"Avis de {self.user.email} sur {self.product.title} - {self.rating}/5"
