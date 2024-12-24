import json
import time
from typing import Dict
import os  # For static noise playback
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StationFailedToPlay(RuntimeError):
    def __init__(self, msg):
        super().__init__(msg)

# Utility Functions

def calculate_station(adc_value: int, min_adc_value: int, max_adc_value: int, min_station: float, max_station: float, station_step: float) -> float:
    """
    Map ADC value to a floating-point station frequency.
    """
    normalized_value = (adc_value - min_adc_value) / (max_adc_value - min_adc_value)
    frequency = min_station + normalized_value * (max_station - min_station)
    return round(frequency / station_step) * station_step

def try_get_station(station: float, station_step: float, static_threshold: float) -> float:
    """
    Determine if the current station is valid or static.
    """
    nearest_station = round(station / station_step) * station_step
    if abs(station - nearest_station) < static_threshold:
        return nearest_station
    return None

def play_static(static_file: str):
    """
    Play static noise.
    """
    os.system(f"aplay {static_file}")

def play_station(sp: spotipy.Spotify, station: float, station_uri_cache: Dict[str, str]):
    """
    Play a playlist corresponding to the given station frequency.
    """
    station_name = f"{station:.1f}"
    if station_name in station_uri_cache:
        try:
            sp.start_playback(context_uri=station_uri_cache[station_name])
        except Exception:
            station_uri_cache.pop(station_name)
            raise StationFailedToPlay(f"Unable to play station: {station_name}")
    else:
        results = sp.search(q=f"playlist:{station_name}", type="playlist", limit=1)
        if results['playlists']['items']:
            playlist_uri = results['playlists']['items'][0]['uri']
            station_uri_cache[station_name] = playlist_uri
            try:
                sp.start_playback(context_uri=playlist_uri)
            except Exception:
                raise StationFailedToPlay(f"Unable to play station: {station_name}")

def read_config(file_path: str) -> Dict:
    """
    Read configuration from a JSON file.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Config file '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file '{file_path}'. Error: {e}")
        return None

def get_env_variable(var_name: str) -> str:
    """
    Retrieve an environment variable or raise an error if not found.
    """
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
    return value

# Main Functionality

def main():
    """
    Main program loop.
    """
    # Replace ADC with the actual ADC library you're using
    adc = ADC()

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=get_env_variable("SPOTIFY_CLIENT_ID"),
        client_secret=get_env_variable("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=get_env_variable("SPOTIFY_REDIRECT_URI"),
        scope="user-modify-playback-state,user-read-playback-state"
    ))

    config = read_config("kid-radio-config.json")
    if config is None:
        return

    last_station = None
    station_uri_cache = {}

    while True:
        adc_value = adc.read(config['adc_channel'])
        current_station = calculate_station(
            adc_value,
            config['min_adc_value'],
            config['max_adc_value'],
            config['min_station'],
            config['max_station'],
            config['station_step']
        )

        station = try_get_station(
            current_station,
            config['station_step'],
            config['static_threshold']
        )

        if station != last_station:
            last_station = station
            if station:
                print(f"Tuning to station: {station:.1f}")
                try:
                    play_station(sp, station, station_uri_cache)
                except StationFailedToPlay as e:
                    print(e)
            else:
                print("Static noise...")
                play_static(config['static_file'])

        time.sleep(config['poll_interval'])

if __name__ == "__main__":
    main()
