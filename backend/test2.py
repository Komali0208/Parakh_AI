import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={"sentences": ["This study investigates the potential implications of AI in healthcare.", "I just stayed up all night trying to finish this."]}
)

print(response.json())
