from django.urls import path
from . import views


urlpatterns = [path("home", views.RoomView.as_view(), name="home")]
