from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from anki_sync.utils.guid import generate_guid

from .synthesizers.audio_synthesizer import AudioSynthesizer
from .models import Word


class WordProcessor:
    """Processes word data from Google Sheets into Word objects.

    This class handles the processing of raw word data from Google Sheets,
    including article handling, tag generation, and audio synthesis.
    """

    GENDER_TO_ARTICLE_MAP = {
        "masculine": "ο",
        "feminine": "η",
        "neuter": "το",
        "masculine pl.": "οι",
        "feminine pl.": "οι",  # Note: feminine pl. is also οι
        "neuter pl.": "τα",
        None: "",  # If there is no gender then return an empty string.
    }

    def __init__(self, audio_synthesizer: AudioSynthesizer) -> None:
        """Initialize the WordProcessor with required dependencies.

        Args:
            audio_synthesizer: Instance of AudioSynthesizer for handling audio generation
        """
        self.audio_synthesizer = audio_synthesizer

    def _process_guid_for_row(
        self, guid_cell_value: Any, row_idx: int, sheet_name: str
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Processes the GUID for a row. Uses existing GUID or generates a new one."""
        guid_to_use = str(guid_cell_value or "").strip()
        guid_update_item = None
        if not guid_to_use:
            new_guid_value = generate_guid()
            guid_to_use = new_guid_value
            actual_sheet_row_num = row_idx + 2
            print(
                f"Info: Row {actual_sheet_row_num} in sheet '{sheet_name}' is missing GUID. Generated: {guid_to_use}"
            )
            guid_update_item = {
                "range": f"{sheet_name}!A{actual_sheet_row_num}",
                "values": [[guid_to_use]],
            }
        return guid_to_use, guid_update_item

    def _prefix_article_to_greek_word(
        self, original_greek_word: str, gender_string_for_article: str
    ) -> str:
        """Prefixes the correct Greek article to the Greek word based on gender."""
        processed_greek_word = original_greek_word
        if gender_string_for_article and original_greek_word:
            article = self.GENDER_TO_ARTICLE_MAP.get(gender_string_for_article, "")
            if article:
                processed_greek_word = f"{article} {original_greek_word}"
        return processed_greek_word

    def _compile_tags_for_word(
        self,
        raw_class: Optional[str],
        original_gender_from_sheet: Optional[str],
        hierarchical_tag_cells: List[Any],
    ) -> List[str]:
        """Compiles a list of tags from class, gender, and hierarchical columns."""
        tags_list = []
        class_tag_value = str(raw_class or "").strip()
        if class_tag_value:
            tags_list.append(f"class::{class_tag_value}".replace(" ", "\u00a0"))

        gender_tag_value = str(original_gender_from_sheet or "").strip()
        if gender_tag_value:
            gender_base_tag = gender_tag_value.split(" ")[0]
            tags_list.append(f"gender::{gender_base_tag}".replace(" ", "\u00a0"))

        current_hierarchy_parts = []
        for cell_content_raw in hierarchical_tag_cells:
            cell_content = str(cell_content_raw or "").strip()
            if not cell_content:
                break
            current_hierarchy_parts.append(cell_content.replace(" ", "\u00a0"))
            tags_list.append("::".join(current_hierarchy_parts))
        return sorted(list(set(tags_list)))

    def process_row(self, row: pd.Series) -> Optional[Word]:
        """Process a row of data from the Google Sheet into a Word object.

        Args:
            row: A pandas Series containing the row data with columns:
                - Greek: The Greek word
                - English: The English translation
                - Gender: Optional gender to determine article
                - Class: Optional word class
                - Category and onwards: Hierarchical tags

        Returns:
            A Word object if the row contains valid data, None otherwise
        """

        # Skip if no Greek word
        if not row.get("Greek"):
            return None

        original_greek_word = row["Greek"].strip()
        processed_greek_word = original_greek_word

        # Handle article based on gender
        if row.get("Gender"):
            gender = row["Gender"].strip().lower()
            article = self.GENDER_TO_ARTICLE_MAP.get(gender, "")
            if article and not processed_greek_word.startswith(article):
                processed_greek_word = f"{article} {processed_greek_word}"

        # Generate sound filename and synthesize if needed
        sound_filename = self.audio_synthesizer.generate_sound_filename(
            original_greek_word
        )
        if sound_filename:
            self.audio_synthesizer.synthesize_if_needed(
                processed_greek_word, sound_filename
            )

        # Process tags using hierarchical tag system
        # Get all columns from Category onwards
        category_index = row.index.get_loc("Category") if "Category" in row.index else -1
        hierarchical_tag_cells = row.iloc[category_index:].tolist() if category_index >= 0 else []

        tags = self._compile_tags_for_word(
            row.get("Class"),
            row.get("Gender"),
            hierarchical_tag_cells,
        )

        word = Word(
            greek=processed_greek_word,
            english=row["English"].strip(),
            sound=sound_filename or "",
            tags=tags,
            word_class=row.get("Class", ""),
            gender=row.get("Gender"),
        )
        print(word)
        return word
