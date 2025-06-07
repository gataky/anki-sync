from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from anki_sync.utils.guid import generate_guid
from .synthesizers.audio_synthesizer import AudioSynthesizer
from .models import Verb
from .stats import Stats


class VerbProcessor:
    """Processes verb data from Google Sheets into Verb objects."""

    def __init__(self, audio_synthesizer: AudioSynthesizer, stats: Stats) -> None:
        """Initialize the VerbProcessor.

        Args:
            audio_synthesizer: Instance for audio generation.
            stats: Instance for tracking processing statistics.
        """
        self.audio_synthesizer = audio_synthesizer
        self.stats = stats

    def _process_guid_for_row(
        self, guid_cell_value: Any, row_idx: int, sheet_name: str
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Processes the GUID for a row. Uses existing GUID or generates a new one."""
        guid_to_use = str(guid_cell_value or "").strip()
        guid_update_item = None
        if not guid_to_use:
            new_guid_value = generate_guid()
            guid_to_use = new_guid_value
            actual_sheet_row_num = row_idx + 2  # Assuming header is row 1, data starts row 2
            print(
                f"Info: Row {actual_sheet_row_num} in sheet '{sheet_name}' is missing GUID. Generated: {guid_to_use}"
            )
            self.stats.new_lines_processed += 1
            # Assuming GUID is in column A for the update range
            guid_update_item = {
                "range": f"{sheet_name}!A{actual_sheet_row_num}",
                "values": [[guid_to_use]],
            }
        return guid_to_use, guid_update_item

    def _compile_tags_for_verb(
        self,
        group: Optional[str],
    ) -> List[str]:
        """Compiles a list of tags from group."""
        tags_list = ["verb"] # Base tag for all verbs

        group_val = str(group or "").strip()
        if group_val:
            tags_list.append(f"group::{group_val}".replace(" ", "\u00a0"))

        return sorted(list(set(tags_list)))

    def process_row(
        self, row: pd.Series, sheet_name: str, row_idx: int
    ) -> Tuple[Optional[Verb], Optional[Dict[str, Any]]]:
        """Process a row of verb data from the Google Sheet into a Verb object.

        Args:
            row: A pandas Series containing the row data. Expected columns:
                 GUID, English, Greek, Group, Past Simple, Past Continuous,
                 Present, Future Continuous, Future Simple.
            sheet_name: The name of the sheet being processed.
            row_idx: The 0-based index of the row in the DataFrame.

        Returns:
            A tuple containing a Verb object (or None) and an optional GUID update item.
        """
        # Ensure essential columns are present
        # "Greek" is the citation form, "English" is the translation.
        if not row.get("Greek") or not row.get("English") or not row.get("Present"):
            # Or log a warning/error, self.stats.errors.append(...)
            return None, None

        # Process GUID
        guid_cell_value = row.get("GUID") # Assumes a 'GUID' column for verbs too
        guid_to_use, guid_update_item = self._process_guid_for_row(
            guid_cell_value, row_idx, sheet_name
        )

        greek_citation_form = str(row["Greek"]).strip()
        english_translation = str(row["English"]).strip()

        # Generate sound filename and synthesize if needed
        sound_filename = ""
        if greek_citation_form:
            sound_filename = self.audio_synthesizer.generate_sound_filename(
                greek_citation_form
            )
            if sound_filename:
                self.audio_synthesizer.synthesize_if_needed(
                    greek_citation_form, sound_filename # Audio for the citation form
                )

        # Extract other verb-specific fields
        group = str(row.get("Group", "")).strip()

        # New tense fields
        present_tense = str(row.get("Present", "")).strip()
        past_simple = str(row.get("Past Simple", "")).strip()
        past_continuous = str(row.get("Past Continuous", "")).strip()
        future_continuous = str(row.get("Future Continuous", "")).strip()
        future_simple = str(row.get("Future Simple", "")).strip()

        # Compile tags
        tags = self._compile_tags_for_verb(group)

        verb = Verb(
            guid=guid_to_use,
            english=english_translation,
            greek_citation=greek_citation_form,
            group=group or None,
            present_tense=present_tense or None,
            past_simple=past_simple or None,
            past_continuous=past_continuous or None,
            future_continuous=future_continuous or None,
            future_simple=future_simple or None,
            sound=sound_filename,
            tags=tags,
        )
        # print(f"Processed Verb: {verb.greek_citation}") # Optional: for debugging
        return verb, guid_update_item
