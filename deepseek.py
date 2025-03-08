import requests

r = requests.post("https://api.deepseek.com/chat/completions", headers={
    "Authorization": f"Bearer sk-86d78d254bfe439ab07237b5f6ccdfc9",
    "Content-Type": "application/json",
}, json={
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    "stream": False
})

print(r)
print(r.text)
print(r.json())
