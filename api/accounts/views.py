from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, get_object_or_404
from .permissions import IsManagerOrAdmin, PinIsCurrent
from .serializers import UserCreateSerializer
from .utils import generate_initial_pin
from .serializers import ChangePinSerializer, LoginSerializer, UserSerializer

User = get_user_model()


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ChangePinView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChangePinSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        return Response(
            {"token": token.key, "user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)



class UserCreateView(CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [IsAuthenticated, PinIsCurrent, IsManagerOrAdmin]


class UserListView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, PinIsCurrent, IsManagerOrAdmin]

    def get_queryset(self):
        location_ids = self.request.user.location_links.values_list(
            "location_id", flat=True
        )
        return (
            User.objects.filter(location_links__location_id__in=location_ids)
            .distinct()
            .prefetch_related("location_links__location")
        )


class UserDeactivateView(APIView):
    permission_classes = [IsAuthenticated, PinIsCurrent, IsManagerOrAdmin]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if user == request.user:
            return Response(
                {"detail": "You cannot deactivate yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = False
        user.save(update_fields=["is_active"])
        Token.objects.filter(user=user).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserResetPinView(APIView):
    permission_classes = [IsAuthenticated, PinIsCurrent, IsManagerOrAdmin]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        pin = generate_initial_pin(user.first_name, user.last_name, user.phone)
        user.set_password(pin)
        user.must_change_pin = True
        user.save(update_fields=["password", "must_change_pin"])
        Token.objects.filter(user=user).delete()

        return Response({"initial_pin": pin}, status=status.HTTP_200_OK)