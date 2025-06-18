from typing import Any

import pandas as pd
from googleapiclient.discovery import build

from anki_sync.core.auth.auth import GoogleAuth  # For Union type hint


class GoogleSheetsManager(GoogleAuth):

    def __init__(self, sheet_id: str) -> None:
        super().__init__()
        """Initialize the GoogleSheetsManager with required dependencies.

        Args:
            sheet_id: The ID of the Google Sheet to manage.
        """
        self._sheet_id: str = sheet_id
        self._client = (
            build("sheets", "v4", credentials=self.certs).spreadsheets().values()
        )

    def batch_update(self, updates: list[dict[str, Any]]):
        """Writes new GUIDs back to the Google Sheet using a batch update."""
        if not updates:
            return

        body = {"valueInputOption": "USER_ENTERED", "data": updates}
        self._client.batchUpdate(spreadsheetId=self._sheet_id, body=body).execute()

    def get_rows(self, sheet_name: str) -> pd.DataFrame:
        """Fetch and process words from a Google Sheet.

        Args:
            sheet_name: Optional name of the specific sheet/tab to read from
        """
        values = (
            self._client.get(spreadsheetId=self._sheet_id, range=sheet_name).execute()
        ).get("values", [])

        if len(values) == 0:
            return pd.DataFrame()
        return pd.DataFrame(values[1:], columns=values[0])
