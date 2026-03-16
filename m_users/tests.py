# backend/m_users/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from .models import UserProfile
from m_products.models import Product, Customisation
from m_shops.models import Order, OrderItem, Cart
import json

class CoreFunctionTests(TestCase):
    def setUp(self):
        # Test Client
        self.client = Client()

        # add user
        self.user = UserProfile.objects.create(
            email="test@example.com",
            name="Test User",
            clerk_id="clerk_001"
        )

        # add products
        self.product1 = Product.objects.create(name="Snowboard A", price=199.99)
        self.product2 = Product.objects.create(name="Snowboard B", price=299.99)

        # add customisations
        self.custom1 = Customisation.objects.create(
            user_id=self.user.id,
            product=self.product1,
            p_size="160",
            p_finish="glossy",
            p_textures=["tex1.png"]
        )
        self.custom2 = Customisation.objects.create(
            user_id=self.user.id,
            product=self.product2,
            p_size="180",
            p_finish="matte",
            p_textures=["tex2.png"]
        )

    def test_add_design_api(self):
        """test add_design api"""
        url = reverse('add_design')
        payload = {
            "user_id": self.user.id,
            "product_id": self.product1.id,
            "p_size": "170",
            "p_finish": "matte",
            "p_flex": "soft",
            "p_textures": ["tex3.png", "tex4.png"]
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json().get("data")
        self.assertIsNotNone(data)
        self.assertEqual(data["user_id"], self.user.id)
        self.assertEqual(data["product_id"], self.product1.id)

    def test_add_order_api(self):
        """test add_order api"""
        url = reverse('add_order')
        payload = {
            "user_id": self.user.id,
            "total_price": 499.97,
            "order_status": "Pending",
            "address": "123 Test St",
            "email": "test@example.com",
            "list": [
                {
                    "design_id": self.custom1.id,
                    "product_id": self.product1.id,
                    "quantity": 2,
                    "unit_price": 199.99
                },
                {
                    "design_id": self.custom2.id,
                    "product_id": self.product2.id,
                    "quantity": 1,
                    "unit_price": 299.99
                }
            ]
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        resp_data = response.json().get("data")
        self.assertIsNotNone(resp_data)
        order_id = resp_data.get("order_id")
        self.assertTrue(Order.objects.filter(id=order_id).exists())
        self.assertEqual(OrderItem.objects.filter(order_id=order_id).count(), 2)

    def test_cart_crud(self):
        """test cart CRUD operations"""
        # add_to_cart
        cart_item = Cart.objects.create(
            user_id=self.user.id,
            design=self.custom1,
            quantity=1,
            unit_price=199.99
        )
        self.assertEqual(cart_item.quantity, 1)

        # update quantity
        cart_item.quantity = 3
        cart_item.save()
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 3)

        # delete
        cart_id = cart_item.id
        cart_item.delete()
        self.assertFalse(Cart.objects.filter(id=cart_id).exists())
    
    
    def test_add_design_missing_fields(self):
        """add_design missing required fields"""
        url = reverse('add_design')
        payload = {
            # missing product_id
            "user_id": self.user.id
        }
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], 400)

    def test_add_design_product_not_found(self):
        """add_design with invalid product_id"""
        url = reverse('add_design')
        payload = {
            "user_id": self.user.id,
            "product_id": 99999,  # not exist
        }
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["code"], 404)

    def test_add_order_missing_required_field(self):
        """add_order missing total_price"""
        url = reverse('add_order')
        payload = {
            "user_id": self.user.id,
            "list": []
        }
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.json()["code"], 400)

    def test_add_order_empty_list(self):
        """add_order with empty item list"""
        url = reverse('add_order')
        payload = {
            "user_id": self.user.id,
            "total_price": 100,
            "list": []
        }
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.json()["code"], 400)

    def test_add_order_invalid_design(self):
        """add_order with non-existing design"""
        url = reverse('add_order')
        payload = {
            "user_id": self.user.id,
            "total_price": 100,
            "list": [
                {
                    "design_id": 99999,
                    "product_id": self.product1.id,
                    "quantity": 1,
                    "unit_price": 199.99
                }
            ]
        }
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.json()["code"], 400)