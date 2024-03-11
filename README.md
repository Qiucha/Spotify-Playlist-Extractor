# Spotify-Playlist-Extractor
For someone who wants the information of one's own playlists.

## Usage
To Extract the information below:
- Information of Favorite Tracks/Episodes, including:
    - Track Name
    - Artists Name (could be more than one artist)
    - Artists Type
    - Album Type
    - Album Name
    - Disc Number
    - Track Number
    - Durations_ms (literally track duration in milliseconds)
    - uri (spotify_api)
- Playlists Information, including: 
    - playlist id (spotify_api)
    - playlist name
    - number of tracks in playlists
    - type of playlists (spotify_api)
- Information of Tracks in the Playlists Extracted Above:
    Including the exact same information as favorite tracks.

## Before You Run, A Few Setup Steps
### Step 1
Head to [Spotify Developer Page](https://developer.spotify.com/).
Sign in with your spotify account, create a app with information below:
- App name: Feel Free to use whatever you want
- App Description: Feel Free to fill in whatever you want
- Redirect URIs: `http://localhost:5000/callback` **IMPORTANT**

* note that you can use other port, just make sure you also alter the port used in `main.py`.


### Step 2
Create a file with file name `.env` under the same directory as `main.py`:
Which should contain the information below:
```
SECRET_KEY="random strings"
CLIENT_ID="get this from spotify development dashboard"
CLIENT_SECRET="get this from spotify development dashboard"
```

### Step 3
Make sure you have python installed with packages below:
- flask
- datetime
- dotenv
- pandas
- urllib.parse
- requests
You could use `pip install 'package name'` to install them.

## How to
### Step 1
After the Setup Steps, head to the directory and run `main.py` with:
```python main.py```
or probably `python3 main.py` in some cases.

### Step 2
If the script run successfully, there should be some messages like:
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://***.***.***.***:5000
Press CTRL+C to quit
 * Restarting with watchdog (fsevents)
 * Debugger is active!
```
Than head to your browser by `ctrl+click` the `http://127.0.0.1:5000` link (if possible),
or open you browser and key in `http://127.0.0.1:5000` manually.

* note that if you've changed the port been used, the link should use different port.

### Step 3
If the browser shows up with:
`Welcome to Spotify playlist extractor, plz login first! login in with spotify`
Click the `login with spotify` link, which would redirect to spotify login page.
Check the user information which would be read by the program, agree with your own risks!

### Step 4
Wait for a few seconds to probably few minute until the browser pops up with `all done!` message.
The process time depends on the size of your playlists.

#### If Something Went Wrong
There should be some kind of error message, feel free to issue with your own error message.

### Step 5
Head to the directory of the `main.py` there should be a `csv` folder now.
ALL the extracted information would be in that folder.

## Why Extractor?
Actually, what I initially planned to write was something tranfer all my playlists and favorite/saved tracks from Spotify to Apple Music.
However the Apple Music API (MusicKit) costs several thousand NTD for a year......
Which is kind of ridiculous to pay for one-time activity.
AND I FOUND OUT THE PRICING AFTER I FINISHED THE CODING PART OF SPOTIFY API. LUL......
That's why......
Huh......

## Reference
- [Spotify for Development - Web API](https://developer.spotify.com/documentation/web-api)
- [Spotify API OAuth - Automate Getting User Playlists (Complete Tutorial)](https://youtu.be/olY_2MW4Eik?feature=shared)
- [Flask Documentation](https://flask.palletsprojects.com/en/2.3.x/)