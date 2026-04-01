import requests

headers = {
    "Authorization": "Bearer "
}

requisicao = requests.get("http://127.0.0.1:8000/auth/refresh", headers=headers, timeout=10)
print(requisicao)
print(requisicao.json())