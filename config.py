# config.py

# consumercompensationbureau Credentials
USER = "ranyabenali@gmail.com"
PASS = "P455word123"
BASE_URL = "https://consumercompensationbureau.omnisign.co.uk/"

# Egnyte Credentials
CLIENT_ID = "gy454xrq53wdhhtgd45jde8t"
EGNYTE_USER = "evgenykurakin19891031@gmail.com"
EGNYTE_PASS = "pmin2005"
ACCESS_TOKEN = ""
UPLOAD_DIR = "/Shared/OmniSign"


def get_access_token():
    """
    Get access token when you change password in egnyte.com
    :return: str
    """
    import requests
    URL = "https://ccbfiles.egnyte.com/puboauth/token"

    payload = {
        "client_id": CLIENT_ID,
        "username": EGNYTE_USER,
        "password": EGNYTE_PASS,
        "grant_type": "password"
    }

    res = requests.post(URL, data=payload).json()
    return res['access_token']

ACCESS_TOKEN = get_access_token()

