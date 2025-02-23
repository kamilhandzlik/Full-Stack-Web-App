from django.urls import path
from . import views


urlpatterns = [
    path("get-auth-url", views.AuthURL.as_view()),
    path("redirect", views.spotify_callback),
    path("is-authenticated", views.IsAuthenticated.as_view()),
    path("current-song", views.CurrentSong.as_view()),
    path('player/play', views.PlaySong.as_view()),
    path('player/pause', views.PauseSong.as_view()),
]
