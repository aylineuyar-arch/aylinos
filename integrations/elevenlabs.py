"""
AylinOS — ElevenLabs Integration
----------------------------------
Converts STAR story text to audio for interview practice.
Lets Aylin listen to her own prep content out loud — hear how answers sound.

Used by: agents/interview_prep.py (optional audio output)
Env var: ELEVENLABS_API_KEY
"""

import os
import requests
from pathlib import Path

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
BASE_URL = "https://api.elevenlabs.io/v1"

# Rachel — clear, professional female voice
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"


def is_enabled() -> bool:
    return bool(ELEVENLABS_API_KEY)


def text_to_speech(text: str, output_path: str, voice_id: str = DEFAULT_VOICE_ID) -> bool:
    """
    Convert text to MP3 audio file.
    Returns True on success, False on failure (graceful degradation).
    """
    if not is_enabled():
        print("[ElevenLabs] No API key — skipping audio generation")
        return False

    try:
        resp = requests.post(
            f"{BASE_URL}/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "model_id": "eleven_turbo_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                },
            },
            timeout=30,
        )
        if resp.status_code == 200:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(resp.content)
            print(f"[ElevenLabs] Audio saved → {output_path}")
            return True
        else:
            print(f"[ElevenLabs] API error {resp.status_code}: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"[ElevenLabs] Failed: {e}")
        return False


def generate_star_audio(job_id: str, star_stories: str) -> str:
    """
    Generate an audio file from STAR story text for a given job.
    Returns local file path if successful, empty string otherwise.
    """
    if not is_enabled():
        return ""

    # Trim to ~2000 chars to stay within TTS limits per call
    text = star_stories[:2000]
    output_path = f"/tmp/aylinos_prep_{job_id}.mp3"
    success = text_to_speech(text, output_path)
    return output_path if success else ""


def list_voices() -> list:
    """Return available ElevenLabs voices."""
    if not is_enabled():
        return []
    try:
        resp = requests.get(
            f"{BASE_URL}/voices",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            timeout=10,
        )
        return resp.json().get("voices", [])
    except Exception as e:
        print(f"[ElevenLabs] Failed to list voices: {e}")
        return []
