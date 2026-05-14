"""
Voice pipeline end-to-end test utility.
Tests TTS and the full pipeline using a pre-recorded sample audio if available.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from app.voice.text_to_speech import text_to_speech
from app.voice.audio_utils import validate_audio_file, get_audio_info

# ─── TEST 1: TTS — Kannada ─────────────────────────────────────────
print("\n[TEST 1] Kannada Text-to-Speech")
print("-" * 40)

kannada_answer = (
    "ನಮಸ್ಕಾರ! ನೀವು ಮಂಡ್ಯದಲ್ಲಿ 3 ಎಕರೆ ಜಮೀನು ಹೊಂದಿರುವ ಅಕ್ಕಿ ರೈತರಾಗಿರುವುದರಿಂದ, "
    "ನಿಮಗೆ ಅಕ್ಕಿ ಬೆಳೆ ಯೋಜನೆ ಮತ್ತು ಕೃಷಿ ವಿಕಾಸ ಯೋಜನೆ ಎರಡಕ್ಕೂ ಅರ್ಹತೆ ಇದೆ. "
    "ಅಕ್ಕಿ ಬೆಳೆ ಯೋಜನೆಯಲ್ಲಿ ನಿಮಗೆ ಉಚಿತ ಬೀಜ ಮತ್ತು ಶೇ 30 ರಷ್ಟು ಕೀಟನಾಶಕ ರಿಯಾಯಿತಿ ಸಿಗುತ್ತದೆ."
)

result = text_to_speech(text=kannada_answer, language="kannada")
status = "PASS" if result["success"] else "FAIL"
print(f"  Status: {status}")
if result["success"]:
    print(f"  Audio saved: {result['audio_path']}")
    print(f"  File size: {result.get('file_size_kb', 0)} KB")
else:
    print(f"  Error: {result['error']}")

# ─── TEST 2: TTS — English ─────────────────────────────────────────
print("\n[TEST 2] English Text-to-Speech")
print("-" * 40)

english_answer = (
    "Hello! As a rice farmer with 3 acres in Mandya, "
    "you are eligible for the Akki Bele Yojane scheme which provides free seeds "
    "and up to 30% pesticide discount. You can also apply for PM-KISAN "
    "which gives Rs. 6000 per year directly to your bank account."
)

result_en = text_to_speech(text=english_answer, language="english")
status_en = "PASS" if result_en["success"] else "FAIL"
print(f"  Status: {status_en}")
if result_en["success"]:
    print(f"  Audio saved: {result_en['audio_path']}")
    print(f"  File size: {result_en.get('file_size_kb', 0)} KB")
else:
    print(f"  Error: {result_en['error']}")

# ─── TEST 3: Audio validation ──────────────────────────────────────
print("\n[TEST 3] Audio File Validation")
print("-" * 40)

# Check if sample audio exists
sample_path = "storage/sample_audio"
samples = [f for f in os.listdir(sample_path) if not f.startswith(".")] if os.path.exists(sample_path) else []

if samples:
    test_file = os.path.join(sample_path, samples[0])
    valid, err = validate_audio_file(test_file)
    info = get_audio_info(test_file)
    print(f"  File: {samples[0]}")
    print(f"  Valid: {valid}")
    print(f"  Info: {info}")
else:
    print("  No sample audio files found in storage/sample_audio/")
    print("  Place a .wav or .mp3 file there to test the full voice pipeline.")

print("\n[All tests complete]")
