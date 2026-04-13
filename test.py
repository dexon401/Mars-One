import requests
import datetime
from pprint import pprint, pformat

host = "127.0.0.1"
port = "5000"

# POST запросы

# Тест правильного запроса на запись работы
print()
print("correct job POST request")
json = {
    "team_leader": 1,
    "job": "test",
    "work_size": 8,
    "collaborators": "2, 3, 5",
    "start_date": datetime.datetime.now().isoformat(),
    "end_date": datetime.datetime.now().isoformat(),
    "is_finished": False,
}
response = requests.post("http://localhost:5000/api/jobs", json=json)
print(
    f"Http status: {response}, reason: {response.reason}, json: \n{pformat(response.json())}"
)

# Тест неправильного запроса на запись работы (пустой json)
print()
print("incorrect job POST request (no json attached)")
response = requests.post("http://localhost:5000/api/jobs", json={})
print(
    f"Http status: {response}, reason: {response.reason}, json: \n{pformat(response.json())}"
)

# Тест неправильного запроса на запись работы (заполнены не все поля)
print()
print("incorrect job POST request (not all columns filled)")
json = {
    "job": "test",
    "work_size": 8,
    "collaborators": "2, 3, 5",
    "start_date": datetime.datetime.now().isoformat(),
    "end_date": datetime.datetime.now().isoformat(),
    "is_finished": False,
}
response = requests.post("http://localhost:5000/api/jobs", json=json)
print(
    f"Http status: {response}, reason: {response.reason}, json: \n{pformat(response.json())}"
)

# Тест неправильного запроса на запись работы (неверный тип данных)
print()
print("incorrect job POST request (invalid data type for work_size)")
json = {
    "team_leader": 1,
    "job": "test",
    "work_size": "eight",
    "collaborators": "2, 3, 5",
    "start_date": datetime.datetime.now().isoformat(),
    "end_date": datetime.datetime.now().isoformat(),
    "is_finished": False,
}
response = requests.post("http://localhost:5000/api/jobs", json=json)
print(
    f"Http status: {response}, reason: {response.reason}, json: \n{pformat(response.json())}"
)

# GET запросы

# Тест правильного запроса получения всех работ
print("correct get jobs request test:")
url = f"http://{host}:{port}/api/jobs"
response = requests.get(url=url)
print(
    f"Http status: {response}, reason: {response.reason}, json: \n{pformat(response.json())}"
)

# Тест правильного запроса получения работы
print()
print("correct get job request test:")
url = f"http://{host}:{port}/api/jobs/1"
response = requests.get(url=url)
print(
    f"Http status: {response}, reason: {response.reason}, json: \n{pformat(response.json())}"
)

# Тест неправильного запроса получения работы (неправильный id)
print()
print("incorrect get job request test (not a valid id)")
url = f"http://{host}:{port}/api/jobs/99"
response = requests.get(url=url)
print(
    f"Http status: {response}, reason: {response.reason}, json: \n{pformat(response.json())}"
)

# Тест неправильного запроса получения работы (строка вместо id)
print()
print("incorrect get job request test (not a valid id: string):")
url = f"http://{host}:{port}/api/jobs/test"
response = requests.get(url=url)
print(
    f"Http status: {response}, reason: {response.reason}, json: \n{pformat(response.json())}"
)

