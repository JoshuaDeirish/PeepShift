from django.urls import path
from .views import ChangePinView, LoginView, LogoutView, MeView, UserCreateView, UserDeactivateView, UserListView, UserResetPinView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("auth/change-pin/", ChangePinView.as_view(), name="change-pin"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/create/", UserCreateView.as_view(), name="user-create"),
    path("users/<int:pk>/deactivate/", UserDeactivateView.as_view(), name="user-deactivate"),
    path("users/<int:pk>/reset-pin/", UserResetPinView.as_view(), name="user-reset-pin"),
]