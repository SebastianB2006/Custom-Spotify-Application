# Custom Spotify Application

A lightweight, customized Spotify desktop controller built with Python and Pygame, powered by the Spotipy library and Spotify Web API.

---

## Features

- Playback Controls: Play, pause, skip forward, and previous track.
- Track Progress & Seeking: Real-time track progress bar with click-to-seek support.
- Volume Slider & Mute: Interactive vertical volume slider and mute toggle.
- Playlist Selector: Dropdown menu with mouse wheel scrolling to switch playlists.
- Dynamic Album Art: Automatically fetches and displays current track cover art.
- Custom Image Slideshow: Integrated photo viewer with navigation arrows.

---

## Prerequisites

- Python 3.8+
- Spotify Premium account (required by Spotify API for playback control)
- Dependencies installed via:
  pip install -r requirements.txt

---

## Spotify API Setup

1. Go to the Spotify Developer Dashboard (developer.spotify.com/dashboard) and log in.
2. Click "Create App".
3. Fill in the app name and description.
4. Set the Redirect URI to exactly:
   http://127.0.0.1:8080/callback
5. Save the app settings.
6. Open your app Settings tab and copy your Client ID and Client Secret.

---

## Project Configuration

Open spotifycustom.py and replace the credentials at the top with your own:

CLIENT_ID = "YOUR_CLIENT_ID_HERE"
CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
REDIRECT_URI = "http://127.0.0.1:8080/callback"

---

## Custom Images Slideshow

Drop your images (.jpg, .jpeg, .png) inside the custom_images/ folder. The application automatically crops them to fit and allows cycling through them with the on-screen buttons.

---

## Running the App

1. Ensure Spotify is open and active on at least one device (desktop app, phone, or web player).
2. Run the application:
   python spotifycustom.py
3. On first launch, a browser window will open asking to authorize the app. Grant permissions
