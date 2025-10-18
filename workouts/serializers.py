from rest_framework import serializers
from .models import Workout
from django.utils import timezone


class WorkoutSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    duration_display = serializers.ReadOnlyField()

    class Meta:
        model = Workout
        fields = [
            'id', 'user', 'workout_type', 'title', 'description',
            'duration', 'duration_display', 'calories_burned', 'distance',
            'intensity', 'status', 'notes', 'workout_date',
            'started_at', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_workout_date(self, value):
        """Ensure workout date is not in the future"""
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "Workout date cannot be in the future."
            )
        return value

    def validate(self, data):
        """Custom validation for workout data"""
        # If status is completed, ensure we have duration
        if data.get('status') == 'completed' and not data.get('duration'):
            raise serializers.ValidationError({
                'duration': 'Duration is required for completed workouts.'
            })

        # If distance is provided, ensure it's positive
        if data.get('distance') and data.get('distance') <= 0:
            raise serializers.ValidationError({
                'distance': 'Distance must be greater than 0.'
            })

        # If calories_burned is provided, ensure it's positive
        if data.get('calories_burned') and data.get('calories_burned') <= 0:
            raise serializers.ValidationError({
                'calories_burned': 'Calories burned must be greater than 0.'
            })

        return data


class WorkoutCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating workouts with minimal required fields"""

    class Meta:
        model = Workout
        fields = [
            'workout_type', 'title', 'description', 'duration',
            'calories_burned', 'distance', 'intensity', 'status',
            'notes', 'workout_date'
        ]

    def validate_workout_date(self, value):
        """Ensure workout date is not in the future"""
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "Workout date cannot be in the future."
            )
        return value


class WorkoutUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating workouts"""

    class Meta:
        model = Workout
        fields = [
            'workout_type', 'title', 'description', 'duration',
            'calories_burned', 'distance', 'intensity', 'status',
            'notes', 'workout_date', 'started_at', 'completed_at'
        ]

    def update(self, instance, validated_data):
        """Handle status changes and timestamps"""
        new_status = validated_data.get('status', instance.status)

        # Auto-set timestamps based on status
        if new_status == 'in_progress' and not instance.started_at:
            validated_data['started_at'] = timezone.now()

        if new_status == 'completed' and not instance.completed_at:
            validated_data['completed_at'] = timezone.now()

        return super().update(instance, validated_data)


class WorkoutSummarySerializer(serializers.Serializer):
    """Serializer for workout statistics and summaries"""
    total_workouts = serializers.IntegerField()
    total_duration = serializers.IntegerField()
    total_calories = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_distance = serializers.DecimalField(max_digits=10, decimal_places=2)
    completed_workouts = serializers.IntegerField()
    workout_types = serializers.DictField()
