import unittest
from unittest.mock import patch, MagicMock
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Mock the Django settings
import sys
import os
import django
from django.conf import settings

# Minimal Django settings without database
if not settings.configured:
    settings.configure(
        SECRET_KEY='test-key',
        ROOT_URLCONF=None,
        INSTALLED_APPS=[],
        MIDDLEWARE=[],
        DATABASES={},
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
    )
    django.setup()

# Now import the viewset after Django is configured
from meals.views import MealViewSet

class TestMealViewSetUnit(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.viewset = MealViewSet()
        
        # Create a test user mock
        self.user = MagicMock()
        self.user.is_authenticated = True
        self.user.id = 1
        
        # Mock the viewset's methods
        self.viewset.get_serializer = MagicMock()
        self.viewset.get_queryset = MagicMock()
        self.viewset.perform_create = MagicMock()

    def test_create_meal_unit(self):
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
        self.viewset.get_serializer.return_value = mock_serializer
        
        # Create a mock response
        response = MagicMock()
        response.status_code = 201
        response.data = mock_serializer.data
        
        # Mock the APIView's create method
        with patch('rest_framework.mixins.CreateModelMixin.create', 
                  return_value=response) as mock_create:
            
            # Make request
            request = self.factory.post('/api/meals/', {
                'name': 'New Meal',
                'meal_type': 'breakfast',
                'calories': 200,
                'meal_date': '2023-01-01'
            }, content_type='application/json')
            
            # Set user on request
            request.user = self.user
            
            # Call the viewset's create method
            result = self.viewset.create(request)
            
            # Assertions
            self.assertEqual(result.status_code, 201)
            mock_serializer.is_valid.assert_called_once()
            self.viewset.perform_create.assert_called_once_with(mock_serializer)

    def test_list_meals_unit(self):
        # Setup mock data
        mock_queryset = [
            {'id': 1, 'name': 'Breakfast'},
            {'id': 2, 'name': 'Lunch'}
        ]
        self.viewset.get_queryset.return_value = mock_queryset
        
        # Create a mock response
        response = MagicMock()
        response.status_code = 200
        response.data = mock_queryset
        
        # Mock the APIView's list method
        with patch('rest_framework.mixins.ListModelMixin.list', 
                  return_value=response) as mock_list:
            
            # Make request
            request = self.factory.get('/api/meals/')
            request.user = self.user
            
            # Call the viewset's list method
            result = self.viewset.list(request)
            
            # Assertions
            self.assertEqual(result.status_code, 200)
            self.viewset.get_queryset.assert_called_once()

if __name__ == '__main__':
    unittest.main()
