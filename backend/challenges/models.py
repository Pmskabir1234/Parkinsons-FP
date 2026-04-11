from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    total_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} profile"


class Challenge(models.Model):
    class Category(models.TextChoices):
        BUG_FIX = "bug_fix", "Bug fix"
        CODE_CHALLENGE = "code_challenge", "Code challenge"
        DEV_SCENARIO = "dev_scenario", "Dev scenario"

    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=32, choices=Category.choices)
    title = models.CharField(max_length=200)
    description = models.TextField()
    starter_code = models.TextField(blank=True, default="")
    time_limit_seconds = models.PositiveIntegerField(default=300)
    points = models.PositiveIntegerField(default=10)
    validator = models.JSONField(default=dict)

    class Meta:
        ordering = ["category", "id"]

    def __str__(self):
        return self.title


class UserChallengeProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="challenge_progress")
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="progress")
    completed = models.BooleanField(default=False)
    best_time_seconds = models.FloatField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "challenge")

    def __str__(self):
        return f"{self.user.username} / {self.challenge.slug}"
