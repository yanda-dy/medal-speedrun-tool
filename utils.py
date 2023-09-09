import requests, json


def fetch_live_data(timeout=0.2):
    url = "http://localhost:20727/json"

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        json_data = json.loads(response.content.decode("utf-8-sig"))
        return json_data

    except requests.exceptions.RequestException as e:
        return -1


def boot_status():
    data = fetch_live_data(timeout=0.02)
    if data == -1:
        return False
    elif data["status"] == 0:
        return False
    return True


def map_start():
    data = fetch_live_data()
    if data == -1: return False
    if data["status"] == 2 and data["score"] == 0: return True
    return False
