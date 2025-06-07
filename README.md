# Anki-Sync: Google Sheets to Anki Deck Generator

Anki-Sync is a Python CLI tool designed to streamline the creation of Anki flashcard decks from vocabulary and verb data stored in Google Sheets. It processes your data, handles audio generation, and produces a combined Anki package (`.apkg`) file ready for import.

## Features

*   **Unified Syncing:** A single command processes both general vocabulary words and detailed verb conjugations from your Google Sheet.
*   **Combined Anki Deck:** Generates one Anki deck containing both words and verbs, using distinct Anki Note Types for clear structural separation.
    *   **Words:** Includes English, Greek (with optional article prefixing based on gender), class, gender, and sound.
    *   **Verbs:** Includes English, Greek citation form, group, various tenses (Present, Past Simple, Past Continuous, Future Simple, Future Continuous), and sound. Verb cards feature a styled table for tenses.
*   **Automatic GUID Management:** Assigns a unique ID (GUID) to each new entry and writes it back to your Google Sheet, ensuring consistent updates and preventing duplicates in Anki.
*   **Audio Synthesis:** Supports text-to-speech audio generation for Greek words/verbs using:
    *   ElevenLabs
    *   Google Cloud Text-to-Speech
*   **Hierarchical Tagging:** Automatically generates hierarchical tags for words based on columns like "Category", "Sub-Category", etc., in your "Words" sheet. Verbs are tagged by their group.
*   **Customizable Anki Models:** Uses distinct, customizable Anki models for words and verbs, allowing for different card layouts and fields.
*   **Environment Variable Configuration:** Simplifies setup by allowing configuration through environment variables.

## Prerequisites

1.  **Python:** Python 3.8 or higher.
2.  **Google Cloud Project:**
    *   A Google Cloud Platform (GCP) project with the **Google Sheets API** enabled.
    *   Service Account credentials (a JSON key file) for accessing your Google Sheet.
3.  **Google Sheet:** A Google Spreadsheet with at least two sheets named:
    *   `Words` (for general vocabulary)
    *   `Verbs` (for verb conjugations)
    *   Ensure your service account has edit access to this spreadsheet.
4.  **(Optional) Audio Synthesizer Setup:**
    *   **ElevenLabs:** An ElevenLabs API key if you choose to use their service.
    *   **Google TTS:** Your Google Cloud project should also have the Text-to-Speech API enabled, and your service account should have permissions for it.

## Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <your-repository-url>
    cd anki-sync
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure you have a `requirements.txt` file listing dependencies like `click`, `pandas`, `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`, `genanki`, `pydantic` etc.)*

## Configuration

Set the following environment variables:

*   `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google Cloud service account JSON key file.
    *   Example: `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"`
*   `GOOGLE_SHEET_ID`: The ID of your Google Spreadsheet.
    *   You can find this in the URL of your sheet: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`
    *   Example: `export GOOGLE_SHEET_ID="your_actual_sheet_id"`
*   `ANKI_DECK_NAME`: The desired name for the Anki deck that will be generated.
    *   Example: `export ANKI_DECK_NAME="My Greek Study Deck"`
*   `ANKI_AUDIO_DIRECTORY` (Optional): Absolute path to the directory where audio files will be stored locally and from where they will be packaged into the Anki deck. This should typically be your Anki `collection.media` folder if you want Anki to find them immediately after import, but can be any directory.
    *   Example: `export ANKI_AUDIO_DIRECTORY="/path/to/anki/user/collection.media"`
*   `ELEVENLABS_API_KEY` (Optional): Your API key for ElevenLabs, if using that synthesizer.
    *   Example: `export ELEVENLABS_API_KEY="your_elevenlabs_api_key"`

## Google Sheet Structure

The tool expects specific sheet names and column headers.

### 1. "Words" Sheet

| GUID (A)                      | English (B)      | Greek (C)   | Class (D)  | Gender (E)      | Category (F) | Sub-Category (G) | ... (More tag columns) |
| :---------------------------- | :--------------- | :---------- | :--------- | :-------------- | :----------- | :--------------- | :--------------------- |
| (Leave blank for new entries) | e.g., The house  | e.g., σπίτι | e.g., Noun | e.g., Neuter    | e.g., Unit 1 | e.g., Chapter A  | ...                    |
| ...                           | ...              | ...         | ...        | ...             | ...          | ...              | ...                    |

*   **GUID:** Unique Identifier. Will be auto-generated and written back if empty.
*   **English:** English translation.
*   **Greek:** Greek word. Articles will be prefixed based on the "Gender" column.
*   **Class:** Word class (e.g., Noun, Adjective). Used for tagging.
*   **Gender:** (e.g., masculine, feminine, neuter, masculine pl., feminine pl., neuter pl.). Used for article prefixing and tagging.
*   **Category, Sub-Category, etc.:** These columns (from "Category" onwards) are used to generate hierarchical Anki tags (e.g., `Category::Unit 1`, `Category::Unit 1::Chapter A`).

### 2. "Verbs" Sheet

| GUID (A)                      | English (B)   | Greek (C)         | Group (D) | Past Simple (E) | Past Continuous (F) | Present (G) | Future Continuous (H) | Future Simple (I) |
| :---------------------------- | :------------ | :---------------- | :-------- | :-------------- | :------------------ | :---------- | :-------------------- | :---------------- |
| (Leave blank for new entries) | e.g., To read | e.g., διαβάζω (I) | e.g., A   | e.g., διάβασα   | e.g., διάβαζα       | e.g., διαβάζω | e.g., θα διαβάζω      | e.g., θα διαβάσω  |
| ...                           | ...           | ...               | ...       | ...             | ...                 | ...         | ...                   | ...               |

*   **GUID:** Unique Identifier. Will be auto-generated and written back if empty.
*   **English:** English meaning of the verb.
*   **Greek:** The main citation form of the Greek verb (e.g., present tense, 1st person singular). This form is used for audio generation.
*   **Group:** Verb group (e.g., A, B1). Used for tagging.
*   **Past Simple, Past Continuous, Present, Future Continuous, Future Simple:** The respective conjugated forms of the verb.

## Usage

The primary command is `sync`.

```bash
python -m anki_sync.cli sync [OPTIONS]
