"""
Test TTS pipeline directly without needing an audio file.
Generates a Kannada MP3 response and saves it to storage/output_audio/.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from app.voice.text_to_speech import text_to_speech

# Kannada test text — a realistic scheme response
kannada_text = (
    "ನಮಸ್ಕಾರ! ನೀವು ಮಂಡ್ಯದಲ್ಲಿ 3 ಎಕರೆ ಜಮೀನು ಹೊಂದಿರುವ ಅಕ್ಕಿ ರೈತರಾಗಿರುವುದರಿಂದ, "
    "ನಿಮಗೆ ಅಕ್ಕಿ ಬೆಳೆ ಯೋಜನೆ ಮತ್ತು ಕೃಷಿ ವಿಕಾಸ ಯೋಜನೆ ಎರಡಕ್ಕೂ ಅರ್ಹತೆ ಇದೆ. "
    "ಅಕ್ಕಿ ಬೆಳೆ ಯೋಜನೆಯಲ್ಲಿ ನಿಮಗೆ ಉಚಿತ ಬೀಜ ಮತ್ತು ಶೇ 30 ರಷ್ಟು ಕೀಟನಾಶಕ ರಿಯಾಯಿತಿ ಸಿಗುತ್ತದೆ. "
    "ಕೃಷಿ ವಿಕಾಸ ಯೋಜನೆಯಲ್ಲಿ ಶೇ 50 ರಷ್ಟು ಗೊಬ್ಬರ ಸಹಾಯಧನ ಮತ್ತು ಪ್ರತಿ ಎಕರೆಗೆ 5000 ರೂಪಾಯಿ ನಗದು ಸಿಗುತ್ತದೆ."
)

print("Generating Kannada TTS audio...")
result = text_to_speech(text=kannada_text, language="kannada")

if result["success"]:
    print(f"✅ SUCCESS! Audio saved to: {result['audio_path']}")
    print(f"   Language: {result['language']} ({result['lang_code']})")
else:
    print(f"❌ FAILED: {result['error']}")
