from django.contrib import admin
from .models import Workout


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'workout_type', 'workout_date',
        'duration', 'calories_burned', 'status', 'created_at'
    ]
    list_filter = ['workout_type', 'status', 'intensity', 'workout_date']
    search_fields = ['title', 'description', 'user__email']
    date_hierarchy = 'workout_date'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'workout_type', 'title', 'description')
        }),
        ('Workout Details', {
            'fields': (
                'duration', 'calories_burned', 'distance',
                'intensity', 'status'
            )
        }),
        ('Dates & Times', {
            'fields': (
                'workout_date', 'started_at', 'completed_at',
                'created_at', 'updated_at'
            )
        }),
        ('Additional Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


from django.contrib import admin

# Register your models here.
