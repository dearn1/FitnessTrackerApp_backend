from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Workout(models.Model):
    WORKOUT_TYPES = [
        ('running', 'Running'),
        ('cycling', 'Cycling'),
        ('swimming', 'Swimming'),
        ('walking', 'Walking'),
        ('gym', 'Gym Workout'),
        ('yoga', 'Yoga'),
        ('pilates', 'Pilates'),
        ('hiit', 'HIIT'),
        ('cardio', 'Cardio'),
        ('strength', 'Strength Training'),
        ('sports', 'Sports'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workouts'
    )
    workout_type = models.CharField(
        max_length=20,
        choices=WORKOUT_TYPES,
        default='other'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    duration = models.IntegerField(
        help_text="Duration in minutes",
        null=True,
        blank=True
    )
    calories_burned = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Calories burned"
    )
    distance = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Distance in kilometers"
    )
    intensity = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ],
        default='medium'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned'
    )
    notes = models.TextField(blank=True, null=True)
    workout_date = models.DateField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workouts'
        ordering = ['-workout_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'workout_date']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.title} - {self.workout_date}"

    @property
    def duration_display(self):
        """Return formatted duration"""
        if self.duration:
            hours = self.duration // 60
            minutes = self.duration % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        return "N/A"

    # Date and Time fields
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True, help_text="Time when workout started")
    end_time = models.TimeField(null=True, blank=True, help_text="Time when workout ended")

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-start_time']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'workout_type']),
        ]

    def __str__(self):
        time_str = f" at {self.start_time.strftime('%H:%M')}" if self.start_time else ""
        return f"{self.user.username} - {self.title} on {self.date}{time_str}"

    @property
    def datetime_display(self):
        """Return formatted date and time string"""
        if self.start_time:
            return f"{self.date.strftime('%Y-%m-%d')} {self.start_time.strftime('%H:%M')}"
        return self.date.strftime('%Y-%m-%d')

    @property
    def time_range_display(self):
        """Return formatted time range if both start and end times exist"""
        if self.start_time and self.end_time:
            return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
        elif self.start_time:
            return f"Started at {self.start_time.strftime('%H:%M')}"
        return "Time not specified"

    def clean(self):
        from django.core.exceptions import ValidationError

        # Validate end_time is after start_time
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError({
                    'end_time': 'End time must be after start time'
                })

            # Calculate duration from time range if provided
            from datetime import datetime, timedelta
            start_dt = datetime.combine(self.date, self.start_time)
            end_dt = datetime.combine(self.date, self.end_time)
            calculated_duration = int((end_dt - start_dt).total_seconds() / 60)

            # Allow some tolerance (±5 minutes)
            if abs(calculated_duration - self.duration) > 5:
                self.duration = calculated_duration

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

from django.db import models

# Create your models here.
