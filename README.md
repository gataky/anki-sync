# Anki-Sync

A Python CLI tool for synchronizing Greek vocabulary data from Google Sheets to Anki flashcards. This tool automatically processes nouns, adjectives, and verb conjugations, generates audio files, and creates comprehensive Anki decks with proper declension tables and audio support.

## Features

- **Multi-word type support**: Handles nouns, adjectives, and verb conjugations
- **Automatic audio synthesis**: Generates audio files using ElevenLabs or Google Cloud TTS
- **Declension tables**: Automatically generates HTML declension tables for nouns and adjectives
- **Google Sheets integration**: Reads vocabulary data directly from Google Sheets
- **Anki database integration**: Syncs with existing Anki collections and maintains note IDs
- **GUID management**: Automatically generates and tracks unique identifiers for notes
- **Tag hierarchy**: Creates organized tag hierarchies for easy deck organization

## Installation

### Prerequisites

- Python 3.12+
- Poetry (for dependency management)
- Google Cloud credentials (for Google Sheets and TTS)
- ElevenLabs API key (optional, for alternative TTS)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd anki-sync
```

2. Install dependencies:
```bash
poetry install
```

3. Set up environment variables:
```bash
# Required
export GOOGLE_SHEET_ID="your-google-sheet-id"

# Optional (for ElevenLabs TTS)
export ELEVENLABS_API_KEY="your-elevenlabs-api-key"

# Optional (for Google Cloud TTS)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
```

4. Set up Google Sheets API:
   - Create a Google Cloud project
   - Enable Google Sheets API and Google Cloud Text-to-Speech API
   - Create service account credentials
   - Share your Google Sheet with the service account email

## Google Sheets Structure

The tool expects specific sheet names and column structures:

### Nouns Sheet
| Column | Description | Required |
|--------|-------------|----------|
| GUID | Unique identifier (auto-generated if empty) | No |
| English | English translation | Yes |
| Greek | Greek word | Yes |
| Gender | masculine/feminine/neuter | Yes |
| tag | Primary category tag | No |
| sub tag 1 | Secondary category tag | No |
| sub tag 2 | Tertiary category tag | No |
| n_s | Nominative singular | No |
| n_p | Nominative plural | No |
| a_s | Accusative singular | No |
| a_p | Accusative plural | No |
| g_s | Genitive singular | No |
| g_p | Genitive plural | No |

### Adjectives Sheet
| Column | Description | Required |
|--------|-------------|----------|
| GUID | Unique identifier (auto-generated if empty) | No |
| English | English translation | Yes |
| Greek | Greek word | Yes |
| n_s_m | Nominative singular masculine | No |
| n_s_f | Nominative singular feminine | No |
| n_s_n | Nominative singular neuter | No |
| n_p_m | Nominative plural masculine | No |
| n_p_f | Nominative plural feminine | No |
| n_p_n | Nominative plural neuter | No |
| a_s_m | Accusative singular masculine | No |
| a_s_f | Accusative singular feminine | No |
| a_s_n | Accusative singular neuter | No |
| a_p_m | Accusative plural masculine | No |
| a_p_f | Accusative plural feminine | No |
| a_p_n | Accusative plural neuter | No |
| g_s_m | Genitive singular masculine | No |
| g_s_f | Genitive singular feminine | No |
| g_s_n | Genitive singular neuter | No |
| g_p_m | Genitive plural masculine | No |
| g_p_f | Genitive plural feminine | No |
| g_p_n | Genitive plural neuter | No |

### Verbs Conjugated Sheet
| Column | Description | Required |
|--------|-------------|----------|
| GUID | Unique identifier (auto-generated if empty) | No |
| ord | Order/sequence number | Yes |
| verb | Base verb form | Yes |
| conjugated | Conjugated verb form | Yes |
| English | English translation | Yes |
| tense | Grammatical tense | Yes |
| person | Grammatical person (1st/2nd/3rd) | Yes |
| number | Grammatical number (singular/plural) | Yes |

## Usage

### Basic Sync

The main command synchronizes all vocabulary from Google Sheets to Anki:

```bash
poetry run anki-sync sync
```

This command will:
1. Read data from the "nouns", "adjectives", and "verbs conjugated" sheets
2. Generate audio files for Greek words using the configured TTS service
3. Create declension tables for nouns and adjectives
4. Generate a single Anki package file (`greek.apkg`)
5. Update Google Sheets with any newly generated GUIDs

### Configuration

The tool automatically detects your Anki installation path:
- **macOS**: `~/Library/Application Support/Anki2/User 1/`
- **Linux**: `~/.local/share/Anki2/User 1/`
- **Windows**: `%APPDATA%\Anki2\User 1\`

### Audio Synthesis

The tool supports two TTS providers:

1. **Google Cloud TTS** (default): High-quality, requires Google Cloud credentials
2. **ElevenLabs**: Alternative TTS service, requires API key

Audio files are automatically generated and included in the Anki package.

## Project Structure

```
anki-sync/
├── anki_sync/
│   ├── cli.py                 # Main CLI interface
│   ├── core/
│   │   ├── auth/             # Google authentication
│   │   ├── models/           # Data models for different word types
│   │   │   ├── base.py       # Base word model
│   │   │   ├── noun.py       # Noun model with declensions
│   │   │   ├── adjective.py  # Adjective model with declensions
│   │   │   ├── verb.py       # Verb conjugation model
│   │   │   ├── note.py       # Anki note model
│   │   │   └── deck.py       # Anki deck model
│   │   ├── synthesizers/     # Audio synthesis
│   │   │   ├── base.py       # Base synthesizer interface
│   │   │   ├── google.py     # Google Cloud TTS
│   │   │   ├── elevenlabs.py # ElevenLabs TTS
│   │   │   └── audio_synthesizer.py # Main audio manager
│   │   ├── gsheets.py        # Google Sheets integration
│   │   └── sql.py            # Anki database integration
│   └── utils/
│       ├── guid.py           # GUID generation utilities
│       └── html.py           # HTML table generation
├── scripts/
│   ├── process.py            # Data processing utilities
│   └── lint.bash             # Code linting script
└── media/                    # Generated audio files
```

## Development

### Code Quality

The project uses several tools for code quality:

```bash
# Run linting
./scripts/lint.bash

# Format code
poetry run black .
poetry run isort .

# Run tests
poetry run pytest
```

### Adding New Word Types

To add support for new word types:

1. Create a new model in `anki_sync/core/models/`
2. Inherit from `BaseWord`
3. Implement required methods: `to_note()`, `get_audio_meta()`
4. Add the model to the CLI sync command
5. Update Google Sheets structure documentation

## Troubleshooting

### Common Issues

1. **Google Sheets API errors**: Ensure your service account has access to the sheet
2. **Audio synthesis failures**: Check API keys and network connectivity
3. **Anki database not found**: Verify Anki installation path and user profile
4. **Missing GUIDs**: The tool will automatically generate GUIDs for new entries

### Debug Mode

Enable debug logging by setting the log level:

```bash
export PYTHONPATH=.
python -m anki_sync.cli sync
```

## License

[Add your license information here]

## Acknowledgments

- Uses `genanki` for Anki package generation
- Uses `modern-greek-inflexion` for declension generation
- Uses Google Cloud TTS and ElevenLabs for audio synthesis
