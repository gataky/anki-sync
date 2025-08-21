import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class Config:
    """Centralized configuration for Anki Sync application."""

    # User and Anki settings
    user: str = "User 1"
    anki_base_path: Path = Path.home() / "Library/Application Support/Anki2"

    # API credentials and endpoints
    google_sheet_id: str = os.environ.get("GOOGLE_SHEET_ID", "")
    google_application_credentials: str = os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS", ""
    )
    google_api_key: str = os.environ.get("GOOGLE_API_KEY", "")
    elevenlabs_api_key: str = os.environ.get("ELEVENLABS_API_KEY", "")

    # Audio synthesis settings
    audio_synthesizer: Literal["elevenlabs", "google"] = "elevenlabs"

    # Performance settings
    max_workers: int = 3
    chunk_size: int = 1000

    # Output settings
    output_filename: str = "greek.apkg"

    @property
    def anki_path(self) -> Path:
        """Get the full Anki user directory path."""
        return self.anki_base_path / self.user

    @property
    def anki_db_path(self) -> Path:
        """Get the Anki collection database path."""
        return self.anki_path / "collection.anki2"

    @property
    def anki_media_path(self) -> Path:
        """Get the Anki media directory path."""
        return self.anki_path / "collection.media"

    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        errors = []

        if not self.google_sheet_id:
            errors.append("GOOGLE_SHEET_ID environment variable is required")

        if not self.google_application_credentials:
            errors.append(
                "GOOGLE_APPLICATION_CREDENTIALS environment variable is required"
            )

        if self.audio_synthesizer == "elevenlabs" and not self.elevenlabs_api_key:
            errors.append(
                "ELEVENLABS_API_KEY environment variable is required for ElevenLabs synthesizer"
            )

        if not self.anki_path.exists():
            errors.append(f"Anki path does not exist: {self.anki_path}")

        if not self.anki_db_path.exists():
            errors.append(f"Anki database does not exist: {self.anki_db_path}")

        if errors:
            print("Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True

    def print_config(self) -> None:
        """Print current configuration for debugging."""
        print("Current Configuration:")
        print(f"  User: {self.user}")
        print(f"  Anki Path: {self.anki_path}")
        print(f"  Database: {self.anki_db_path}")
        print(f"  Media: {self.anki_media_path}")
        print(f"  Google Sheet ID: {self.google_sheet_id}")
        print(f"  Audio Synthesizer: {self.audio_synthesizer}")
        print(f"  Max Workers: {self.max_workers}")
        print(f"  Chunk Size: {self.chunk_size}")
        print(f"  Output File: {self.output_filename}")


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def update_config(**kwargs) -> None:
    """Update configuration values."""
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            print(f"Warning: Unknown configuration key '{key}'")


def load_config_from_env() -> None:
    """Load configuration from environment variables."""
    update_config(
        google_sheet_id=os.environ.get("GOOGLE_SHEET_ID", config.google_sheet_id),
        google_application_credentials=os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS", config.google_application_credentials
        ),
        google_api_key=os.environ.get("GOOGLE_API_KEY", config.google_api_key),
        elevenlabs_api_key=os.environ.get(
            "ELEVENLABS_API_KEY", config.elevenlabs_api_key
        ),
        audio_synthesizer=os.environ.get("AUDIO_SYNTHESIZER", config.audio_synthesizer),
        max_workers=int(os.environ.get("MAX_WORKERS", config.max_workers)),
        chunk_size=int(os.environ.get("CHUNK_SIZE", config.chunk_size)),
        output_filename=os.environ.get("OUTPUT_FILENAME", config.output_filename),
    )
