from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from backend_py.orders.models import Order
from backend_py.products.models import Product
from backend_py.users.models import User


class OrderStatusUpdateTests(TestCase):
    """Tests pour la mise à jour du statut des commandes"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer des utilisateurs
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='adminpass123',
            is_staff=True
        )
        
        self.normal_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='userpass123'
        )
        
        # Créer un produit
        self.product = Product.objects.create(
            title="Test Product",
            description="Test Description",
            price="99.99",
            stock=10
        )

    def test_normal_user_cannot_update_order_status(self):
        """Les utilisateurs normaux ne peuvent pas mettre à jour le statut"""
        # Créer une commande
        order = Order.objects.create(
            user=self.normal_user,
            total=99.99,
            status='pending'
        )
        
        # Essayer de mettre à jour avec un utilisateur normal
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('order-detail', args=[order.id])
        data = {'status': 'shipped'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_order_status(self):
        """Les admins peuvent mettre à jour le statut des commandes"""
        # Créer une commande
        order = Order.objects.create(
            user=self.normal_user,
            total=99.99,
            status='pending'
        )
        
        # Mettre à jour avec un admin
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('order-detail', args=[order.id])
        data = {'status': 'shipped'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'shipped')

    def test_admin_can_update_order_status_full_update(self):
        """Les admins peuvent faire une mise à jour complète (PUT)"""
        # Créer une commande
        order = Order.objects.create(
            user=self.normal_user,
            total=99.99,
            status='pending'
        )
        
        # Mettre à jour avec un admin (PUT)
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('order-detail', args=[order.id])
        data = {'status': 'delivered'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'delivered')

    def test_valid_status_values(self):
        """Test que seuls les statuts valides sont acceptés"""
        # Créer une commande
        order = Order.objects.create(
            user=self.normal_user,
            total=99.99,
            status='pending'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('order-detail', args=[order.id])
        
        # Tester les statuts valides
        valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
        for valid_status in valid_statuses:
            data = {'status': valid_status}
            response = self.client.patch(url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            order.refresh_from_db()
            self.assertEqual(order.status, valid_status)

    def test_invalid_status_rejected(self):
        """Test qu'un statut invalide est rejeté"""
        # Créer une commande
        order = Order.objects.create(
            user=self.normal_user,
            total=99.99,
            status='pending'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('order-detail', args=[order.id])
        data = {'status': 'invalid_status'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
