import requests

payload = {
    "model": "qwen2.5:7b",
    "prompt": "Say only Hello",
    "stream": False
}

print("Sending...")

response = requests.post(
    "http://localhost:11434/api/generate",
    json=payload,
    timeout=20
)

print(response.json()["response"])