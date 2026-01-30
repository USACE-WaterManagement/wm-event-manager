import requests

from cwms_batch_events.core.models import CdaUserProfile
from cwms_batch_events.core.settings import settings

CDA_API_ROOT = settings.cda_api_root


def get_user_profile(token: str):
    if not CDA_API_ROOT:
        raise ValueError("No CDA_API_ROOT has been provided")
    headers = {"accept": "application/json", "Authorization": f"Bearer {token}"}
    url = f"{CDA_API_ROOT}user/profile"
    response = requests.get(url, headers=headers)
    profile = CdaUserProfile(**response.json())
    return profile


def get_user_allowed_offices(cda_user: CdaUserProfile):
    allowed_offices: list[str] = []
    for office, roles in cda_user.roles.items():
        if "CWMS Users" in roles:
            allowed_offices.append(office.lower())
    return allowed_offices
