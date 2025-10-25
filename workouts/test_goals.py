import json
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from workouts.models import Goal

User = get_user_model()


class FitnessGoalsTests(APITestCase):
    """Test cases for fitness goals functionality"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create some test goals
        self.today = timezone.now().date()
        self.future_date = self.today + timedelta(days=30)
        
        # Active goal
        self.active_goal = Goal.objects.create(
            user=self.user,
            goal_type='running',
            target_value=100.0,  # 100 km
            current_value=25.0,
            start_date=self.today,
            end_date=self.future_date,
            is_completed=False,
            notes='My running goal'
        )
        
        # Completed goal
        self.completed_goal = Goal.objects.create(
            user=self.user,
            goal_type='weight',
            target_value=75.0,  # 75 kg
            current_value=75.0,
            start_date=self.today - timedelta(days=60),
            end_date=self.today - timedelta(days=30),
            is_completed=True,
            notes='Weight loss goal'
        )
    
    def test_create_goal(self):
        """Test creating a new fitness goal"""
        url = reverse('goal-list')
        data = {
            'goal_type': 'cycling',
            'target_value': 500.0,  # 500 km
            'current_value': 0.0,
            'start_date': self.today.isoformat(),
            'end_date': (self.today + timedelta(days=90)).isoformat(),
            'notes': 'Cycling distance goal'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Goal.objects.count(), 3)  # 2 from setUp + 1 new
        self.assertEqual(Goal.objects.latest('id').goal_type, 'cycling')
    
    def test_list_goals(self):
        """Test retrieving a list of user's goals"""
        url = reverse('goal-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return both goals
    
    def test_get_goal_detail(self):
        """Test retrieving a single goal's details"""
        url = reverse('goal-detail', args=[self.active_goal.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['goal_type'], 'running')
        self.assertEqual(float(response.data['target_value']), 100.0)
    
    def test_update_goal(self):
        """Test updating a goal's details"""
        url = reverse('goal-detail', args=[self.active_goal.id])
        data = {
            'current_value': 50.0,
            'notes': 'Updated running goal progress'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.active_goal.refresh_from_db()
        self.assertEqual(self.active_goal.current_value, 50.0)
        self.assertEqual(self.active_goal.notes, 'Updated running goal progress')
    
    def test_delete_goal(self):
        """Test deleting a goal"""
        url = reverse('goal-detail', args=[self.active_goal.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Goal.objects.count(), 1)  # Only completed_goal should remain
    
    def test_filter_goals_by_status(self):
        """Test filtering goals by completion status"""
        # Test active goals
        url = f"{reverse('goal-list')}?is_completed=false"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.active_goal.id)
        
        # Test completed goals
        url = f"{reverse('goal-list')}?is_completed=true"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.completed_goal.id)
    
    def test_filter_goals_by_type(self):
        """Test filtering goals by type"""
        url = f"{reverse('goal-list')}?goal_type=running"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['goal_type'], 'running')
    
    def test_goal_completion_auto_update(self):
        """Test that goal completion status updates when current_value reaches target"""
        url = reverse('goal-detail', args=[self.active_goal.id])
        data = {'current_value': 100.0}
        
        response = self.client.patch(url, data, format='json')
        self.active_goal.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.active_goal.is_completed)
    
    def test_cannot_update_other_users_goal(self):
        """Test that users can't update other users' goals"""
        # Create a second user
        other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpass123',
            username='otheruser'
        )
        
        # Try to update the first user's goal as the second user
        self.client.force_authenticate(user=other_user)
        url = reverse('goal-detail', args=[self.active_goal.id])
        data = {'current_value': 50.0}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
