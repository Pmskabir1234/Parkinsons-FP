from datetime import date, timedelta
from typing import Optional

from django.utils import timezone

from .models import UserProfile


def apply_daily_streak(profile: UserProfile, when: Optional[date] = None) -> None:
    today = when or timezone.now().date()
    last = profile.last_activity_date
    if last is None:
        profile.current_streak = 1
    elif last == today:
        pass
    elif last == today - timedelta(days=1):
        profile.current_streak += 1
    else:
        profile.current_streak = 1
    profile.last_activity_date = today
    if profile.current_streak > profile.longest_streak:
        profile.longest_streak = profile.current_streak
    profile.save(
        update_fields=[
            "current_streak",
            "longest_streak",
            "last_activity_date",
        ]
    )
