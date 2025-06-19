import os

from google.oauth2.service_account import Credentials


class GoogleAuth:

    def __init__(self):
        certs_path: str = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
        self._api_key = os.environ.get("GOOGLE_API_KEY", "")
        self._certs: Credentials = Credentials.from_service_account_file(certs_path)

    @property
    def certs(self) -> Credentials:
        return self._certs

    @property
    def key(self) -> str:
        return self._api_key


class ElevenlabsAuth:

    def __init__(self):
        self._certs: str = os.getenv("ELEVENLABS_API_KEY", "")

    @property
    def certs(self) -> str:
        return self._certs
