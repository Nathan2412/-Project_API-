from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Product

class ProductsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        Product.objects.create(title="Item 1", description="Desc", price="9.99", stock=10)

    def test_list_products(self):
        url = reverse('product-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.json()) >= 1)
