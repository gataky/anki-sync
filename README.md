# Anki-Sync

A Python CLI tool for synchronizing Greek vocabulary data from Google Sheets to Anki flashcards. This tool automatically processes nouns, adjectives, and verb conjugations, generates audio files, and creates comprehensive Anki decks with proper declension tables and audio support.

## ✨ Recent Updates & Optimizations

### 🚀 Performance Improvements
- **Database Connection Optimization**: Fixed redundant database connections and improved connection management
- **Audio File Caching**: Implemented efficient audio file existence checking
- **Batch Operations**: Added support for batch Google Sheets operations
- **Memory Optimization**: Improved pandas DataFrame handling with optimized data types

### ⚙️ Configuration Management
- **Centralized Configuration**: New `config.py` system for all application settings
- **Environment Variable Support**: Easy configuration via environment variables
- **Automatic Validation**: Built-in configuration validation and error checking
- **Flexible Settings**: Easy to customize performance, audio, and output options

### 🏗️ Architecture Improvements
- **Module Reorganization**: Resolved circular imports and improved code structure
- **Separation of Concerns**: Moved Note, Card, and Rev classes to dedicated modules
- **Better Error Handling**: Enhanced error messages and validation
- **Code Maintainability**: Cleaner, more organized codebase

## Features

- **Multi-word type support**: Handles nouns, adjectives, and verb conjugations
- **Automatic audio synthesis**: Generates audio files using ElevenLabs or Google Cloud TTS
- **Declension tables**: Automatically generates HTML declension tables for nouns and adjectives
- **Google Sheets integration**: Reads vocabulary data directly from Google Sheets
- **Anki database integration**: Syncs with existing Anki collections and maintains note IDs
- **GUID management**: Automatically generates and tracks unique identifiers for notes
- **Tag hierarchy**: Creates organized tag hierarchies for easy deck organization
- **Configuration Management**: Centralized settings with environment variable support
- **Performance Optimization**: Efficient database operations and audio processing

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
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"

# Optional (for ElevenLabs TTS)
export ELEVENLABS_API_KEY="your-elevenlabs-api-key"

# Optional (for Google Cloud TTS)
export GOOGLE_API_KEY="your-google-api-key"

# Performance and Output Configuration
export AUDIO_SYNTHESIZER="elevenlabs"  # or "google"
export MAX_WORKERS=3
export CHUNK_SIZE=1000
export OUTPUT_FILENAME="greek.apkg"
```

4. Set up Google Sheets API:
   - Create a Google Cloud project
   - Enable Google Sheets API and Google Cloud Text-to-Speech API
   - Create service account credentials
   - Share your Google Sheet with the service account email

## Configuration

The application now uses a centralized configuration system. See [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options.

### Quick Configuration Commands

```bash
# Show current configuration
python -m anki_sync.cli config

# Sync with current configuration
python -m anki_sync.cli sync
```

## Google Sheets Structure

The tool expects specific sheet names and column structures. The current implementation uses a simplified structure focused on essential vocabulary information rather than detailed declension tables.

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
| definitions | Word definitions | No |
| synonyms | Synonyms | No |
| antonyms | Antonyms | No |
| etymology | Word origin | No |
| notes | Additional notes | No |

### Adjectives Sheet
| Column | Description | Required |
|--------|-------------|----------|
| GUID | Unique identifier (auto-generated if empty) | No |
| English | English translation | Yes |
| Greek | Greek word | Yes |
| tag | Primary category tag | No |
| sub tag 1 | Secondary category tag | No |
| sub tag 2 | Tertiary category tag | No |
| definitions | Word definitions | No |
| synonyms | Synonyms | No |
| antonyms | Antonyms | No |
| etymology | Word origin | No |
| notes | Additional notes | No |

### Adverbs Sheet
| Column | Description | Required |
|--------|-------------|----------|
| GUID | Unique identifier (auto-generated if empty) | No |
| English | English translation | Yes |
| Greek | Greek word | Yes |
| tag | Primary category tag | No |
| sub tag 1 | Secondary category tag | No |
| sub tag 2 | Tertiary category tag | No |
| definitions | Word definitions | No |
| synonyms | Synonyms | No |
| antonyms | Antonyms | No |
| etymology | Word origin | No |
| notes | Additional notes | No |

### Prepositions Sheet
| Column | Description | Required |
|--------|-------------|----------|
| GUID | Unique identifier (auto-generated if empty) | No |
| English | English translation | Yes |
| Greek | Greek word | Yes |
| tag | Primary category tag | No |
| sub tag 1 | Secondary category tag | No |
| sub tag 2 | Tertiary category tag | No |
| definitions | Word definitions | No |
| synonyms | Synonyms | No |
| antonyms | Antonyms | No |
| etymology | Word origin | No |
| notes | Additional notes | No |

### Conjunctions Sheet
| Column | Description | Required |
|--------|-------------|----------|
| GUID | Unique identifier (auto-generated if empty) | No |
| English | English translation | Yes |
| Greek | Greek word | Yes |
| tag | Primary category tag | No |
| sub tag 1 | Secondary category tag | No |
| sub tag 2 | Tertiary category tag | No |
| definitions | Word definitions | No |
| synonyms | Synonyms | No |
| antonyms | Antonyms | No |
| etymology | Word origin | No |
| notes | Additional notes | No |

### Verbs Conjugated Sheet
| Column | Description | Required |
|--------|-------------|----------|
| GUID | Unique identifier (auto-generated if empty) | No |
| English | English translation | Yes |
| Greek | Greek word | Yes |
| tag | Primary category tag | No |
| sub tag 1 | Secondary category tag | No |
| sub tag 2 | Tertiary category tag | No |
| definitions | Word definitions | No |
| synonyms | Synonyms | No |
| antonyms | Antonyms | No |
| etymology | Word origin | No |
| notes | Additional notes | No |

### Tag System

The tool uses a hierarchical tag system for organizing vocabulary:

- **Primary tags** (`tag` column): Main category (e.g., "animals", "food", "family")
- **Secondary tags** (`sub tag 1` column): Subcategory (e.g., "mammals", "fruits", "relatives")
- **Tertiary tags** (`sub tag 2` column): Specific group (e.g., "domestic", "tropical", "immediate")

Tags are automatically processed and converted into Anki tag hierarchies (e.g., "animals::mammals::domestic").

### Note Fields

Each word type generates an Anki note with the following fields:
1. **English**: English translation
2. **Greek**: Greek word
3. **Audio Filename**: Generated audio file reference
4. **Part of Speech**: Grammatical category with gender (for nouns/adjectives)
5. **Definitions**: Word definitions
6. **Synonyms**: Related words
7. **Antonyms**: Opposite words
8. **Etymology**: Word origin
9. **Notes**: Additional information

## Usage

### Basic Sync

The main command synchronizes all vocabulary from Google Sheets to Anki:

```bash
poetry run anki-sync sync
```

Or using the module directly:

```bash
python -m anki_sync.cli sync
```

This command will:
1. Load and validate configuration from environment variables
2. Read data from the configured sheets (nouns, adjectives, verbs conjugated)
3. Generate audio files for Greek words using the configured TTS service
4. Create declension tables for nouns and adjectives
5. Generate an Anki package file with the configured filename
6. Update Google Sheets with any newly generated GUIDs

### Configuration Management

```bash
# View current configuration
python -m anki_sync.cli config

# The sync command automatically:
# - Loads configuration from environment variables
# - Validates all required settings
# - Uses optimized performance parameters
# - Applies audio synthesis preferences
```

### Audio Synthesis

The tool supports two TTS providers:

1. **ElevenLabs** (default): High-quality, multilingual TTS, requires API key
2. **Google Cloud TTS**: Alternative TTS service, requires Google Cloud credentials

Audio files are automatically generated and included in the Anki package.

## Project Structure

```
anki-sync/
├── anki_sync/
│   ├── cli.py                 # Main CLI interface with configuration support
│   ├── config.py              # Centralized configuration management
│   ├── core/
│   │   ├── auth/             # Google authentication
│   │   │   └── auth.py       # Google and ElevenLabs auth
│   │   ├── models/           # Data models for different word types
│   │   │   ├── constants.py  # Anki note model constants
│   │   │   ├── word.py       # Base word models and implementations
│   │   │   ├── note.py       # Anki note, card, and revision models
│   │   │   ├── genanki.py    # Deck generation and management
│   │   │   └── audio.py      # Audio metadata models
│   │   ├── synthesizers/     # Audio synthesis
│   │   │   ├── base.py       # Base synthesizer interface
│   │   │   ├── google.py     # Google Cloud TTS
│   │   │   ├── elevenlabs.py # ElevenLabs TTS
│   │   │   └── audio_synthesizer.py # Main audio manager
│   │   ├── gsheets.py        # Google Sheets integration (optimized)
│   │   └── sql.py            # Anki database integration (optimized)
│   └── utils/
│       └── guid.py           # GUID generation utilities
├── scripts/
│   ├── process.py            # Data processing utilities
│   ├── exp.py                # Export utilities
│   ├── ipa.py                # IPA processing
│   └── lint.bash             # Code linting script
├── tests/                    # Test suite
├── CONFIGURATION.md          # Detailed configuration guide
└── pyproject.toml           # Project dependencies and metadata
```

## Performance Optimizations

### Database Operations
- **Connection Management**: Optimized database connection handling
- **Batch Operations**: Support for batch note lookups
- **Memory Efficiency**: Chunked processing and optimized data types
- **Query Optimization**: Efficient SQL queries with proper indexing

### Audio Processing
- **File Caching**: Efficient audio file existence checking
- **Batch Synthesis**: Support for parallel audio generation
- **Error Handling**: Graceful fallback for synthesis failures

### Google Sheets Integration
- **Client Caching**: Reuse Google Sheets client connections
- **Batch Operations**: Fetch multiple sheets in single API calls
- **Error Recovery**: Robust error handling for network issues

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

# Check configuration
python -m anki_sync.cli config
```

### Adding New Word Types

To add support for new word types:

1. Create a new model in `anki_sync/core/models/word.py`
2. Inherit from `BaseWord`
3. Implement required methods: `to_note()`, `get_audio_meta()`
4. Add the model to the CLI sync command
5. Update Google Sheets structure documentation

### Configuration Extensions

To add new configuration options:

1. Add new fields to the `Config` class in `config.py`
2. Update the `load_config_from_env()` function
3. Add validation rules in the `validate()` method
4. Update documentation in `CONFIGURATION.md`

## Troubleshooting

### Common Issues

1. **Configuration Validation Errors**: Use `python -m anki_sync.cli config` to check settings
2. **Google Sheets API errors**: Ensure your service account has access to the sheet
3. **Audio synthesis failures**: Check API keys and network connectivity
4. **Anki database not found**: Verify Anki installation path and user profile
5. **Missing GUIDs**: The tool will automatically generate GUIDs for new entries

### Debug Mode

Enable debug logging by setting the log level:

```bash
export PYTHONPATH=.
python -m anki_sync.cli sync
```

### Configuration Issues

```bash
# Check configuration status
python -m anki_sync.cli config

# Common configuration problems:
# - Missing GOOGLE_SHEET_ID
# - Invalid GOOGLE_APPLICATION_CREDENTIALS path
# - Missing API keys for selected synthesizer
# - Incorrect Anki user profile path
```

## Migration Guide

### From Previous Versions

If you're upgrading from a previous version:

1. **Environment Variables**: Update your environment variables to use the new configuration system
2. **CLI Commands**: The sync command now automatically loads configuration
3. **Performance**: Enjoy improved performance with the new optimizations
4. **Configuration**: Use the new `config` command to verify your settings

### Configuration Changes

- **Before**: Hardcoded paths and settings in `cli.py`
- **After**: Centralized configuration with environment variable support
- **Benefits**: Easier deployment, better error handling, flexible configuration

## License

[Add your license information here]

## Acknowledgments

- Uses `genanki` for Anki package generation
- Uses `modern-greek-inflexion` for declension generation
- Uses Google Cloud TTS and ElevenLabs for audio synthesis
- Built with modern Python best practices and performance optimization
