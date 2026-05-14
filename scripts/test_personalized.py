import requests
import json

url = "http://localhost:8000/personalized-ask"

# Kannada test — includes district, crop, land size
payload = {
    "question": "ನಾನು ಮಂಡ್ಯದಲ್ಲಿ 3 ಎಕರೆ ಜಮೀನು ಹೊಂದಿದ್ದೇನೆ. ಅಕ್ಕಿ ಬೆಳೆ ಮಾಡುತ್ತೇನೆ. ನನಗೆ ಯಾವ ಯೋಜನೆಗಳು ಸಿಗುತ್ತವೆ?",
    "session_id": "farmer_session_001"
}

headers = {"Content-Type": "application/json", "Accept": "application/json"}
response = requests.post(url, json=payload, headers=headers)

result = response.json()

# Write full response to file
with open("test_personalized_output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("=== PERSONALIZED ASK RESULT ===")
print(f"Status: {response.status_code}")
print(f"Language: {result.get('language')}")

profile = result.get("farmer_profile", {})
print(f"\nExtracted Farmer Profile:")
print(f"  District: {profile.get('district')}")
print(f"  Land: {profile.get('land_size')} acres")
print(f"  Crop: {profile.get('crop_type')}")
print(f"  Confidence: {profile.get('extraction_confidence')}")

schemes = result.get("recommended_schemes", [])
print(f"\nTop {len(schemes)} Recommended Schemes:")
for s in schemes:
    print(f"  [{s.get('eligibility_score')}/100] {s.get('scheme_name')} — {s.get('reason')[:60]}")

print(f"\nFull response saved to test_personalized_output.json")
