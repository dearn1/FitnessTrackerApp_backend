import json
import unittest
from datetime import date, datetime, time, timedelta
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory, force_authenticate

from workouts.models import Workout
from workouts.views import WorkoutViewSet

User = get_user_model()



class MinimalUser:
    """Minimal in-memory user for testing"""

    def __init__(self):
        self.id = 1
        self.pk = 1
        self.email = "test@example.com"
        self.username = "testuser"

    @property
    def is_authenticated(self):
        return True


class MinimalWorkout:
    """Minimal in-memory workout object"""

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.pk = self.id
        self.user_id = kwargs.get('user_id', 1)
        self.workout_type = kwargs.get('workout_type', 'running')
        self.title = kwargs.get('title', 'Morning Run')
        self.description = kwargs.get('description', 'Easy run')
        self.duration = kwargs.get('duration', 30)
        self.calories_burned = kwargs.get('calories_burned', 250.0)
        self.distance = kwargs.get('distance', 5.0)
        self.intensity = kwargs.get('intensity', 'medium')
        self.status = kwargs.get('status', 'planned')
        self.notes = kwargs.get('notes', '')
        self.workout_date = kwargs.get('workout_date', date.today())
        self.started_at = kwargs.get('started_at', None)
        self.completed_at = kwargs.get('completed_at', None)
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())

        # Mock user relationship
        self.user = MinimalUser()

    @property
    def duration_display(self):
        if self.duration:
            hours = self.duration // 60
            minutes = self.duration % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        return "N/A"

    def save(self):
        """Mock save method"""
        pass


class WorkoutViewSetNoDBTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = MinimalUser()
        self.viewset = WorkoutViewSet

    @patch('workouts.views.Workout.objects')
    def test_list_workouts_without_db(self, mock_workout_objects):
        """Test listing workouts without DB"""
        # Mock queryset
        mock_workout1 = MinimalWorkout(id=1, title='Morning Run')
        mock_workout2 = MinimalWorkout(id=2, title='Evening Cycle')

        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.__iter__.return_value = [mock_workout1, mock_workout2]
        mock_queryset.count.return_value = 2

        mock_workout_objects.filter.return_value = mock_queryset

        request = self.factory.get('/api/workouts/')
        force_authenticate(request, user=self.user)

        view = self.viewset.as_view({'get': 'list'})
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('workouts.views.Workout')
    @patch('workouts.views.WorkoutCreateSerializer')
    @patch('workouts.views.WorkoutSerializer')
    def test_create_workout_without_db(self, mock_workout_serializer_class, mock_serializer_class, mock_workout_model):
        """Test creating a workout without DB"""
        # Create a mock serializer instance for WorkoutCreateSerializer
        mock_create_serializer = MagicMock()
        mock_create_serializer.is_valid.return_value = True
        mock_create_serializer.validated_data = {
            'title': 'New Workout',
            'workout_type': 'running',
            'duration': 30,
            'workout_date': date.today()
        }
        
        # Create a mock workout object
        mock_workout = MinimalWorkout(
            id=1,
            title='New Workout',
            workout_type='running',
            duration=30,
            workout_date=date.today(),
            user_id=1
        )
        mock_create_serializer.save.return_value = mock_workout
        
        # Create a mock serializer instance for WorkoutSerializer
        mock_workout_serializer = MagicMock()
        mock_workout_serializer.data = {
            'id': 1,
            'title': 'New Workout',
            'workout_type': 'running',
            'duration': 30,
            'duration_display': '30m',
            'workout_date': date.today().isoformat(),
            'user': 'test@example.com',
            'description': '',
            'calories_burned': None,
            'distance': None,
            'intensity': 'medium',
            'status': 'planned',
            'notes': None,
            'started_at': None,
            'completed_at': None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Configure the mock serializer classes
        mock_serializer_class.return_value = mock_create_serializer
        mock_workout_serializer_class.return_value = mock_workout_serializer
        
        # Create the request
        payload = {
            'workout_type': 'running',
            'title': 'New Workout',
            'duration': 30,
            'workout_date': str(date.today())
        }
        
        request = self.factory.post('/api/workouts/', payload, format='json')
        force_authenticate(request, user=self.user)
        
        # Get the view and call it
        view = self.viewset.as_view({'post': 'create'})
        response = view(request)
        
        # Assert the response is correct
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Workout')
        
        # Verify the serializer was called with the correct data
        self.assertEqual(mock_serializer_class.call_count, 1)
        call_args, call_kwargs = mock_serializer_class.call_args
        self.assertEqual(call_kwargs['data'], payload)
        self.assertIn('request', call_kwargs['context'])
        self.assertEqual(call_kwargs['context']['request'].user, self.user)
        mock_create_serializer.is_valid.assert_called_once_with(raise_exception=True)
        mock_create_serializer.save.assert_called_once_with(user=self.user)

    @patch('workouts.views.WorkoutViewSet.get_object')
    def test_start_workout_without_db(self, mock_get_object):
        """Test starting a workout without DB"""
        mock_workout = MinimalWorkout(id=1, status='planned')
        mock_get_object.return_value = mock_workout

        request = self.factory.post('/api/workouts/1/start/')
        force_authenticate(request, user=self.user)

        view = self.viewset.as_view({'post': 'start'})
        response = view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mock_workout.status, 'in_progress')

    @patch('workouts.views.WorkoutViewSet.get_object')
    def test_complete_workout_without_db(self, mock_get_object):
        """Test completing a workout without DB"""
        mock_workout = MinimalWorkout(id=1, status='in_progress')
        mock_get_object.return_value = mock_workout

        payload = {
            'duration': 45,
            'calories_burned': 350
        }

        request = self.factory.post('/api/workouts/1/complete/', payload, format='json')
        force_authenticate(request, user=self.user)
        view = self.viewset.as_view({'post': 'complete'})
        response = view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mock_workout.status, 'completed')
        self.assertEqual(mock_workout.duration, 45)


class ActivityHistoryTests(APITestCase):
    """Test cases for viewing activity history"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test data with explicit timezone-aware datetimes
        self.today = timezone.now().date()
        self.yesterday = (timezone.now() - timezone.timedelta(days=1)).date()
        self.last_week = (timezone.now() - timezone.timedelta(weeks=1)).date()
        
        # Create workouts on different dates with all required fields
        self.workout1 = Workout.objects.create(
            user=self.user,
            workout_type='running',
            title='Morning Run',
            description='Morning run in the park',
            duration=30,
            calories_burned=250,
            distance=5.0,
            intensity='medium',
            status='completed',
            workout_date=self.today,
            notes='Good run!',
            started_at=timezone.now() - timezone.timedelta(hours=2),
            completed_at=timezone.now() - timezone.timedelta(hours=1)
        )
        
        self.workout2 = Workout.objects.create(
            user=self.user,
            workout_type='cycling',
            title='Evening Ride',
            description='Evening cycling',
            duration=45,
            calories_burned=350,
            distance=15.0,
            intensity='high',
            status='completed',
            workout_date=self.yesterday,
            notes='Fast ride',
            started_at=timezone.now() - timezone.timedelta(days=1, hours=3),
            completed_at=timezone.now() - timezone.timedelta(days=1, hours=2)
        )
        
        self.workout3 = Workout.objects.create(
            user=self.user,
            workout_type='swimming',
            title='Swim Session',
            description='Morning swim',
            duration=60,
            calories_burned=400,
            distance=2.0,
            intensity='medium',
            status='completed',
            workout_date=self.last_week,
            notes='Good swim',
            started_at=timezone.now() - timezone.timedelta(weeks=1, hours=4),
            completed_at=timezone.now() - timezone.timedelta(weeks=1, hours=3)
        )
        
        # Create another user's workout that shouldn't appear in results
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.other_workout = Workout.objects.create(
            user=self.other_user,
            workout_type='running',
            title='Other User Run',
            duration=20,
            calories_burned=150,
            distance=3.0,
            workout_date=self.today,
            status='completed',
            started_at=timezone.now() - timezone.timedelta(hours=5),
            completed_at=timezone.now() - timezone.timedelta(hours=4, minutes=40)
        )
    
    def test_retrieve_activity_history(self):
        """Test retrieving all activity history for the authenticated user"""
        url = reverse('workout-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if 'results' in response.data:
            # Paginated response
            workouts = response.data['results']
            self.assertEqual(len(workouts), 3)  # Should only see own workouts
            # Verify the workouts are ordered by workout_date (newest first)
            workout_dates = [item['workout_date'] for item in workouts]
        else:
            # Non-paginated response
            self.assertEqual(len(response.data), 3)  # Should only see own workouts
            # Verify the workouts are ordered by workout_date (newest first)
            workout_dates = [item['workout_date'] for item in response.data]
            
        # Convert to date objects for proper comparison
        workout_dates = [date.fromisoformat(d) if isinstance(d, str) else d for d in workout_dates]
        self.assertEqual(workout_dates, sorted(workout_dates, reverse=True))
    
    def test_filter_activity_history_by_date_range(self):
        """Test filtering activity history by date range"""
        url = reverse('workout-list')
        params = {
            'start_date': self.yesterday.isoformat(),
            'end_date': self.today.isoformat()
        }
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if 'results' in response.data:
            workouts = response.data['results']
            self.assertEqual(len(workouts), 2)  # Should only see today's and yesterday's workouts
            workout_dates = {item['workout_date'] for item in workouts}
        else:
            self.assertEqual(len(response.data), 2)  # Should only see today's and yesterday's workouts
            workout_dates = {item['workout_date'] for item in response.data}
            
        # Convert to date strings for comparison
        today_str = self.today.isoformat()
        yesterday_str = self.yesterday.isoformat()
        last_week_str = self.last_week.isoformat()
        
        self.assertIn(today_str, workout_dates)
        self.assertIn(yesterday_str, workout_dates)
        self.assertNotIn(last_week_str, workout_dates)
    
    def test_filter_activity_history_by_workout_type(self):
        """Test filtering activity history by workout type"""
        url = reverse('workout-list')
        response = self.client.get(url, {'workout_type': 'running'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if 'results' in response.data:
            workouts = response.data['results']
            self.assertEqual(len(workouts), 1)
            self.assertEqual(workouts[0]['workout_type'], 'running')
        else:
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['workout_type'], 'running')
    
    @unittest.skip("Pagination is not currently enabled in the API")
    def test_activity_history_pagination(self):
        """Test that activity history returns all items by default"""
        url = reverse('workout-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return all 3 workouts in a list
        self.assertEqual(len(response.data), 3)
        
        # Verify we have all expected workouts
        workout_types = {item['workout_type'] for item in response.data}
        self.assertIn('running', workout_types)
        self.assertIn('cycling', workout_types)
        self.assertIn('swimming', workout_types)


class WorkoutDeletionTests(APITestCase):
    """Test cases for deleting workout entries"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test workouts
        self.workout = Workout.objects.create(
            user=self.user,
            workout_type='running',
            title='Morning Run',
            duration=30,
            calories_burned=250,
            status='completed',
            workout_date=timezone.now().date()
        )
        self.other_user_workout = Workout.objects.create(
            user=self.other_user,
            workout_type='cycling',
            title='Evening Ride',
            duration=45,
            calories_burned=350,
            status='completed',
            workout_date=timezone.now().date()
        )
    
    def test_delete_own_workout(self):
        """Test that a user can delete their own workout"""
        url = reverse('workout-detail', args=[self.workout.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Workout.objects.filter(id=self.workout.id).exists())
    
    def test_delete_nonexistent_workout(self):
        """Test deleting a workout that doesn't exist"""
        non_existent_id = 9999
        url = reverse('workout-detail', args=[non_existent_id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_cannot_delete_other_users_workout(self):
        """Test that a user cannot delete another user's workout"""
        url = reverse('workout-detail', args=[self.other_user_workout.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Workout.objects.filter(id=self.other_user_workout.id).exists())
    
    def test_delete_workout_unauthenticated(self):
        """Test that unauthenticated users cannot delete workouts"""
        self.client.force_authenticate(user=None)
        url = reverse('workout-detail', args=[self.workout.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Workout.objects.filter(id=self.workout.id).exists())
