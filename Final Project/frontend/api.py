import requests

BASE_URL = "http://localhost:8000"

def get(path, params=None):
    try:
        r = requests.get(f"{BASE_URL}{path}", params=params, timeout=5)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to backend. Make sure the FastAPI server is running on port 8000."
    except Exception as e:
        return None, str(e)

def post(path, data):
    try:
        r = requests.post(f"{BASE_URL}{path}", json=data, timeout=5)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to backend."
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except:
            detail = str(e)
        return None, detail
    except Exception as e:
        return None, str(e)

def patch(path, data=None):
    try:
        r = requests.patch(f"{BASE_URL}{path}", json=data, timeout=5)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to backend."
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except:
            detail = str(e)
        return None, detail
    except Exception as e:
        return None, str(e)
