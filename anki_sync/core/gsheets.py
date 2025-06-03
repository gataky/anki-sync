import os
from typing import Any, Optional, List, Dict
from .models import Word
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from .word_processor import WordProcessor
from .stats import Stats

class GoogleSheetsManager:
    """Manages interactions with Google Sheets for word data."""

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(self, word_processor: WordProcessor, stats: Stats):
        """Initialize the Google Sheets manager.

        Args:
            word_processor: The WordProcessor instance to use for processing word data
            stats: Stats instance to track processing statistics
        """
        self.word_processor = word_processor
        self.stats = stats
        self.service = None

    def get_service(self) -> Optional[Any]:
        """Authenticates and returns the Google Sheets service client."""
        if self.service:
            return self.service

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
            print("or specify the service account JSON file path directly in gsheets.py.")
            return None

        self.service = build("sheets", "v4", credentials=creds)
        return self.service

    def _write_guids_to_sheet(
        self, sheet_api: Any, sheet_id: str, sheet_name: str, updates: List[Dict[str, Any]]
    ):
        """Writes new GUIDs back to the Google Sheet using a batch update."""
        if not updates:
            return

        try:
            body = {"valueInputOption": "USER_ENTERED", "data": updates}
            sheet_api.values().batchUpdate(spreadsheetId=sheet_id, body=body).execute()
        except Exception as e:
            self.stats.errors["guid_update"] = self.stats.errors.get("guid_update", 0) + 1

    def get_words_from_sheet(self, sheet_id: str, sheet_name: str) -> List[Word]:
        """Fetches words from the specified Google Sheet using a service account."""
        service = self.get_service()
        if not service:
            self.stats.errors["service_init"] = self.stats.errors.get("service_init", 0) + 1
            return []

        sheet_api = service.spreadsheets()
        range_name = f"{sheet_name}!A2:Z"  # Start from row 2 to skip headers

        try:
            result = (
                sheet_api.values().get(spreadsheetId=sheet_id, range=range_name).execute()
            )
            values = result.get("values", [])
        except Exception as e:
            self.stats.errors["data_fetch"] = self.stats.errors.get("data_fetch", 0) + 1
            return []

        words_data: List[Word] = []
        guid_updates_for_sheet: List[Dict[str, Any]] = []
        
        self.stats.total_lines_read = len(values)
        
        if not values:
            return []

        for row_idx, row in enumerate(values):
            if not any(cell for cell in row if str(cell).strip()):
                continue
            try:
                padded_row = row + [None] * (max(0, 6 - len(row)))
                word_constructor_args, guid_update_item = self.word_processor.process_row(
                    padded_row,
                    row_idx,
                    sheet_name,
                )

                if guid_update_item:
                    guid_updates_for_sheet.append(guid_update_item)
                    self.stats.new_lines_processed += 1

                if word_constructor_args:
                    words_data.append(Word(**word_constructor_args))
                    self.stats.total_lines_processed += 1

            except Exception as e:
                self.stats.errors["row_processing"] = self.stats.errors.get("row_processing", 0) + 1

        self._write_guids_to_sheet(sheet_api, sheet_id, sheet_name, guid_updates_for_sheet)
        return words_data
