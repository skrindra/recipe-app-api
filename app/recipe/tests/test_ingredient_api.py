"""
Tests for Ingredients API requests.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return a detail ingredient url."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])

def create_user(email='user@example.com', password='test123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngrdientAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Salt')
        Ingredient.objects.create(user=self.user, name='Sugar')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_ingredients_limited_to_user(self):
        """Test retrieving list of ingredients limited to user."""
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=self.user, name='Salt')
        my_ingredient =Ingredient.objects.create(user=user2, name='Sugar')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.filter(user=self.user).order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Salt')
        payload = {'name': 'Pepper'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Salt')
        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())
