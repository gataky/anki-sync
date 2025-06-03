from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Stats:
    """Tracks statistics for the sync process.

    This class collects and tracks various metrics during the synchronization
    process, including line counts, audio generation, and error tracking.
    """

    total_lines_read: int = 0
    total_lines_processed: int = 0
    new_lines_processed: int = 0
    audio_files_generated: int = 0
    errors: Dict[str, int] = field(default_factory=dict)

    def print_summary(self) -> None:
        """Prints a summary of the collected statistics.

        Displays:
        - Total lines read from the sheet
        - Total lines successfully processed
        - Number of new lines (those without GUIDs)
        - Number of audio files generated
        - Any errors encountered during the process
        """
        print("\nSync Statistics:")
        print(f"  Total lines read: {self.total_lines_read}")
        print(f"  Total lines processed: {self.total_lines_processed}")
        print(f"  New lines (no GUID): {self.new_lines_processed}")
        print(f"  Audio files generated: {self.audio_files_generated}")

        if self.errors:
            print("\nErrors encountered:")
            for error_type, count in self.errors.items():
                print(f"  {error_type}: {count}")
