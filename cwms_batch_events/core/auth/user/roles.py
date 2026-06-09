import requests

from cwms_batch_events.core.models import CdaUserProfile
from cwms_batch_events.core.settings import settings

CDA_API_ROOT = settings.cda_api_root


def get_user_profile_apikey(apikey: str):
    if not CDA_API_ROOT:
        raise ValueError("No CDA_API_ROOT has been provided")
    headers = {"accept": "application/json", "Authorization": f"apikey {apikey}"}
    url = f"{CDA_API_ROOT}user/profile"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    profile = CdaUserProfile(**response.json())
    return profile


def get_user_profile_jwt(token: str):
    if not CDA_API_ROOT:
        raise ValueError("No CDA_API_ROOT has been provided")
    headers = {"accept": "application/json", "Authorization": f"Bearer {token}"}
    url = f"{CDA_API_ROOT}user/profile"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    profile = CdaUserProfile(**response.json())
    return profile


def get_user_allowed_offices(cda_user: CdaUserProfile):
    allowed_offices: list[str] = []
    for office, roles in cda_user.roles.items():
        if "CWMS Users" in roles:
            allowed_offices.append(office)
    return allowed_offices


def get_user_admin_offices(cda_user: CdaUserProfile):
    admin_roles = ["Data Acquisition Mgr", "Data Exchange Mgr"]
    admin_offices: list[str] = []
    for office, roles in cda_user.roles.items():
        office_admin = [role for role in roles if role in admin_roles]
        if len(office_admin) > 0:
            admin_offices.append(office)
    return admin_offices
