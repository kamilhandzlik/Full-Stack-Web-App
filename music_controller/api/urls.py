from django.urls import path
from . import views


urlpatterns = [
    path("home", views.RoomView.as_view(), name="home"),
    path("create-room", views.CreateRoomView.as_view(), name="create-room"),
]
