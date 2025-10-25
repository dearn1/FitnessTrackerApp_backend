import json
from datetime import date, datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from workouts.models import Workout

User = get_user_model()


class DailyActivitySummaryTests(APITestCase):
    """Test cases for the daily activity summary feature"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create some test workouts
        self.today = timezone.now().date()
        self.yesterday = self.today - timedelta(days=1)
        
        # Today's workouts
        self.run = Workout.objects.create(
            user=self.user,
            workout_type='running',
            title='Morning Run',
            duration=30,
            calories_burned=250.0,
            distance=5.0,
            intensity='medium',
            status='completed',
            workout_date=self.today,
            date=self.today,
            start_time=time(8, 0),
            end_time=time(8, 30),
            notes='Test run'
        )
        
        self.gym = Workout.objects.create(
            user=self.user,
            workout_type='strength',
            title='Gym Session',
            duration=45,
            calories_burned=350.0,
            intensity='high',
            status='completed',
            workout_date=self.today,
            date=self.today,
            start_time=time(18, 0),
            end_time=time(18, 45),
            notes='Test gym session'
        )
        
        # Yesterday's workout (shouldn't appear in today's summary)
        self.walk = Workout.objects.create(
            user=self.user,
            workout_type='walking',
            title='Evening Walk',
            duration=20,
            calories_burned=100.0,
            distance=1.5,
            intensity='low',
            status='completed',
            workout_date=self.yesterday,
            date=self.yesterday,
            start_time=time(19, 0),
            end_time=time(19, 20),
            notes='Test walk'
        )
    
    def test_get_daily_activity_summary(self):
        """Test retrieving today's activity summary"""
        url = reverse('workout-today')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should have 2 workouts for today
        
        # Verify the data for each workout
        for workout in response.data:
            self.assertIn('id', workout)
            self.assertIn('title', workout)
            self.assertIn('workout_type', workout)
            self.assertIn('duration', workout)
            self.assertIn('calories_burned', workout)
            self.assertEqual(workout['status'], 'completed')
            
            # Verify the workout date is today
            workout_date = timezone.datetime.strptime(
                workout['workout_date'], '%Y-%m-%d'
            ).date()
            self.assertEqual(workout_date, self.today)
    
    def test_empty_daily_summary(self):
        """Test getting daily summary when no workouts exist for the day"""
        # Delete all workouts
        Workout.objects.all().delete()
        
        url = reverse('workout-today')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should be an empty list
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access the endpoint"""
        self.client.logout()
        url = reverse('workout-today')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
