from django.db import models


class SpotifyToken(models.Model):
    user = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    refresh_token = models.CharField(max_length=150, blank=True, null=True)
    access_token = models.CharField(max_length=150, blank=True, null=True)
    expires_in = models.DateTimeField(blank=True, null=True)
    token_type = models.CharField(max_length=50, blank=True, null=True)
