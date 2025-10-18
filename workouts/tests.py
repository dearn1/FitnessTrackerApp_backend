from django.test import SimpleTestCase
from unittest.mock import patch, MagicMock, PropertyMock
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from datetime import date, datetime
from .views import WorkoutViewSet


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


class WorkoutViewSetNoDBTests(SimpleTestCase):
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


from django.test import TestCase

# Create your tests here.
