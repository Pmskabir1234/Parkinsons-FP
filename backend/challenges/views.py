from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Challenge, UserChallengeProgress, UserProfile
from .serializers import (
    ChallengeDetailSerializer,
    ChallengeListSerializer,
    ProgressSerializer,
)
from .streaks import apply_daily_streak
from .validators import validate_submission


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Challenge.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self) -> type:
        if self.action == "retrieve":
            return ChallengeDetailSerializer
        return ChallengeListSerializer

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        challenge = self.get_object()
        payload = request.data
        time_elapsed = payload.get("time_elapsed_seconds")
        try:
            time_elapsed = float(time_elapsed)
        except (TypeError, ValueError):
            return Response(
                {"ok": False, "detail": "time_elapsed_seconds is required (number)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if time_elapsed > challenge.time_limit_seconds:
            return Response(
                {
                    "ok": False,
                    "detail": "Time limit exceeded for this challenge.",
                    "time_limit_seconds": challenge.time_limit_seconds,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if time_elapsed < 0:
            return Response(
                {"ok": False, "detail": "Invalid time."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ok, message = validate_submission(challenge.validator, payload)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        progress, _ = UserChallengeProgress.objects.get_or_create(
            user=request.user,
            challenge=challenge,
        )
        progress.attempts += 1
        progress.last_attempt_at = timezone.now()
        was_first_completion = not progress.completed

        if ok:
            progress.completed = True
            if progress.best_time_seconds is None:
                progress.best_time_seconds = time_elapsed
            else:
                progress.best_time_seconds = min(progress.best_time_seconds, time_elapsed)
            if was_first_completion:
                profile.total_points += challenge.points
                profile.save(update_fields=["total_points"])
                apply_daily_streak(profile)
        progress.save()

        return Response(
            {
                "ok": ok,
                "message": message,
                "completed": progress.completed,
                "attempts": progress.attempts,
                "best_time_seconds": progress.best_time_seconds,
                "total_points": profile.total_points,
                "current_streak": profile.current_streak,
                "longest_streak": profile.longest_streak,
            },
            status=status.HTTP_200_OK,
        )


class DashboardView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        challenges = Challenge.objects.all()
        total = challenges.count()
        completed = UserChallengeProgress.objects.filter(
            user=request.user,
            completed=True,
        ).count()
        progress_rows = UserChallengeProgress.objects.filter(user=request.user).select_related(
            "challenge"
        )
        return Response(
            {
                "username": request.user.username,
                "current_streak": profile.current_streak,
                "longest_streak": profile.longest_streak,
                "total_points": profile.total_points,
                "last_activity_date": profile.last_activity_date,
                "challenges_total": total,
                "challenges_completed": completed,
                "progress": ProgressSerializer(progress_rows, many=True).data,
            }
        )


class PublicChallengeMetaView(APIView):
    """Unauthenticated list of categories and counts (for landing page)."""

    permission_classes = (AllowAny,)

    def get(self, request):
        qs = Challenge.objects.all()
        by_cat = {}
        for c in Challenge.Category.values:
            by_cat[c] = qs.filter(category=c).count()
        return Response(
            {
                "categories": Challenge.Category.choices,
                "counts_by_category": by_cat,
                "total": qs.count(),
            }
        )
