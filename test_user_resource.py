import requests


print(requests.get("http://127.0.0.1:5000/api/v2/users").json())
print(requests.get("http://127.0.0.1:5000/api/v2/users/1").json())
print(requests.get("http://127.0.0.1:5000/api/v2/users/999").json())

test_data_json = {
  "surname": "Smith",
  "name": "John",
  "age": 35,
  "position": "Software Engineer",
  "speciality": "Backend Development",
  "address": "123 Main Street, Apt 4B, New York, NY 10001",
  "email": "john.smith@example.com",
  "password": "SecurePassword123!"
}

response_json = requests.post("http://127.0.0.1:5000/api/v2/users", json=test_data_json).json()
print(response_json)
print(requests.post("http://127.0.0.1:5000/api/v2/users", json={}).json())

print(requests.delete(f"http://127.0.0.1:5000/api/v2/users/{response_json["id"]}").json())
print(requests.delete(f"http://127.0.0.1:5000/api/v2/users/999").json())
