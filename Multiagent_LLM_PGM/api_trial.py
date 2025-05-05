import requests
data = {"prompt": "Hello, how are you?", "n_predict": 50, "temperature": 0.7}
response = requests.post("http://localhost:6567/completion", json=data)
print(response.json())
