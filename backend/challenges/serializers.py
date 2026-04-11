from rest_framework import serializers

from .models import Challenge, UserChallengeProgress


def public_validator(validator: dict) -> dict:
    kind = validator.get("kind")
    if kind == "mcq":
        return {
            "kind": "mcq",
            "options": validator.get("options") or [],
            "prompt": validator.get("prompt", ""),
        }
    if kind == "text_match":
        return {
            "kind": "text_match",
            "prompt": validator.get("prompt", ""),
            "hint": validator.get("hint", ""),
        }
    if kind == "python_io":
        return {"kind": "python_io", "language": validator.get("language", "python")}
    return {"kind": kind or "unknown"}


class ChallengeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = (
            "id",
            "slug",
            "category",
            "title",
            "description",
            "time_limit_seconds",
            "points",
        )


class ChallengeDetailSerializer(serializers.ModelSerializer):
    public_validator = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = (
            "id",
            "slug",
            "category",
            "title",
            "description",
            "starter_code",
            "time_limit_seconds",
            "points",
            "public_validator",
        )

    def get_public_validator(self, obj):
        return public_validator(obj.validator or {})


class ProgressSerializer(serializers.ModelSerializer):
    challenge_id = serializers.IntegerField(source="challenge.id", read_only=True)
    challenge_slug = serializers.CharField(source="challenge.slug", read_only=True)
    challenge_title = serializers.CharField(source="challenge.title", read_only=True)
    category = serializers.CharField(source="challenge.category", read_only=True)

    class Meta:
        model = UserChallengeProgress
        fields = (
            "challenge_id",
            "challenge_slug",
            "challenge_title",
            "category",
            "completed",
            "best_time_seconds",
            "attempts",
            "last_attempt_at",
        )
        read_only_fields = fields
