import os
from google.oauth2.service_account import Credentials


class GoogleAuth:

    def __init__(self):
        key_path: str = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
        self._certs: Credentials = Credentials.from_service_account_file(key_path)

    @property
    def certs(self) -> Credentials:
        return self._certs


class ElevenlabsAuth:

    def __init__(self):
        self._certs: str =os.getenv("ELEVENLABS_API_KEY", "")

    @property
    def certs(self) -> str:
        return self._certs
