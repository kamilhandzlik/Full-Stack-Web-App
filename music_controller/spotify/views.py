from django.shortcuts import redirect, render
from decouple import config
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from api.models import Room
from .util import *


class AuthURL(APIView):
    def get(self, request, format=None):
        scopes = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
        REDIRECT_URI = config("REDIRECT_URI")
        CLIENT_ID = config("CLIENT_ID")
        url = (
            Request(
                "GET",
                "https://accounts.spotify.com/authorize",
                params={
                    "scope": scopes,
                    "response_type": "code",
                    "redirect_uri": REDIRECT_URI,
                    "client_id": CLIENT_ID,
                },
            )
            .prepare()
            .url
        )

        return Response({"url": url}, status=status.HTTP_200_OK)


def spotify_callback(request, format=None):
    code = request.GET.get("code")
    error = request.GET.get("error")
    REDIRECT_URI = config("REDIRECT_URI")
    CLIENT_ID = config("CLIENT_ID")
    CLIENT_SECRET = config("CLIENT_SECRET")

    response = post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    ).json()

    access_token = response.get("access_token")
    token_type = response.get("token_type")
    refresh_token = response.get("refresh_token")
    expires_in = response.get("expires_in")
    error = response.get("error")

    if not expires_in:
        expires_in = 3600

    if not request.session.exists(request.session.session_key):
        request.session.create()

 
    update_or_create_user_tokens(
        request.session.session_key, access_token, token_type, expires_in, refresh_token
    )

    return redirect("frontend:")



class IsAuthenticated(APIView):
    def get(self, request, format=None):
        auth_response = is_spotify_authenticated(self.request.session.session_key)

        if isinstance(auth_response, dict) and "error" in auth_response:
            return Response(auth_response, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": True}, status=status.HTTP_200_OK)

class CurrentSong(APIView):
    def get(self, request, format=None):
        room_code = self.request.session.get("room_code")
        room = Room.objects.filter(code=room_code).first()

        if not room:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        host = room.host
        access_token = ensure_valid_token(host)

        if not access_token:
            return Response({"error": "Brak ważnego tokena Spotify"}, status=status.HTTP_401_UNAUTHORIZED)

        endpoint = "player/currently-playing"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = get(f"https://api.spotify.com/v1/{endpoint}", headers=headers).json()

        if "error" in response:
            return Response({"error": response["error"]["message"]}, status=response["error"]["status"])

        if "item" not in response:
            return Response({"error": "Brak aktywnego utworu"}, status=status.HTTP_204_NO_CONTENT)

        item = response["item"]
        song = {
            "title": item["name"],
            "artist": ", ".join(artist["name"] for artist in item["artists"]),
            "duration": item["duration_ms"],
            "time": response.get("progress_ms", 0),
            "image_url": item["album"]["images"][0]["url"],
            "is_playing": response.get("is_playing", False),
            "id": item["id"],
        }

        return Response(song, status=status.HTTP_200_OK)