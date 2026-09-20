# Haleigh's Music Studio

This folder contains the complete songwriting app we built together.

## Easiest way to start the app

1. Double-click `Start Haleighs Music Studio.command`.
2. If asked, paste the Gemini API key and press Return.
   - The key will stay hidden while you paste it.
   - The key is used only for this Terminal session and is not saved in this folder.
3. Wait for Safari to open the app.

If Safari does not open automatically, visit:

http://localhost:8501

Keep the Terminal window open while using the app. To stop the app, click the Terminal window and press Control+C.

## What each item is

- `app.py` — the visual Streamlit app.
- `song_engine.py` — Gemini lyric review, chord generation, and capo calculations.
- `app_icon.jpeg` — Haleigh's original app artwork.
- `studio_background.png` — the guitar-and-cross background.
- `Saved-Songs` — song files made while testing the app.
- `Learning` — Kaleb's Python lessons and early AI test.
- `Terminal-Version` — the earlier command-line version of the project.
- `requirements.txt` — the Python packages the app needs.

## Current features

- Corrects spelling, grammar, capitalization, and punctuation in lyrics.
- Gives optional songwriting suggestions.
- Places guitar chords above lyric words using Gemini.
- Supports Christian, Country, Rock, and Pop styles.
- Recommends an easy guitar capo position.
- Lets the songwriter edit the finished arrangement.
- Downloads readable text and reusable song-data files.
- Reopens saved song-data files for later editing.
- Includes a confirmed New Song reset.

## Important

Do not put the Gemini API key inside `app.py`, `song_engine.py`, or any file that might later be uploaded to GitHub. The launcher asks for it privately each time it is needed.

The `localhost` link works only on this Mac while the app is running. We can publish the app later when it is finished.

## Hosted app

The deployment-ready files in this folder can be hosted on Streamlit Community Cloud. Once deployed, the app receives a permanent `streamlit.app` address that works while this Mac is off.

- On iPhone or iPad, open the hosted link in Safari, tap Share, and choose **Add to Home Screen**.
- On a PC or Mac, open the hosted link in Chrome or Edge and create an app shortcut from the browser menu.
- Future updates are published from the connected GitHub repository and appear without reinstalling the app.

Saved songs, learning exercises, the local launcher, and API secrets are intentionally excluded from deployment.
