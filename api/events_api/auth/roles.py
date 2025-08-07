import os
import requests

from events_api.schemas import CdaUserProfile

CDA_HOST = os.getenv("CDA_HOST")


def get_user_allowed_offices(token: str):
    if not CDA_HOST:
        raise ValueError("No CDA_HOST has been provided.")
    headers = {"accept": "application/json", "Authorization": f"Bearer {token}"}
    url = f"{CDA_HOST}/user/profile"
    response = requests.get(url, headers=headers)
    profile = CdaUserProfile(**response.json())
    allowed_offices: list[str] = []
    for office, roles in profile.roles.items():
        if "CWMS Users" in roles:
            allowed_offices.append(office.lower())
    return allowed_offices
