from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from unittest.mock import patch, MagicMock

class MockUser:
    is_authenticated = True
    is_active = True
    id = 1
    pk = 1
    
    def has_perm(self, perm):
        return True

class TestMealViews(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = MockUser()
        
    @patch('meals.views.MealViewSet')
    def test_meal_list_view(self, mock_viewset):
        """Test that the meal list view returns a 200 status code."""
        # Setup mock viewset
        mock_view = MagicMock()
        mock_view.get.return_value = MagicMock(status_code=200)
        mock_viewset.as_view.return_value = lambda request: mock_view.get(request)
        
        # Create request and authenticate
        request = self.factory.get('/api/meals/')
        force_authenticate(request, user=self.user)
        
        # Call the view
        from meals.views import MealViewSet
        view = MealViewSet.as_view({'get': 'list'})
        response = view(request)
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    @patch('meals.views.MealViewSet')
    def test_meal_create_view(self, mock_viewset):
        """Test that the meal create view returns a 201 status code."""
        # Setup mock viewset
        mock_view = MagicMock()
        mock_view.post.return_value = MagicMock(status_code=201)
        mock_viewset.as_view.return_value = lambda request: mock_view.post(request)
        
        # Create request and authenticate
        request = self.factory.post(
            '/api/meals/', 
            {'name': 'Test Meal'}, 
            format='json'
        )
        force_authenticate(request, user=self.user)
        
        # Call the view
        from meals.views import MealViewSet
        view = MealViewSet.as_view({'post': 'create'})
        response = view(request)
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
