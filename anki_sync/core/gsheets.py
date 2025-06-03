import os
from typing import Any, Dict, List, Optional

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .models import Word
from .stats import Stats
from .word_processor import WordProcessor


class GoogleSheetsManager:
    """Manages interactions with Google Sheets API and data processing.

    This class handles authentication, fetching data from Google Sheets,
    and processing the data into Word objects using a WordProcessor.
    """

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(self, word_processor: WordProcessor, stats: Stats) -> None:
        """Initialize the GoogleSheetsManager with required dependencies.

        Args:
            word_processor: Instance of WordProcessor for processing sheet data
            stats: Instance of Stats for tracking processing statistics
        """
        self.word_processor = word_processor
        self.stats = stats
        self.service = self._get_sheets_service()

    def _get_sheets_service(self):
        """Get an authenticated Google Sheets service.

        Returns:
            An authenticated Google Sheets API service instance.

        Raises:
            Exception: If authentication fails or service cannot be created.
        """
        creds = None
        key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

        if not key_path:
            print("Error: GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
            return None

        try:
            creds = Credentials.from_service_account_file(key_path)
        except Exception as e:
            print(f"Error loading Google credentials: {e}")
            print(
                "Please ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly,"
            )
            print(
                "or specify the service account JSON file path directly in gsheets.py."
            )
            return None

        return build("sheets", "v4", credentials=creds)

    def _write_guids_to_sheet(
        self,
        sheet_api: Any,
        sheet_id: str,
        sheet_name: str,
        updates: List[Dict[str, Any]],
    ):
        """Writes new GUIDs back to the Google Sheet using a batch update."""
        if not updates:
            return

        try:
            body = {"valueInputOption": "USER_ENTERED", "data": updates}
            sheet_api.values().batchUpdate(spreadsheetId=sheet_id, body=body).execute()
        except Exception:
            self.stats.errors["guid_update"] = (
                self.stats.errors.get("guid_update", 0) + 1
            )

    def get_sheet_data(self, sheet_id: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Fetch and process words from a Google Sheet.

        Args:
            sheet_id: The ID of the Google Sheet to fetch data from
            sheet_name: Optional name of the specific sheet/tab to read from
        """
        # Get the sheet data
        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=sheet_name)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found in the sheet.")
            return pd.DataFrame()

        # Convert to DataFrame for easier processing
        df = pd.DataFrame(values[1:], columns=values[0])

        # Find the Category column index
        category_col = "Category"
        if category_col in df.columns:
            category_idx = df.columns.get_loc(category_col)
            # Convert all columns from Category onwards to strings, replacing None with empty string
            tag_columns = df.columns[category_idx:]
            df[tag_columns] = df[tag_columns].fillna("").astype(str)

        return df

    def get_words_from_sheet(
        self, sheet_id: str, sheet_name: Optional[str] = None
    ) -> List[Word]:
        """Fetch and process words from a Google Sheet.

        Args:
            sheet_id: The ID of the Google Sheet to fetch data from
            sheet_name: Optional name of the specific sheet/tab to read from

        Returns:
            List of processed Word objects

        Raises:
            Exception: If there's an error fetching or processing the data
        """
        try:
            df = self.get_sheet_data(sheet_id, sheet_name)
            self.stats.total_lines_read = len(df)

            # Process each row
            words = []
            for _, row in df.iterrows():
                try:
                    word = self.word_processor.process_row(row)
                    if word:
                        words.append(word)
                        self.stats.total_lines_processed += 1
                except Exception as e:
                    print(e)
                    self.stats.errors.append(f"Error processing row: {str(e)}")
                    continue

            return words

        except HttpError as error:
            raise Exception(f"An error occurred while fetching data: {error}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")
