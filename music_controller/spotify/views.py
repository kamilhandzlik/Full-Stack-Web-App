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
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        host = room.host
        access_token = ensure_valid_token(host)
        if not access_token:
            return Response({"error": "Brak ważnego tokena Spotify"}, status=status.HTTP_401_UNAUTHORIZED) # TODO pamiętaj żeby zmienić a angielski

        # print(f"Access Token: {access_token}") # TODO Pamiętaj żeby usunąć!!
        
        endpoint = "player/currently-playing"
        response = execute_spotify_api_request(host, endpoint)

        if 'error' in response or 'item' not in response:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        item = response.get('item')
        duration = item.get('duration_ms')
        progress = response.get('progress_ms')
        album_cover = item.get('album').get('images')[0].get('url')
        is_playing = response.get('is_playing')
        song_id = item.get('id')

        artist_string = ""

        for i, artist in enumerate(item.get('artists')):
            if i > 0:
                artist_string += ", "
            name = artist.get('name')
            artist_string += name

        song = {
            'title': item.get('name'),
            'artist': artist_string,
            'duration': duration,
            'time': progress,
            'image_url': album_cover,
            'is_playing': is_playing,
            'votes': 0,
            'id': song_id
        }

        return Response(song, status=status.HTTP_200_OK)


class PauseSong(APIView):
    def put(self, request, format=None):
        room_code = self.request.session.get('room_code')
        if not room_code:
            return Response({"error": "Room code not found in session"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = Room.objects.get(code=room_code)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        if self.request.session.session_key == room.host or room.guest_can_pause:
            print(f"Pausing song for host: {room.host}")
            response = pause_song(room.host)
            print("Spotify API response:", response)  # LOGOWANIE odpowiedzi od Spotify
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        return Response({}, status=status.HTTP_403_FORBIDDEN)



class PlaySong(APIView):
    def put(self, request, format=None):
        room_code = self.request.session.get('room_code')
        if not room_code:
            return Response({"error": "Room code not found in session"}, status=status.HTTP_400_BAD_REQUEST)
        
        room = Room.objects.filter(code=room_code)[0]
        if self.request.session.session_key == room.host or room.guest_can_pause:
            play_song(room.host)
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        return Response({}, status=status.HTTP_403_FORBIDDEN)