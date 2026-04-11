from django.contrib import admin

from .models import Challenge, UserChallengeProgress, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "current_streak", "longest_streak", "total_points")


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("slug", "category", "title", "points", "time_limit_seconds")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(UserChallengeProgress)
class UserChallengeProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "challenge", "completed", "attempts", "best_time_seconds")
