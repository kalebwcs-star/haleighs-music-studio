from google import genai


CAPO_POSITIONS = {
    "C": (0, "C"),
    "D": (0, "D"),
    "E": (0, "E"),
    "F": (1, "E"),
    "G": (0, "G"),
    "A": (2, "G"),
    "B": (4, "G"),
}


def friendly_gemini_error(error, action):
    error_message = str(error).lower()

    if (
        "api key" in error_message
        or "api_key" in error_message
        or "unauthenticated" in error_message
        or "permission denied" in error_message
        or "401" in error_message
        or "403" in error_message
    ):
        return (
            "The Gemini API key is missing or was not accepted. Stop the app, "
            "start it again, and carefully paste the key when Terminal asks for it."
        )

    if "429" in error_message or "quota" in error_message or "resource_exhausted" in error_message:
        return (
            "Gemini's free usage limit has been reached. "
            "Please wait a little while and try again."
        )

    if "503" in error_message or "unavailable" in error_message or "overloaded" in error_message:
        return "Gemini is temporarily busy. Please wait a minute and try again."

    return f"Unable to {action}. Please try again."


def get_capo_recommendation(key, use_capo):
    if not use_capo:
        return 0, key

    return CAPO_POSITIONS[key]


def refine_lyrics(mood, style, lyrics):
    prompt = f"""
You are a careful songwriting editor.

Review these original song lyrics.

Mood: {mood}
Style: {style}

Editing rules:
- Preserve the songwriter's meaning, voice, point of view, and line breaks.
- Correct spelling, capitalization, grammar, and punctuation.
- Make only light wording changes when a line is confusing or unnatural.
- Do not add an entirely new verse or chorus.
- After the refined lyrics, give 2 to 4 optional suggestions about flow, rhyme, imagery, or structure.
- Do not apply the optional suggestions to the lyrics.
- Use the two exact section headings shown below.
- Do not use Markdown code fences.

REFINED LYRICS:
<the complete corrected lyrics>

SUGGESTIONS:
<a short numbered list>

Original lyrics:
{lyrics}
"""

    try:
        client = genai.Client()
        response = client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=prompt,
        )
        result = response.output_text.strip()
        refined_heading = "REFINED LYRICS:"
        suggestions_heading = "SUGGESTIONS:"

        if refined_heading in result and suggestions_heading in result:
            refined_section = result.split(refined_heading, 1)[1]
            refined_lyrics, suggestions = refined_section.split(suggestions_heading, 1)
            return refined_lyrics.strip(), suggestions.strip()

        return lyrics, result
    except Exception as error:
        return None, friendly_gemini_error(error, "review the lyrics")


def suggest_chords(key, mood, style, lyrics, capo_fret, chord_shape_key):
    prompt = f"""
You are a songwriting assistant.

Suggest chords for these original lyrics.

Key: {key}
Mood: {mood}
Style: {style}
Capo fret: {capo_fret}
Chord shapes to use: {chord_shape_key}

Rules:
- Do not change any lyric words.
- The song must sound in the key of {key}.
- Write the chord names the guitarist should physically play with the capo on fret {capo_fret}.
- Build the progression from chord shapes belonging to the key of {chord_shape_key}.
- Place a chord line immediately above each lyric line.
- Position each chord above the word where it should change.
- Only return the lyrics and chord lines.
- Do not include explanations or Markdown formatting.

Lyrics:
{lyrics}
"""

    try:
        client = genai.Client()
        response = client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=prompt,
        )
        return response.output_text
    except Exception as error:
        return friendly_gemini_error(error, "generate chord suggestions")


def transform_song(song_text, instructions, current_key, target_key):
    key_direction = (
        f"Transpose the song to {target_key}."
        if target_key != "Keep current / let AI decide"
        else "Keep the current key unless the user's instructions request a change."
    )
    known_key = (
        f"The song is currently in {current_key}."
        if current_key != "Not sure"
        else "The current key is unknown; infer it from the chords when possible."
    )

    prompt = f"""
You are a practical guitar arrangement editor.

Transform the pasted song according to the user's request.

Current-key information: {known_key}
Target-key instruction: {key_direction}
User's request: {instructions}

Rules:
- Preserve every lyric word and the order of all sections unless the user explicitly asks for lyric changes.
- When transposing, transpose every chord consistently, including slash chords.
- When simplifying, choose common open guitar chords and recommend a capo when that keeps the requested sounding key.
- Keep chord lines immediately above their lyric lines.
- Preserve labels such as Verse, Chorus, Bridge, and Intro.
- If the pasted song has lyrics but no chords, add suitable guitar chords.
- Do not use Markdown code fences.
- Use the two exact headings below.

TRANSFORMED SONG:
<the complete transformed chord-and-lyric sheet>

NOTES:
<a short explanation of the key, capo, and important changes>

Pasted song:
{song_text}
"""

    try:
        client = genai.Client()
        response = client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=prompt,
        )
        result = response.output_text.strip()
        song_heading = "TRANSFORMED SONG:"
        notes_heading = "NOTES:"

        if song_heading in result and notes_heading in result:
            transformed_section = result.split(song_heading, 1)[1]
            transformed_song, notes = transformed_section.split(notes_heading, 1)
            return transformed_song.strip(), notes.strip()

        return result, "Review the transformed arrangement before downloading."
    except Exception as error:
        return None, friendly_gemini_error(error, "transform the song")
