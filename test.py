import io
import os
from pathlib import Path
import pandas as pd
import logging
from anki_sync.core.gemini_client import GeminiClient, GeminiAuthError, GeminiQueryError
from anki_sync.core.gsheets import GoogleSheetsManager

# Configure basic logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---

if __name__ == "__main__":
    logger.info("Starting Gemini API query script using GeminiClient...")
    try:
        sheets = GoogleSheetsManager(
            os.environ.get("GOOGLE_SHEET_ID"), None
        )
        client = GeminiClient()

        data = sheets.get_sheet_data("Verbs")

        data["Learning"] = pd.to_numeric(data["Learning"])
        data["Processed"] = pd.to_numeric(data["Processed"])

        verbs = data[(data["Learning"] == 1) & (data["Processed"] != 1)]

        column_names = [
            'Conjugated',
            'English',
            'Greek Sentence',
            'English Sentence',
            'Tense',
            'Person',
            'Number'
        ]

        conjugated = []
        for i, verb in verbs.iterrows():
            lex = verb["Greek"]

            resp = client.query(lex)
            csv_data_string = "\n".join(resp.split("\n")[1:-1])
            csv_file_object = io.StringIO(csv_data_string)

            df = pd.read_csv(csv_file_object, header=None, names=column_names)
            df.insert(loc=0, column="Verb", value=lex)
            conjugated.append(df)

        all = pd.concat(conjugated)
        clean = all[all['Conjugated'] != '```']

        clean.to_csv('output.csv')


    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}", exc_info=True)
    except GeminiAuthError as e:
        logger.error(f"Authentication/Configuration error with Gemini: {e}", exc_info=True)
    except GeminiQueryError as e:
        logger.error(f"Error during Gemini API query: {e}", exc_info=True)
    except Exception as e: # Catch-all for other unexpected errors
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
