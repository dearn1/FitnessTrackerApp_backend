from django.test import SimpleTestCase, TestCase
from unittest.mock import Mock, patch

class SimpleStepTests(SimpleTestCase):
    @patch('steps.models.StepGoal.user')
    def test_step_goal_str_representation(self, mock_user):
        """Test the string representation of a step goal"""
        from .models import StepGoal
        
        # Setup mock user
        mock_user.username = 'testuser'
        
        goal = StepGoal(daily_goal=10000)
        goal.user = mock_user
        
        self.assertEqual(str(goal), "testuser's goal: 10,000 steps/day")
    
    @patch('steps.models.DailySteps.user')
    def test_goal_achieved_calculation(self, mock_user):
        """Test the goal_achieved method of DailySteps"""
        from .models import DailySteps, StepGoal
        
        # Setup mock step goal
        mock_step_goal = Mock(spec=StepGoal)
        mock_step_goal.daily_goal = 10000
        
        # Setup mock user with step_goal property
        mock_user.step_goal = mock_step_goal
        
        # Create test instances with mock user
        below_goal = DailySteps(steps=8500)
        below_goal.user = mock_user
        
        at_goal = DailySteps(steps=10000)
        at_goal.user = mock_user
        
        above_goal = DailySteps(steps=12000)
        above_goal.user = mock_user
        
        # Test the property
        self.assertFalse(below_goal.goal_achieved)
        self.assertTrue(at_goal.goal_achieved)
        self.assertTrue(above_goal.goal_achieved)
