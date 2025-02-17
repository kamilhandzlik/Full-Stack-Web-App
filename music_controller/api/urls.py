from django.urls import path
from . import views


urlpatterns = [
    path("room", views.RoomView.as_view(), name="room"),
    path("create-room", views.CreateRoomView.as_view(), name="create-room"),
    path("get-room", views.GetRoom.as_view()),
    path("join-room", views.JoinRoomView.as_view()),
    path("user-in-room", views.UserInRoom.as_view()),
    path("leave-room", views.LeaveRoom.as_view()),
    path("update-room", views.UpdateRoom.as_view()),
]
