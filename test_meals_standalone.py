import unittest
from unittest.mock import patch, MagicMock
from django.http import HttpRequest
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Mock the Django settings
import sys
import os
import django
from django.conf import settings

# Minimal Django settings
if not settings.configured:
    settings.configure(
        SECRET_KEY='test-key',
        ROOT_URLCONF=None,
        INSTALLED_APPS=[],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
    )
    django.setup()

# Now import the viewset after Django is configured
from meals.views import MealViewSet

class MinimalMeal:
    """Minimal in-memory meal object for testing"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.pk = self.id
        self.meal_type = kwargs.get('meal_type', 'breakfast')
        self.name = kwargs.get('name', 'Test Meal')
        self.calories = kwargs.get('calories', 500)
        self.meal_date = '2023-01-01'
        self.user_id = 1

class TestMealViewSet(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.viewset = MealViewSet()
        
        # Create a test user
        User = get_user_model()
        self.user = User(username='testuser')
        self.user.save = MagicMock(return_value=None)

    @patch('meals.views.MealViewSet.get_serializer')
    def test_create_meal(self, mock_get_serializer):
        # Setup mock serializer
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = {
            'id': 1,
            'name': 'New Meal',
            'meal_type': 'breakfast',
            'calories': 200,
            'meal_date': '2023-01-01'
        }
        mock_serializer.save.return_value = MinimalMeal(id=1, name='New Meal')
        mock_get_serializer.return_value = mock_serializer
        
        # Make request
        request = self.factory.post('/api/meals/', {
            'name': 'New Meal',
            'meal_type': 'breakfast',
            'calories': 200,
            'meal_date': '2023-01-01'
        }, content_type='application/json')
        
        # Set user on request
        request.user = self.user
        
        # Call the viewset's create method directly
        response = self.viewset.create(request)
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        mock_serializer.is_valid.assert_called_once()
        mock_serializer.save.assert_called_once()

    @patch('meals.views.MealViewSet.get_queryset')
    def test_list_meals(self, mock_get_queryset):
        # Setup mock data
        mock_meal1 = MinimalMeal(id=1, name='Breakfast')
        mock_meal2 = MinimalMeal(id=2, name='Lunch')
        mock_get_queryset.return_value = [mock_meal1, mock_meal2]
        
        # Make request
        request = self.factory.get('/api/meals/')
        request.user = self.user
        
        # Call the viewset's list method directly
        response = self.viewset.list(request)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

if __name__ == '__main__':
    unittest.main()
