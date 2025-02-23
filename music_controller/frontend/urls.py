from django.urls import path
from . import views

app_name = "frontend"

urlpatterns = [
    path("", views.index, name=""),
    path("join", views.index),
    path("create", views.index),
    path("room/<str:roomCode>", views.index),
]
