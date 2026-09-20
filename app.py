import base64
import hashlib
import json
from pathlib import Path

import streamlit as st

from song_engine import get_capo_recommendation, refine_lyrics, suggest_chords

st.set_page_config(
    page_title="Haleigh's Music Studio",
    page_icon="app_icon.jpeg",
    layout="centered",
)

background_bytes = Path("studio_background.png").read_bytes()
background_image = base64.b64encode(background_bytes).decode("utf-8")

page_styles = (
    """
    <style>
    :root {
        --studio-pink: #ec4f92;
        --studio-coral: #f47a67;
        --studio-ink: #24212a;
        --studio-paper: #fffafd;
    }

    .stApp {
        background-image:
            linear-gradient(rgba(247, 243, 246, 0.58), rgba(247, 243, 246, 0.64)),
            url("data:image/png;base64,__BACKGROUND_IMAGE__"),
            radial-gradient(circle at 8% 5%, rgba(244, 122, 103, 0.16), transparent 24rem),
            radial-gradient(circle at 92% 12%, rgba(236, 79, 146, 0.14), transparent 26rem);
        background-color: #f7f3f6;
        background-position: center, center center, left top, right top;
        background-repeat: no-repeat;
        background-size: cover, contain, auto, auto;
        background-attachment: fixed;
        color: var(--studio-ink);
    }

    .block-container {
        max-width: 820px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    [data-testid="stImage"] img {
        border-radius: 24px;
        box-shadow: 0 10px 28px rgba(91, 48, 72, 0.18);
    }

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-baseweb="select"] > div,
    [data-testid="stFileUploaderDropzone"] {
        background-color: var(--studio-paper);
        border-radius: 14px;
    }

    [data-testid="stTextArea"] textarea {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        line-height: 1.55;
    }

    [data-testid="stButton"] button[kind="primary"] {
        min-height: 3.25rem;
        border: 0;
        border-radius: 16px;
        background: linear-gradient(120deg, var(--studio-pink), var(--studio-coral));
        box-shadow: 0 8px 20px rgba(236, 79, 146, 0.24);
        font-weight: 700;
    }

    [data-testid="stButton"] button[kind="secondary"] {
        border: 1px solid rgba(236, 79, 146, 0.45);
        border-radius: 14px;
        background: var(--studio-paper);
        color: var(--studio-ink);
        font-weight: 650;
    }

    [data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: var(--studio-pink);
        color: var(--studio-pink);
    }

    [data-testid="stDownloadButton"] button {
        border: 1px solid rgba(236, 79, 146, 0.45);
        border-radius: 14px;
        background: var(--studio-paper);
    }

    [data-testid="stAlert"] {
        border-radius: 14px;
    }

    h1, h2, h3, h4 {
        color: var(--studio-ink);
        letter-spacing: -0.02em;
    }

    @media (max-width: 640px) {
        .block-container {
            padding: 1rem 1rem 3rem;
        }

        h1 {
            font-size: 2rem !important;
        }
    }
    </style>
    """
).replace("__BACKGROUND_IMAGE__", background_image)

st.markdown(
    page_styles,
    unsafe_allow_html=True,
)

logo_column, heading_column = st.columns([1, 4], vertical_alignment="center")

with logo_column:
    st.image("app_icon.jpeg", width=115)

with heading_column:
    st.title("Haleigh's Music Studio")
    st.caption("Turn your lyrics into a guitar-ready chord arrangement.")

st.divider()

new_song_spacer, new_song_column = st.columns([3, 1])

with new_song_column:
    if st.button("New Song", use_container_width=True):
        st.session_state["confirm_new_song"] = True

if st.session_state.get("confirm_new_song"):
    st.warning("Start a new song? Any changes that have not been downloaded will be lost.")
    confirm_column, cancel_column = st.columns(2)

    with confirm_column:
        if st.button("Yes, start over", type="primary", use_container_width=True):
            keys_to_clear = [
                "song_result",
                "arrangement_editor",
                "loaded_file_fingerprint",
                "saved_song_uploader",
                "song_title_input",
                "mood_input",
                "key_input",
                "style_input",
                "use_capo_input",
                "lyrics_input",
                "refined_lyrics",
                "refined_lyrics_editor",
                "lyric_suggestions",
                "pending_lyrics",
                "confirm_new_song",
            ]

            for state_key in keys_to_clear:
                st.session_state.pop(state_key, None)

            st.rerun()

    with cancel_column:
        if st.button("Keep this song", use_container_width=True):
            st.session_state["confirm_new_song"] = False
            st.rerun()

with st.expander("Open a saved song"):
    saved_song_file = st.file_uploader(
        "Song data file",
        type=["json"],
        help="Choose a song data file previously downloaded from this app.",
        label_visibility="collapsed",
        key="saved_song_uploader",
    )

if saved_song_file is not None:
    file_bytes = saved_song_file.getvalue()
    file_fingerprint = hashlib.sha256(file_bytes).hexdigest()

    if st.session_state.get("loaded_file_fingerprint") != file_fingerprint:
        try:
            loaded_song = json.loads(file_bytes.decode("utf-8"))
            required_fields = {
                "title",
                "mood",
                "key",
                "style",
                "original_lyrics",
                "suggested_arrangement",
            }

            if not required_fields.issubset(loaded_song):
                raise ValueError("This file is missing song information.")

            loaded_song.setdefault("capo_fret", 0)
            loaded_song.setdefault("chord_shape_key", loaded_song["key"])

            st.session_state["song_result"] = loaded_song
            st.session_state["arrangement_editor"] = loaded_song["suggested_arrangement"]
            st.session_state["loaded_file_fingerprint"] = file_fingerprint
            st.success(f"Opened {loaded_song['title']}.")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError) as error:
            st.error(f"That song file could not be opened: {error}")

st.subheader("Create a new arrangement")
song_title = st.text_input(
    "Song title",
    placeholder="Enter the name of the song",
    key="song_title_input",
)

left_column, right_column = st.columns(2)

with left_column:
    mood = st.selectbox(
        "Mood",
        ["Happy", "Sad"],
        key="mood_input",
    )

with right_column:
    key = st.selectbox(
        "Musical key",
        ["C", "D", "E", "F", "G", "A", "B"],
        key="key_input",
    )

style = st.selectbox(
    "Music style",
    ["Christian", "Country", "Rock", "Pop"],
    key="style_input",
)

use_capo = st.checkbox(
    "Recommend an easy capo position",
    value=True,
    help="The song will still sound in your chosen key, but the chords may be easier to play.",
    key="use_capo_input",
)

if "pending_lyrics" in st.session_state:
    st.session_state["lyrics_input"] = st.session_state.pop("pending_lyrics")

lyrics = st.text_area(
    "Lyrics",
    placeholder="Write or paste the lyrics here...",
    height=300,
    key="lyrics_input",
)

polish_button = st.button(
    "Polish Lyrics & Give Suggestions",
    use_container_width=True,
)

if polish_button:
    if not lyrics.strip():
        st.warning("Please enter some lyrics first.")
    else:
        with st.spinner("Reviewing spelling, punctuation, and song flow..."):
            refined_lyrics, lyric_suggestions = refine_lyrics(
                mood=mood.lower(),
                style=style,
                lyrics=lyrics,
            )

        if refined_lyrics is None:
            st.error(lyric_suggestions)
        else:
            st.session_state["refined_lyrics"] = refined_lyrics
            st.session_state["refined_lyrics_editor"] = refined_lyrics
            st.session_state["lyric_suggestions"] = lyric_suggestions

if "refined_lyrics" in st.session_state:
    st.subheader("Lyric review")
    st.caption("Read and edit Gemini's corrected version before using it in the song.")

    polished_lyrics = st.text_area(
        "Polished lyrics",
        key="refined_lyrics_editor",
        height=300,
    )

    st.markdown("**Optional songwriting suggestions**")
    st.info(st.session_state["lyric_suggestions"])

    if st.button("Use polished lyrics", use_container_width=True):
        st.session_state["pending_lyrics"] = polished_lyrics
        st.session_state["refined_lyrics"] = polished_lyrics
        st.rerun()

suggest_button = st.button(
    "Suggest Chords",
    type="primary",
    use_container_width=True
)

if suggest_button:
    if not song_title.strip():
        st.warning("Please enter a song title.")
    elif not lyrics.strip():
        st.warning("Please enter some lyrics.")
    else:
        capo_fret, chord_shape_key = get_capo_recommendation(key, use_capo)

        with st.spinner("Finding chords for your lyrics..."):
            suggested_song = suggest_chords(
                key=key,
                mood=mood.lower(),
                style=style,
                lyrics=lyrics,
                capo_fret=capo_fret,
                chord_shape_key=chord_shape_key,
            )

        st.session_state["song_result"] = {
            "title": song_title,
            "mood": mood,
            "key": key,
            "style": style,
            "capo_fret": capo_fret,
            "chord_shape_key": chord_shape_key,
            "original_lyrics": lyrics,
            "suggested_arrangement": suggested_song,
        }
        st.session_state["arrangement_editor"] = suggested_song

if "song_result" in st.session_state:
    song = st.session_state["song_result"]
    safe_title = song["title"].strip().replace(" ", "_") or "song"

    st.subheader(f"Suggested arrangement for {song['title']}")
    if song["capo_fret"] == 0:
        st.info(f"No capo needed — play in {song['chord_shape_key']}.")
    else:
        st.info(
            f"Put the capo on fret {song['capo_fret']} and play "
            f"{song['chord_shape_key']}-shaped chords. The song will sound in {song['key']}."
        )
    st.caption("Edit any chord or move it above a different word before downloading.")

    edited_arrangement = st.text_area(
        "Chord arrangement",
        key="arrangement_editor",
        height=320,
        label_visibility="collapsed",
    )
    song["suggested_arrangement"] = edited_arrangement
    st.session_state["song_result"] = song

    text_download = (
        f"Song: {song['title']}\n"
        f"Mood: {song['mood']}\n"
        f"Key: {song['key']}\n"
        f"Style: {song['style']}\n\n"
        f"Capo fret: {song['capo_fret']}\n"
        f"Chord shapes: {song['chord_shape_key']}\n\n"
        f"{song['suggested_arrangement']}"
    )
    json_download = json.dumps(song, indent=4)

    text_column, json_column = st.columns(2)

    with text_column:
        st.download_button(
            "Download readable song",
            data=text_download,
            file_name=f"{safe_title}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with json_column:
        st.download_button(
            "Download song data",
            data=json_download,
            file_name=f"{safe_title}.json",
            mime="application/json",
            use_container_width=True,
        )
