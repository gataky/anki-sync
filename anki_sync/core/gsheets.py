import os
from typing import Any, Dict, List, Optional

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Union # For Union type hint
from .models import Word, Verb # Added Verb
# from .word_processor import WordProcessor # Will use a generic processor type


class GoogleSheetsManager:
    """Manages interactions with Google Sheets API and data processing.

    This class handles authentication, fetching data from Google Sheets,
    and processing the data into items (like Word or Verb objects) using a provided processor.
    """

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(self, sheet_id: str, item_processor: Any) -> None:
        """Initialize the GoogleSheetsManager with required dependencies.

        Args:
            sheet_id: The ID of the Google Sheet to manage.
            word_processor: Instance of WordProcessor for processing sheet data
        """
        self.sheet_id = sheet_id
        self.item_processor = item_processor # Renamed from word_processor
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
        sheet_name: str,
        updates: List[Dict[str, Any]],
    ):
        """Writes new GUIDs back to the Google Sheet using a batch update."""
        if not updates:
            return

        try:
            body = {"valueInputOption": "USER_ENTERED", "data": updates}
            sheet_api.values().batchUpdate(spreadsheetId=self.sheet_id, body=body).execute()
        except Exception:
            pass

    def get_sheet_data(self, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Fetch and process words from a Google Sheet.

        Args:
            sheet_name: Optional name of the specific sheet/tab to read from
        """
        # Get the sheet data
        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=self.sheet_id, range=sheet_name)
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

    def get_items_from_sheet(
        self, sheet_name: Optional[str] = None
    ) -> List[Union[Word, Verb, Any]]: # Adjusted return type
        """Fetch and process items (words, verbs, etc.) from a Google Sheet.

        Args:
            sheet_name: Optional name of the specific sheet/tab to read from

        Returns:
            List of processed item objects (e.g., Word, Verb)

        Raises:
            Exception: If there's an error fetching or processing the data
        """
        try:
            # Ensure sheet_name is provided for GUID updates, default if necessary
            actual_sheet_name = sheet_name
            if not actual_sheet_name:
                # Attempt to get the first sheet's name if not provided,
                # as _write_guids_to_sheet needs a specific sheet name.
                # This might require an additional API call if not easily determined.
                # For simplicity, we'll assume sheet_name is usually provided when GUIDs are managed.
                # If sheet_name is None, GUID writing might target an unexpected sheet or fail.
                # A robust solution would fetch sheet metadata to get the first sheet name if None.
                print("Warning: sheet_name not provided to get_items_from_sheet. GUID updates might be affected.")
                # For now, let's pass it as None and let _process_guid_for_row handle it if it can.
                # Or, require sheet_name if GUID updates are expected.
                # Let's assume sheet_name is the actual name used in ranges like 'Sheet1'.
                pass # actual_sheet_name remains as passed

            df = self.get_sheet_data(actual_sheet_name)

            items = []
            guid_updates_batch = []
            for idx, row in df.iterrows(): # idx is the 0-based DataFrame index
                try:
                    item, guid_update = self.item_processor.process_row(row, actual_sheet_name or "Sheet1", idx)
                    if item:
                        items.append(item)
                    if guid_update:
                        guid_updates_batch.append(guid_update)
                except Exception as e:
                    print(e)
                    continue

            if guid_updates_batch and actual_sheet_name: # Ensure sheet_name is valid for writing
                self._write_guids_to_sheet(
                    self.service.spreadsheets(), actual_sheet_name, guid_updates_batch
                )
            elif guid_updates_batch and not actual_sheet_name:
                print("Warning: GUID updates were generated but sheet_name was not available to write them back.")


            return items

        except HttpError as error:
            raise Exception(f"An error occurred while fetching data: {error}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")
