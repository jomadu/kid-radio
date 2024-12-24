import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import ADC_Library  # Replace with the actual ADC library you're using
import os  # For static noise playback

# Configuration for Spotify
SPOTIFY_CLIENT_ID = "<your_client_id>"
SPOTIFY_CLIENT_SECRET = "<your_client_secret>"
SPOTIFY_REDIRECT_URI = "<your_redirect_uri>"

# Constants
ADC_CHANNEL = 0
POLL_INTERVAL = 0.5
STATIC_FILE = "/path/to/static_noise.mp3"  # Replace with the path to your static noise file
MIN_ADC_VALUE = 0  # Minimum ADC value when knob is at the start
MAX_ADC_VALUE = 1023  # Maximum ADC value when knob is at the end
MIN_STATION = 88.1  # Minimum radio station frequency
MAX_STATION = 107.9  # Maximum radio station frequency
STATION_STEP = 0.2  # Frequency step size for stations (e.g., 88.1, 88.3, 88.5, etc.)
STATIC_THRESHOLD = 0.1  # Tolerance to detect "in-between" static zones

# Initialize ADC and Spotify client
def initialize_system():
    adc = ADC_Library.ADC()  # Replace with actual ADC initialization code
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="user-modify-playback-state,user-read-playback-state"
    ))
    return adc, sp

# Map ADC value to a station frequency
def calculate_station(adc_value):
    # Map ADC value to a floating-point station frequency
    normalized_value = (adc_value - MIN_ADC_VALUE) / (MAX_ADC_VALUE - MIN_ADC_VALUE)
    frequency = MIN_STATION + normalized_value * (MAX_STATION - MIN_STATION)
    # Round to the nearest valid station frequency
    rounded_station = round(frequency / STATION_STEP) * STATION_STEP
    return rounded_station

# Determine if the current station is valid or static
def get_station_or_static(station):
    # Calculate the fractional difference to the nearest valid station
    nearest_station = round(station / STATION_STEP) * STATION_STEP
    if abs(station - nearest_station) < STATIC_THRESHOLD:
        return nearest_station
    return None

# Play static noise
def play_static():
    os.system(f"mpg123 {STATIC_FILE}")  # Replace with your preferred playback method

# Play a playlist by station name
def play_station(sp, station):
    station_name = f"{station:.1f}"  # Format station as a string (e.g., "88.1")
    # Search for the playlist by name
    results = sp.search(q=f"playlist:{station_name}", type="playlist", limit=1)
    if results['playlists']['items']:
        playlist_uri = results['playlists']['items'][0]['uri']
        sp.start_playback(context_uri=playlist_uri)

# Main program loop
def main():
    adc, sp = initialize_system()
    last_station = None

    while True:
        # Read the ADC value from the potentiometer
        adc_value = adc.read(ADC_CHANNEL)
        current_station = calculate_station(adc_value)
        valid_station = get_station_or_static(current_station)

        # Switch to a station or play static if station changes
        if valid_station != last_station:
            last_station = valid_station
            if valid_station:
                print(f"Tuning to station: {valid_station:.1f}")
                play_station(sp, valid_station)
            else:
                print("Static noise...")
                play_static()

        # Sleep before the next poll
        time.sleep(POLL_INTERVAL)

# Run the program
if __name__ == "__main__":
    main()
