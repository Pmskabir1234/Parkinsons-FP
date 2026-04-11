from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from challenges.models import UserProfile

from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            UserProfile.objects.get_or_create(user=user)
            return Response(
            {"username": user.username, "id": user.id},
            status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        u = request.user
        profile, _ = UserProfile.objects.get_or_create(user=u)
        return Response(
            {
                "username": u.username,
                "email": u.email,
                "current_streak": profile.current_streak,
                "longest_streak": profile.longest_streak,
                "total_points": profile.total_points,
                "last_activity_date": profile.last_activity_date,
            }
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """Same as default; kept for a single import path if we extend later."""

    pass
