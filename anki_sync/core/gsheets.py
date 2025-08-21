from typing import Any

import pandas as pd
from googleapiclient.discovery import build

from anki_sync.core.auth.auth import GoogleAuth  # For Union type hint


class GoogleSheetsManager(GoogleAuth):

    def __init__(self, sheet_id: str) -> None:
        super().__init__()
        self._sheet_id: str = sheet_id

        self._sheets_service = build("sheets", "v4", credentials=self.certs, cache_discovery=False)
        self._values_service = self._sheets_service.spreadsheets().values()        

    def batch_update(self, updates: list[dict[str, Any]]):
        if not updates:
            return

        body = {"valueInputOption": "USER_ENTERED", "data": updates}
        self._values_service.batchUpdate(spreadsheetId=self._sheet_id, body=body).execute()

    def get_rows(self, sheet: str) -> pd.DataFrame:
        values = (
            self._values_service.get(spreadsheetId=self._sheet_id, range=sheet).execute()
        ).get("values", [])

        expected_columns = len(values[0])
        for v in values:
            if len(v) < expected_columns:
                v.extend([""] * (expected_columns - len(v)))

        if len(values) == 0:
            return pd.DataFrame()
        return pd.DataFrame(values[1:], columns=values[0])

    def get_notes(self, sheet: str) -> pd.DataFrame:
        data = self.get_rows(sheet)
        if sheet in {"nouns", "adverbs"}:
            for col in ["tag", "sub tag 1", "sub tag 2"]:
                if col in data:
                    data[col] = data[col].fillna("")
        return data
