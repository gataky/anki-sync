# Anik-Sync: Google Sheets to Anki Vocabulary Synchronizer

Anik-Sync is a Python tool designed to streamline the process of creating Anki flashcards for language learning, specifically tailored for Greek vocabulary. It reads vocabulary data from a Google Sheet, processes it (including prepending articles and generating tags), synthesizes audio for new Greek words using Google Cloud Text-to-Speech, and prepares the data for easy integration with Anki.

## Features

*   **Google Sheets Integration**: Reads vocabulary entries directly from a specified Google Sheet.
*   **Automatic GUID Generation**: Assigns unique identifiers (GUIDs) to new vocabulary entries and writes them back to the sheet for persistent tracking.
*   **Greek Article Prepending**: Automatically prepends the correct Greek definite article (ο, η, το, οι, τα) to Greek nouns based on their specified gender.
*   **Audio Synthesis**: Generates MP3 audio files for Greek words using Google Cloud Text-to-Speech if they don't already exist in your specified sound directory. The generated audio uses a standard Greek female voice.
*   **Structured Tagging**:
    *   Automatically tags entries with their word class (e.g., `class::noun`, `class::verb`).
    *   Tags entries with their base gender (e.g., `class::masculine`, `class::feminine`).
    *   Supports hierarchical tagging from designated columns in your spreadsheet (e.g., `Chapter1`, `Chapter1::Lesson2`).
    *   Replaces spaces in tag components with NO-BREAK SPACEs (`\u00A0`) for better Anki compatibility.
*   **Data Validation**: Skips malformed rows (e.g., missing essential English, Greek, or Class data) and logs errors.
*   **Efficient Batch Updates**: Writes all new GUIDs back to the Google Sheet in a single API call.

## Prerequisites

*   Python 3.8+
*   Poetry (for dependency management - recommended) or pip
*   A Google Cloud Platform (GCP) account
*   Anki (desktop application, for using the generated media and data)

## Setup

### 1. Clone the Repository
   ```bash
   git clone <your-repository-url> # Replace <your-repository-url> with the actual URL
   cd anik-sync
   ```

### 2. Install Dependencies
   It's recommended to use Poetry for managing dependencies.
   ```bash
   poetry install
   ```
   This will install necessary libraries such as `google-api-python-client`, `google-cloud-texttospeech`, and `google-auth`.

### 3. Google Cloud Platform Setup
   a. **Create a Service Account**:
      *   Go to the GCP Console -> IAM & Admin -> Service Accounts.
      *   Create a new service account.
      *   Grant it the following roles:
          *   "Google Sheets API" -> "Sheets Editor" (to read data and write back GUIDs).
          *   "Cloud Text-to-Speech API" -> "Cloud Text-to-Speech User" (or a role that allows `synthesize_speech`).
      *   Create a key for this service account (JSON format) and download it securely.

   b. **Enable APIs**:
      *   In the GCP Console, go to APIs & Services -> Library.
      *   Search for and enable the following APIs for your project:
          *   Google Sheets API
          *   Cloud Text-to-Speech API

### 4. Environment Variables
   Set the following environment variables in your shell or `.env` file (if your CLI tool supports it):

   *   `GOOGLE_APPLICATION_CREDENTIALS`: Set this to the absolute path of the JSON key file you downloaded for your service account.
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
     ```

   *   `SOUND_DIR`: Set this to the absolute path of the directory where generated audio files should be saved. This is typically your Anki user's `collection.media` directory.
     ```bash
     # Example for macOS, default Anki profile "User 1":
     export SOUND_DIR="$HOME/Library/Application Support/Anki2/User 1/collection.media"
     # Adjust for your OS and Anki profile name if different.
     # Windows example: %APPDATA%\Anki2\User 1\collection.media
     # Linux example: ~/.local/share/Anki2/User 1/collection.media
     ```
   To make these persistent, add the `export` commands to your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`, `~/.profile`).

## Spreadsheet Format

Your Google Sheet should be structured with the following columns, starting from Column A. The script assumes the first row (Row 1) contains headers and data processing begins from the second row (Row 2).

*   **Column A: GUID** (Leave blank for new entries; the script will populate this with a unique ID)
*   **Column B: English** (The English translation or meaning of the word)
*   **Column C: Greek** (The Greek word, *without* the definite article initially. The script will add it based on gender)
*   **Column D: Class** (The word class, e.g., "noun", "verb", "adjective", "adverb")
*   **Column E: Gender** (For nouns, specify the gender. Expected values: "masculine", "feminine", "neuter", "masculine pl.", "feminine pl.", "neuter pl.")
*   **Column F onwards: Hierarchical Tags**
    *   Column F: Top-level tag (e.g., "Chapter1", "UnitA", "Topic_Colors").
    *   Column G: Sub-tag (e.g., "Lesson2"). If present, a tag like `Chapter1::Lesson2` will be created.
    *   Column H: Sub-sub-tag, and so on. The hierarchy is built by joining non-empty cells from F onwards with `::`.

## Usage

This project is designed to be run as a command-line interface (CLI) tool. The exact command will depend on the main entry point of your application (e.g., a `main.py` or `cli.py` file that uses a library like `click`).

A hypothetical invocation (assuming your CLI is set up) might be:

```bash
poetry run anik-sync --sheet-id YOUR_GOOGLE_SHEET_ID --sheet-name "NameOfYourSheetPage"
```

*   Replace `YOUR_GOOGLE_SHEET_ID` with the ID of your Google Spreadsheet (found in its URL).
*   Replace `"NameOfYourSheetPage"` with the actual name of the sheet tab containing your vocabulary.

The script will then:
1.  Connect to your Google Sheet.
2.  Read vocabulary data starting from row 2.
3.  For each valid row:
    *   Generate a GUID if one is missing.
    *   Generate an MP3 audio file for the Greek word (from Column C) if it doesn't already exist in `SOUND_DIR`. The filename will be `GreekWord.mp3`.
    *   Prepend the appropriate Greek definite article to the Greek word based on the gender in Column E.
    *   Compile a list of tags based on Columns D, E, and F+.
4.  Write any newly generated GUIDs back to Column A of your Google Sheet.
5.  The processed data (including GUIDs, modified Greek words, sound filenames, and tags) is then available for further steps to create Anki notes (e.g., generating a CSV for Anki import or using an AnkiConnect-like API, which would be a separate part of your workflow).

## How Audio Generation Works

*   The script uses the original Greek word (from Column C of your sheet) to name the audio file (e.g., if Column C is "λέξη", the file will be "λέξη.mp3").
*   It checks if a file with this name already exists in the directory specified by the `SOUND_DIR` environment variable.
*   If the file is missing and the Google Cloud Text-to-Speech client is initialized successfully, it calls the API to generate the audio and saves it to `SOUND_DIR`.
*   The `sound_file` field in the processed data will then contain this filename (e.g., "λέξη.mp3"). In Anki, you would typically use this in a card template like `[sound:{{SoundFileField}}]`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

MIT
<!-- Or your preferred license -->
