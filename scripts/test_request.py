import requests
import json

url = "http://localhost:8000/ask"
payload = {
    "question": "ಅಕ್ಕಿ ಬೆಳೆ ರೈತರಿಗೆ ಯಾವ ಯೋಜನೆಗಳಿವೆ?"
}
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
result = json.dumps(response.json(), indent=2, ensure_ascii=False)

# Write to file to handle Kannada Unicode on Windows terminal
with open("test_output.json", "w", encoding="utf-8") as f:
    f.write(result)

print("Response written to test_output.json")
print("Status:", response.status_code)
print("Language detected:", response.json().get("language"))
print("Answer preview (first 100 chars):", response.json().get("answer", "")[:100])
