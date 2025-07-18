from typing import Any

import pandas as pd
from googleapiclient.discovery import build

from anki_sync.core.auth.auth import GoogleAuth  # For Union type hint


class GoogleSheetsManager(GoogleAuth):

    def __init__(self, sheet_id: str) -> None:
        super().__init__()
        self._sheet_id: str = sheet_id
        self._client = (
            build("sheets", "v4", credentials=self.certs, cache_discovery=False)
            .spreadsheets()
            .values()
        )

    def batch_update(self, updates: list[dict[str, Any]]):
        if not updates:
            return

        body = {"valueInputOption": "USER_ENTERED", "data": updates}
        self._client.batchUpdate(spreadsheetId=self._sheet_id, body=body).execute()

    def get_rows(self, sheet_name: str) -> pd.DataFrame:
        values = (
            self._client.get(spreadsheetId=self._sheet_id, range=sheet_name).execute()
        ).get("values", [])

        if len(values) == 0:
            return pd.DataFrame()
        return pd.DataFrame(values[1:], columns=values[0])
