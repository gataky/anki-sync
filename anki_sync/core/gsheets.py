from typing import Any

import pandas as pd
from googleapiclient.discovery import build

from anki_sync.core.auth.auth import GoogleAuth # For Union type hint


class GoogleSheetsManager(GoogleAuth):
    """Manages interactions with Google Sheets API and data processing.

    This class handles authentication, fetching data from Google Sheets,
    and processing the data into items (like Word or Verb objects) using a provided processor.
    """


    def __init__(self, sheet_id: str) -> None:
        super().__init__()
        """Initialize the GoogleSheetsManager with required dependencies.

        Args:
            sheet_id: The ID of the Google Sheet to manage.
            word_processor: Instance of WordProcessor for processing sheet data
        """
        self.sheet_id: str = sheet_id
        self.service = build("sheets", "v4", credentials=self.certs)


    def get_sheet_data(self, sheet_name: str | None = None) -> pd.DataFrame:
        """Fetch and process words from a Google Sheet.

        Args:
            sheet_name: Optional name of the specific sheet/tab to read from
        """
        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=self.sheet_id, range=sheet_name)
            .execute()
        )
        values = result.get("values", [])

        if len(values) == 0:
            return pd.DataFrame()
        return pd.DataFrame(values[1:], columns=values[0])
