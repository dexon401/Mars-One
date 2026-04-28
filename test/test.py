import requests
import datetime
from pprint import pprint, pformat

host = "127.0.0.1"
port = "5000"

DELETE_TEST_JOBS = True

TEST_GET = False
TEST_POST = False
TEST_DELETE = False
TEST_PUT = True

if TEST_POST:
    # POST запросы

    # Тест правильного запроса на запись работы
    print("correct job POST request:")
    json = {
        "team_leader": 1,
        "job": "test",
        "work_size": 8,
        "collaborators": "2, 3, 5",
        "start_date": datetime.datetime.now().isoformat(),
        "end_date": datetime.datetime.now().isoformat(),
        "is_finished": False,
    }
    response = requests.post(f"http://{host}:{port}/api/jobs", json=json)
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n\t{pformat(response.json())}"
    )
    if DELETE_TEST_JOBS:
        requests.delete(f"http://{host}:{port}/api/jobs/{response.json()['id']}")

    # Тест неправильного запроса на запись работы (пустой json)
    print("incorrect job POST request (no json attached):")
    response = requests.post(f"http://{host}:{port}/api/jobs", json={})
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n\t{pformat(response.json())}"
    )

    # Тест неправильного запроса на запись работы (заполнены не все поля)
    print("incorrect job POST request (not all columns filled):")
    json = {
        "job": "test",
        "work_size": 8,
        "collaborators": "2, 3, 5",
        "start_date": datetime.datetime.now().isoformat(),
        "end_date": datetime.datetime.now().isoformat(),
        "is_finished": False,
    }
    response = requests.post(f"http://{host}:{port}/api/jobs", json=json)
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n\t{pformat(response.json())}"
    )

    # Тест неправильного запроса на запись работы (неверный тип данных)
    print("incorrect job POST request (invalid data type for work_size):")
    json = {
        "team_leader": 1,
        "job": "test",
        "work_size": "eight",
        "collaborators": "2, 3, 5",
        "start_date": datetime.datetime.now().isoformat(),
        "end_date": datetime.datetime.now().isoformat(),
        "is_finished": False,
    }
    response = requests.post(f"http://{host}:{port}/api/jobs", json=json)
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n\t{pformat(response.json())}"
    )

if TEST_GET:
    # GET запросы

    # Тест правильного запроса получения всех работ
    print("correct GET jobs request test:")
    url = f"http://{host}:{port}/api/jobs"
    response = requests.get(url=url)
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n{pformat(response.json())}"
    )

    # Тест правильного запроса получения работы
    print("correct GET job request test:")
    url = f"http://{host}:{port}/api/jobs/1"
    response = requests.get(url=url)
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n{pformat(response.json())}"
    )

    # Тест неправильного запроса получения работы (неправильный id)
    print("incorrect GET job request test (not a valid id):")
    url = f"http://{host}:{port}/api/jobs/999"
    response = requests.get(url=url)
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n\t{pformat(response.json())}"
    )

    # Тест неправильного запроса получения работы (строка вместо id)
    print()
    print("incorrect GET job request test (not a valid id: string):")
    url = f"http://{host}:{port}/api/jobs/test"
    response = requests.get(url=url)
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n\t{pformat(response.json())}"
    )

if TEST_DELETE:
    # DELETE запросы

    # Тест правильного запроса удаления работы
    print("correct DELETE job request:")
    # Создание тестовой записи
    json = {
        "team_leader": 1,
        "job": "test",
        "work_size": 8,
        "collaborators": "2, 3, 5",
        "start_date": datetime.datetime.now().isoformat(),
        "end_date": datetime.datetime.now().isoformat(),
        "is_finished": False,
    }
    response = requests.post(f"http://{host}:{port}/api/jobs", json=json)
    if response:
        test_id = response.json()["id"]
        print(f"\tcreated job with id {test_id}")

    # Удаление тестовой записи
    print(f"\tdeleting job with id {test_id}")
    response = requests.delete(f"http://{host}:{port}/api/jobs/{test_id}")
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n\t{pformat(response.json())}"
    )
    
    # Тест неправильного запроса удаления работы (не существующий id)
    print("incorrect DELETE job request (not a valid id):")
    response = requests.delete(f"http://{host}:{port}/api/jobs/999")
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n\t{pformat(response.json())}"
    )
    
    #Тест неправильного запроса удаления работы (неправильный тип данных)
    print("incorrect DELETE job request (not a valid id type):")
    response = requests.delete(f"http://{host}:{port}/api/jobs/test")
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n\t{pformat(response.json())}"
    )

if TEST_PUT:
    # PUT запросы
    
    # Тест правильного запроса изменения работы
    print("correct PUT job request:")
    json = {
        "team_leader": 1,
        "job": "test",
        "work_size": 8,
        "collaborators": "2, 3, 5",
        "start_date": datetime.datetime.now().isoformat(),
        "end_date": datetime.datetime.now().isoformat(),
        "is_finished": False,
    }
    response = requests.post(f"http://{host}:{port}/api/jobs", json=json)
    job_id = response.json()['id']
    print(f"\tcreated job with id {job_id} info: {json}")
    print(f"\tchanging job's team leader to 2")
    response = requests.put(f"http://{host}:{port}/api/jobs/{job_id}", json={"team_leader": 2})
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n\t{pformat(response.json())}"
    )
    print("\tchanged job with id", job_id, "info:", requests.get(f"http://{host}:{port}/api/jobs/{job_id}").json())
    
    if DELETE_TEST_JOBS:
        requests.delete(f"http://{host}:{port}/api/jobs/{job_id}")
    
    #Тест неправильного запроса изменения работы (не существующий id)
    print("incorrect job PUT request (not a valid id):")
    response = requests.put(f"http://{host}:{port}/api/jobs/999", json={"team_leader": 2})
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n\t{pformat(response.json())}"
    )
    
    #Тест неправильного запроса изменения работы (неправильный тип id)
    print("incorrect job PUT request (not a valid id type):")
    response = requests.put(f"http://{host}:{port}/api/jobs/test", json={"team_leader": 2})
    print(
        f"\tHttp status: {response}, reason: {response.reason}, json: \n\t{pformat(response.json())}"
    )