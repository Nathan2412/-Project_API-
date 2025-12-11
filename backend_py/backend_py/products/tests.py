from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Product
from backend_py.users.models import User


class ProductsApiTests(TestCase):
    """Tests pour l'API Produits"""
    
    def setUp(self):
        self.client = APIClient()
        self.product1 = Product.objects.create(
            title="Produit Test 1", 
            description="Description du produit 1", 
            price="29.99", 
            stock=10,
            image="https://example.com/image1.jpg"
        )
        self.product2 = Product.objects.create(
            title="Produit Test 2", 
            description="Description du produit 2", 
            price="49.99", 
            stock=5
        )
        
        # Créer un utilisateur admin pour les tests
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='adminpass123',
            is_staff=True
        )
        
        # Créer un utilisateur normal
        self.normal_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='userpass123'
        )

    def test_list_products_anonymous(self):
        """Les utilisateurs anonymes peuvent voir la liste des produits"""
        url = reverse('product-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 2)

    def test_get_product_detail(self):
        """Récupérer les détails d'un produit"""
        url = reverse('product-detail', args=[self.product1.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()['title'], 'Produit Test 1')
        self.assertEqual(res.json()['price'], '29.99')

    def test_create_product_anonymous_forbidden(self):
        """Les utilisateurs anonymes ne peuvent pas créer de produits"""
        url = reverse('product-list')
        data = {
            'title': 'Nouveau Produit',
            'description': 'Description',
            'price': '19.99',
            'stock': 20
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_product_normal_user_forbidden(self):
        """Les utilisateurs normaux ne peuvent pas créer de produits"""
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('product-list')
        data = {
            'title': 'Nouveau Produit',
            'description': 'Description',
            'price': '19.99',
            'stock': 20
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_admin_success(self):
        """Les admins peuvent créer des produits"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('product-list')
        data = {
            'title': 'Nouveau Produit',
            'description': 'Description',
            'price': '19.99',
            'stock': 20
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)

    def test_update_product_admin_success(self):
        """Les admins peuvent modifier des produits"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('product-detail', args=[self.product1.id])
        data = {
            'title': 'Produit Modifié',
            'description': 'Nouvelle description',
            'price': '39.99',
            'stock': 15
        }
        res = self.client.put(url, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.title, 'Produit Modifié')

    def test_delete_product_admin_success(self):
        """Les admins peuvent supprimer des produits"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('product-detail', args=[self.product1.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 1)

    def test_product_stock_validation(self):
        """Le stock ne peut pas être négatif"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('product-list')
        data = {
            'title': 'Produit Invalid',
            'description': 'Description',
            'price': '19.99',
            'stock': -5
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
