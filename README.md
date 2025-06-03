# Anki Sync

A CLI tool to synchronize words from Google Sheets to Anki, with optional audio synthesis.

## Installation

```bash
pip install anki-sync
```

## Requirements

1. Google Cloud Project with:
   - Google Sheets API enabled
   - Service account with Sheets access
   - Service account key JSON file

2. ElevenLabs API key (for audio synthesis)

3. Environment Variables:
   ```bash
   # Google Sheets
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
   export GOOGLE_SHEET_ID="your-sheet-id"
   export GOOGLE_SHEET_NAME="Sheet1"  # Optional, defaults to "Words"

   # Anki
   export ANKI_DECK_NAME="Your Deck Name"
   export ANKI_AUDIO_DIRECTORY="/path/to/audio/files"  # Optional
   ```

## Usage

```bash
# Basic usage
anki-sync sync

# With custom options
anki-sync sync \
  --sheet-id "your-sheet-id" \
  --sheet-name "Sheet1" \
  --deck-name "Your Deck Name" \
  --output-file "output.apkg" \
  --anki-audio-directory "/path/to/audio" \
  --synthesizer elevenlabs  # or google
```

All options are optional if you have environment variables set. Otherwise you can override when running the script.

## Google Sheet Format

Required columns:
1. GUID (auto-generated if empty)
2. English
3. Greek
4. Word Class
5. Gender
6. Tags (optional)

## Output

The script will:
1. Read words from Google Sheets
2. Generate audio files (if enabled)
3. Create an Anki package (.apkg)
4. Display statistics about the process
