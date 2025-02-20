from requests import post
from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from decouple import config
from requests import post, put, get


BASE_URL = "https://api.spotify.com/v1/me/"


def get_user_tokens(session_id):
    user_tokens = SpotifyToken.objects.filter(user=session_id)
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None


def update_or_create_user_tokens(
    session_id, access_token, token_type, expires_in, refresh_token
):
    if expires_in is None:
        expires_in = 3600

    tokens = get_user_tokens(session_id)
    expires_at = timezone.now() + timedelta(seconds=expires_in)

    if tokens:
        tokens.access_token = access_token
        tokens.token_type = token_type
        tokens.expires_in = expires_at
        tokens.refresh_token = refresh_token
        tokens.save(
            update_fields=["access_token", "token_type", "expires_in", "refresh_token"]
        )
    else:
        tokens = SpotifyToken(
            user=session_id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
            expires_in=expires_in,
        )
        tokens.save()


def is_spotify_authenticated(session_id):
    tokens = get_user_tokens(session_id)
    if tokens:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            refresh_spotify_token(session_id)

        if not tokens.refresh_token:
            return {"error": "Brak refresh_token, proszę zalogować się ponownie."}  # TODO pamiętaj żeby zmienić a angielski
        

        return True

    return False


def refresh_spotify_token(session_id):
    tokens = get_user_tokens(session_id)

    if not tokens or not tokens.refresh_token:
        print(f"Brak refresh_token dla użytkownika: {session_id}")  # TODO pamiętaj żeby zmienić a angielski
        return {"error": "Brak refresh_token, proszę zalogować się ponownie."}  # TODO pamiętaj żeby zmienić a angielski

    print(f"Refresh token przed odświeżeniem: {tokens.refresh_token}")  # TODO pamiętaj żeby zusunąć

    refresh_token = tokens.refresh_token
    CLIENT_ID = config("CLIENT_ID")
    CLIENT_SECRET = config("CLIENT_SECRET")

    response = post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    ).json()

    print("Spotify API Response:", response)

    if "error" in response:
        print(f"Błąd podczas odświeżania tokena: {response}")  # TODO pamiętaj żeby zmienić a angielski
        return {"error": f"Błąd podczas odświeżania tokena: {response}"}  # TODO pamiętaj żeby zmienić a angielski

    access_token = response.get("access_token")
    token_type = response.get("token_type")
    expires_in = response.get("expires_in")
    new_refresh_token = response.get("refresh_token", refresh_token)  

    print(f"Nowy access_token: {access_token}")   # TODO pamiętaj żeby usunąć
    print(f"Nowy refresh_token: {new_refresh_token}")    # TODO pamiętaj żeby usunąć

    if not access_token:
        print("Nie udało się odświeżyć tokena!")     # TODO pamiętaj żeby zmienić a angielski
        return {"error": "Nie udało się odświeżyć tokena!"}    # TODO pamiętaj żeby zmienić a angielski

    update_or_create_user_tokens(
        session_id, access_token, token_type, expires_in, new_refresh_token
    )
    
    print("Tokeny zaktualizowane w bazie")    # TODO pamiętaj żeby usunąć
    return {"access_token": access_token}



def execute_spotify_api_request(session_id, endpoint, post_=False, put_=False):
    tokens = get_user_tokens(session_id)

    if not tokens or not tokens.access_token:
        return {"error": "No valid access token"}

    header = {
        "Content-type": "application/json",
        "Authorization": "Bearer " + tokens.access_token,
    }

    if post_:
        response = post(BASE_URL + endpoint, headers=header)
    elif put_:
        response = put(BASE_URL + endpoint, headers=header)
    else:
        response = get(BASE_URL + endpoint, headers=header)

    # print("Spotify API Response:", response.status_code, response.text)  #  TODO Usunąć

    try:
        return response.json()
    except Exception as e:
        return {"error": f"Invalid JSON response: {str(e)}"}



def ensure_valid_token(host):
    tokens = SpotifyToken.objects.filter(user=host).first()

    if not tokens:
        return None

    if tokens.expires_in <= timezone.now():  
        refresh_token = tokens.refresh_token
        new_tokens = refresh_spotify_token(refresh_token)

        if new_tokens:
            tokens.access_token = new_tokens["access_token"]
            tokens.expires_in = timezone.now() + timedelta(seconds=new_tokens["expires_in"])
            tokens.save()
        else:
            return None

    return tokens.access_token


def play_song(session_id):
    return execute_spotify_api_request(session_id, 'player/play', put_=True)


def pause_song(sesion_id):
    return execute_spotify_api_request(sesion_id, 'player/pause', put_=True)