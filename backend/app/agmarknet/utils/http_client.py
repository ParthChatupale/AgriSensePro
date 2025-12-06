import requests

DEFAULT_HEADERS = {
    "User-Agent": "AgriSenseBot/1.0",
    "Accept": "application/json"
}

def http_get(url, params=None, timeout=20):
    """
    Wrapper for GET requests with basic error handling.
    Returns: (success, json or bytes or error message)
    """
    try:
        response = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=timeout)

        if not response.ok:
            return False, f"HTTP {response.status_code}: {response.text}"

        # Auto-detect JSON or file download
        if "application/json" in response.headers.get("Content-Type", ""):
            return True, response.json()
        else:
            return True, response.content

    except Exception as e:
        return False, str(e)
