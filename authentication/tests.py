from unittest import TestCase
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from django.urls import reverse, path, include
from rest_framework.response import Response

# Import your views and serializer
# Adjust the import paths to match your project layout
from authentication.views import UserLoginView

# Provide a minimal URLConf for reversing if needed
# or directly call the view without reverse.
urlpatterns = [
    path('api/auth/login/', UserLoginView.as_view(), name='login'),
]

class MinimalUser:
    """
    Minimal in-memory user object for tests.
    Must support attrs used by:
      - UserProfileSerializer fields
      - SimpleJWT RefreshToken.for_user (requires a truthy .pk or .id)
    """
    def __init__(self):
        self.id = 1
        self.pk = 1
        self.email = "test@example.com"
        self.username = "testuser"
        self.first_name = "Test"
        self.last_name = "User"
        self.phone_number = None
        self.date_of_birth = None
        self.height = None
        self.weight = None
        self.gender = ""
        self.fitness_goal = None
        # created_at is read-only; the serializer may access it.
        # Provide a string or datetime; here a string is fine as serializer returns fields directly.
        self.created_at = "2024-01-01T00:00:00Z"

    # DRF permissions check uses IsAuthenticated which inspects request.user.is_authenticated
    @property
    def is_authenticated(self):
        return True

class AuthenticationNoDBTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.login_view = UserLoginView.as_view()

    @patch("authentication.views.authenticate")
    def test_user_login_success_without_db(self, mock_authenticate):
        """
        Patches authenticate to return a minimal in-memory user.
        Verifies 200 and tokens in the response. No DB access.
        """
        dummy_user = MinimalUser()
        mock_authenticate.return_value = dummy_user

        payload = {
            "email": "test@example.com",
            "password": "TestPass123!"
        }
        request = self.factory.post("/api/auth/login/", payload, format="json")
        response = self.login_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["user"]["email"], "test@example.com")

    @patch("authentication.views.authenticate")
    def test_user_login_invalid_credentials_without_db(self, mock_authenticate):
        """
        Patches authenticate to return None to simulate invalid creds.
        Expects 401. No DB access.
        """
        mock_authenticate.return_value = None

        payload = {
            "email": "wrong@example.com",
            "password": "WrongPass123!"
        }
        request = self.factory.post("/api/auth/login/", payload, format="json")
        response = self.login_view(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)

