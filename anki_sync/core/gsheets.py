import os
from typing import List, Any, Optional, Dict, Tuple
from .models import Word
from anki_sync.utils.guid import generate_guid

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials # For service account
# Import from the new synthesize_audio module
from .synthesize_audio import Synthesize

# Global instance of the synthesizer, initialized once
SYNTHESIZER = Synthesize()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

GENDER_TO_ARTICLE_MAP = {
    "masculine": "ο",
    "feminine": "η",
    "neuter": "το",
    "masculine pl.": "οι",
    "feminine pl.": "οι", # Note: feminine pl. is also οι
    "neuter pl.": "τα",
}


def get_google_sheets_service() -> Optional[Any]:
    """Authenticates and returns the Google Sheets service client."""
    creds = None
    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    if not key_path:
        print("Error: GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
        return

    try:
        creds = Credentials.from_service_account_file(key_path)
    except Exception as e:
        print(f"Error loading Google credentials: {e}")
        print("Please ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly,")
        print("or specify the service account JSON file path directly in gsheets.py.")
        return None

    service = build('sheets', 'v4', credentials=creds)
    return service

def _process_guid_for_row(
    guid_cell_value: Any,
    row_idx: int,
    sheet_name: str
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Processes the GUID for a row. Uses existing GUID or generates a new one.
    Returns the GUID to use and an optional update item for the sheet.
    """
    guid_to_use = str(guid_cell_value or "").strip()
    guid_update_item = None
    if not guid_to_use:
        new_guid_value = generate_guid()
        guid_to_use = new_guid_value
        actual_sheet_row_num = row_idx + 2
        print(f"Info: Row {actual_sheet_row_num} in sheet '{sheet_name}' is missing GUID. Generated: {guid_to_use}")
        guid_update_item = {
            'range': f"{sheet_name}!A{actual_sheet_row_num}",
            'values': [[guid_to_use]]
        }
    return guid_to_use, guid_update_item

def _generate_sound_filename_from_greek(original_greek_word: str) -> Optional[str]:
    """Generates the sound filename if a Greek word is provided."""
    if original_greek_word:
        return f"{original_greek_word}.mp3"
    return None

def _prefix_article_to_greek_word(
    original_greek_word: str,
    gender_string_for_article: str
) -> str:
    """Prefixes the correct Greek article to the Greek word based on gender."""
    processed_greek_word = original_greek_word
    if gender_string_for_article and original_greek_word:
        article = GENDER_TO_ARTICLE_MAP.get(gender_string_for_article)
        if article:
            processed_greek_word = f"{article} {original_greek_word}"
    return processed_greek_word

def _compile_tags_for_word(
    raw_class: Optional[str],
    original_gender_from_sheet: Optional[str],
    hierarchical_tag_cells: List[Any]
) -> List[str]:
    """Compiles a list of tags from class, gender, and hierarchical columns."""
    tags_list = []
    class_tag_value = str(raw_class or "").strip()
    if class_tag_value:
        tags_list.append(f"class::{class_tag_value}".replace(" ", "\u00A0"))

    gender_tag_value = str(original_gender_from_sheet or "").strip()
    if gender_tag_value:
        # Take only the first part of gender (e.g., "masculine" from "masculine pl.") for this tag
        gender_base_tag = gender_tag_value.split(" ")[0]
        tags_list.append(f"class::{gender_base_tag}".replace(" ", "\u00A0"))

    current_hierarchy_parts = []
    for cell_content_raw in hierarchical_tag_cells:
        cell_content = str(cell_content_raw or "").strip()
        if not cell_content:
            break
        current_hierarchy_parts.append(cell_content.replace(" ", "\u00A0"))
        tags_list.append("::".join(current_hierarchy_parts))
    return sorted(list(set(tags_list)))

def _parse_sheet_row(
    padded_row: List[Any],
    row_idx: int,
    sheet_name: str,
    sound_dir: str
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Parses a single row from the sheet data to extract Word arguments and any GUID update needed.
    Returns a tuple: (word_constructor_args, guid_update_operation).
    word_constructor_args is None if the row is invalid for Word creation.
    guid_update_operation is None if no new GUID was generated for this row.
    """
    guid_to_use, guid_update_item = _process_guid_for_row(padded_row[0], row_idx, sheet_name)

    raw_english = padded_row[1]
    original_greek_word = str(padded_row[2] or "").strip()
    raw_class = padded_row[3]
    original_gender_from_sheet = padded_row[4] # Keep original case for Word object

    sound_filename = _generate_sound_filename_from_greek(original_greek_word)

    # Audio synthesis logic using the new module
    if sound_filename and original_greek_word and sound_dir and SYNTHESIZER.client:
        # sound_filename is like "word.mp3", os.path.exists needs full path
        full_sound_path = os.path.join(sound_dir, sound_filename)
        if not os.path.exists(full_sound_path):
            print(f"Attempting to synthesize audio for '{original_greek_word}' as it's missing at '{full_sound_path}'...")
            # SYNTHESIZER.text expects the base word and the output directory
            SYNTHESIZER.text(text_to_synthesize=original_greek_word, output_directory=sound_dir)
        # else:
            # print(f"Audio for '{original_greek_word}' already exists. Skipping synthesis.")

    gender_string_for_article = str(original_gender_from_sheet or "").strip().lower()
    processed_greek_word = _prefix_article_to_greek_word(
        original_greek_word,
        gender_string_for_article
    )

    # Hierarchical tags start from column F (index 5)
    hierarchical_tag_cells = padded_row[5:]
    tags = _compile_tags_for_word(
        raw_class,
        original_gender_from_sheet,
        hierarchical_tag_cells
    )

    word_args = {
        "guid": guid_to_use,
        "english": raw_english or "",
        "greek": processed_greek_word,
        "word_class": raw_class or "",
        "gender": original_gender_from_sheet, # Store the original gender string from the sheet
        "sound_file": sound_filename,
        "tags": tags
    }

    # Basic validation: ensure essential fields are present
    if not word_args["english"] or not original_greek_word or not word_args["word_class"]:
        print(f"Skipping malformed row {row_idx + 2} (Sheet row): Missing essential data (English, Greek, or Class). Content: {padded_row[:6]}")
        return None, guid_update_item # word_args is None, but guid_update_item might exist

    return word_args, guid_update_item

def _write_guids_to_sheet(sheet_api: Any, sheet_id: str, sheet_name: str, updates: List[Dict[str, Any]]):
    """Writes new GUIDs back to the Google Sheet using a batch update."""
    if not updates:
        return

    print(f"\nAttempting to write back {len(updates)} new GUID(s) to sheet '{sheet_name}'...")
    try:
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': updates
        }
        sheet_api.values().batchUpdate(spreadsheetId=sheet_id, body=body).execute()
        print(f"Successfully wrote back {len(updates)} GUID(s) to the sheet.")
    except Exception as e:
        print(f"Error writing new GUIDs back to Google Sheet: {e}")
        print("Note: The Word objects in memory will have the new GUIDs, but they were not saved back to the sheet.")

def get_words_from_sheet(sheet_id: str, sheet_name: str, sound_dir: str) -> List[Word]:
    """
    Fetches words from the specified Google Sheet using a service account.
    Logs errors for malformed rows.
    """
    print(f"Attempting to fetch words from sheet ID: {sheet_id}, page: {sheet_name}")
    service = get_google_sheets_service()
    if not service:
        print("Failed to initialize Google Sheets service. Cannot fetch words.")
        return []

    sheet_api = service.spreadsheets()
    # Assuming Column A:GUID, B:Eng, C:Gre, D:Class, E:Gender, F+ :Tags
    range_name = f"{sheet_name}!A2:Z" # Start from row 2 to skip headers

    try:
        result = sheet_api.values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get('values', [])
    except Exception as e:
        print(f"Error fetching data from Google Sheet: {e}")
        return []

    words_data: List[Word] = []
    guid_updates_for_sheet: List[Dict[str, Any]] = []
    if not values:
        print("No data found in the sheet.")
        return []

    for row_idx, row in enumerate(values):
        if not any(cell for cell in row if str(cell).strip()): # Skip entirely empty or whitespace-only rows
            continue
        try:
            # Pad row with None if core columns are missing (up to where tags start)
            padded_row = row + [None] * (max(0, 6 - len(row)))

            word_constructor_args, guid_update_item = _parse_sheet_row(
                padded_row, row_idx, sheet_name, sound_dir,
            )

            if guid_update_item:
                guid_updates_for_sheet.append(guid_update_item)

            if word_constructor_args:
                words_data.append(Word(**word_constructor_args))
            # If word_constructor_args is None, the row was invalid for Word creation,
            # but a GUID might have still been generated and added to guid_updates_for_sheet.
            # This is fine, as we'd still want to write back that GUID.

        except Exception as e: # Catches Pydantic validation errors and others
            print(f"Error processing row {row_idx + 2} (Sheet row). Content: {row}. Error: {e}")

    # After processing all rows, write back any new GUIDs to the Google Sheet
    _write_guids_to_sheet(sheet_api, sheet_id, sheet_name, guid_updates_for_sheet)

    return words_data
