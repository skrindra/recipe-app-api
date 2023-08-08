"""
Tests for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')

# helper function to create a recipe (that can be used for tests)


def create_recipe(user, **params):
    """Create and return a sample recipe."""
    # deafult inputs
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 8,
        'price': Decimal('5.05'),
        'description': 'Sample description',
        'link': 'htps://example.com/recipe.pdf',
    }
    # update the default, if params supplied
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retriving a list of recipes."""
        # create multiple recipes
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        # retrieve object in reverse order (recent first)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_list_limited_to_user(self):
        """Test list of recipes is limited to the authenticated user."""
        other_user = get_user_model().objects.create_user(
            'otheruser@example.com',
            'testpass123',
        )
        # create recipe by both authenticated user and other user
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        # get the recipe list from API
        res = self.client.get(RECIPES_URL)

        # fetch the list of recipes of authenticated user
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
