from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from backend_py.reviews.models import Review
from backend_py.products.models import Product
from backend_py.users.models import User


class ReviewsApiTests(TestCase):
    """Tests pour l'API Avis"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer un produit
        self.product = Product.objects.create(
            title="Test Product",
            description="Test Description",
            price="99.99",
            stock=10
        )
        
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer un autre utilisateur
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )

    def test_list_reviews_anonymous(self):
        """Les utilisateurs anonymes peuvent voir la liste des avis"""
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_review_anonymous_forbidden(self):
        """Les utilisateurs anonymes ne peuvent pas créer d'avis"""
        url = reverse('review-list')
        data = {
            'product': self.product.id,
            'rating': 5,
            'comment': 'Great product!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_authenticated(self):
        """Les utilisateurs authentifiés peuvent créer des avis"""
        self.client.force_authenticate(user=self.user)
        url = reverse('review-list')
        data = {
            'product': self.product.id,
            'rating': 5,
            'comment': 'Great product!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().user, self.user)

    def test_create_duplicate_review_forbidden(self):
        """Un utilisateur ne peut pas laisser deux avis pour le même produit"""
        # Créer le premier avis
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment='First review'
        )
        
        # Essayer de créer un deuxième avis
        self.client.force_authenticate(user=self.user)
        url = reverse('review-list')
        data = {
            'product': self.product.id,
            'rating': 4,
            'comment': 'Second review'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 1)

    def test_rating_validation(self):
        """La note doit être entre 1 et 5"""
        self.client.force_authenticate(user=self.user)
        url = reverse('review-list')
        
        # Test avec note invalide (0)
        data = {
            'product': self.product.id,
            'rating': 0,
            'comment': 'Invalid rating'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test avec note invalide (6)
        data['rating'] = 6
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_own_review(self):
        """Un utilisateur peut modifier son propre avis"""
        # Créer un avis
        review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment='Original comment'
        )
        
        # Modifier l'avis
        self.client.force_authenticate(user=self.user)
        url = reverse('review-detail', args=[review.id])
        data = {
            'product': self.product.id,
            'rating': 4,
            'comment': 'Updated comment'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.comment, 'Updated comment')
        self.assertEqual(review.rating, 4)

    def test_update_others_review_forbidden(self):
        """Un utilisateur ne peut pas modifier l'avis d'un autre"""
        # Créer un avis avec user1
        review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment='User1 review'
        )
        
        # Essayer de modifier avec user2
        self.client.force_authenticate(user=self.user2)
        url = reverse('review-detail', args=[review.id])
        data = {
            'product': self.product.id,
            'rating': 1,
            'comment': 'Hacked!'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_review(self):
        """Un utilisateur peut supprimer son propre avis"""
        # Créer un avis
        review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment='To be deleted'
        )
        
        # Supprimer l'avis
        self.client.force_authenticate(user=self.user)
        url = reverse('review-detail', args=[review.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)

    def test_delete_others_review_forbidden(self):
        """Un utilisateur ne peut pas supprimer l'avis d'un autre"""
        # Créer un avis avec user1
        review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment='User1 review'
        )
        
        # Essayer de supprimer avec user2
        self.client.force_authenticate(user=self.user2)
        url = reverse('review-detail', args=[review.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 1)

    def test_filter_reviews_by_product(self):
        """Filtrer les avis par product_id"""
        # Créer un deuxième produit
        product2 = Product.objects.create(
            title="Product 2",
            description="Description 2",
            price="49.99",
            stock=5
        )
        
        # Créer des avis pour les deux produits
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment='Review for product 1'
        )
        Review.objects.create(
            user=self.user2,
            product=product2,
            rating=4,
            comment='Review for product 2'
        )
        
        # Filtrer par product_id
        url = f"{reverse('review-list')}?product_id={self.product.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['product'], self.product.id)
