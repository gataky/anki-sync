#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
import json

def get_first_word(cell_text):
    """
    Extracts the first verb form from a cell.
    Handles multiple forms separated by commas or slashes, and removes annotations.
    """
    if not cell_text:
        return ""
    # Remove annotations like [1], [2], etc.
    text = re.sub(r'\[\d+\]', '', cell_text).strip()
    if not text or text == "—": # Handle empty or dash (often used for non-existent forms)
        return ""

    # Split by common delimiters for alternative forms (comma, slash)
    # and take the part before the first such delimiter.
    text = re.split(r'\s*[,/]\s*', text, 1)[0]

    return text.strip()

def extract_verb_conjugations(greek_word):
    """
    Extracts verb conjugations for a given Greek word from Wiktionary.
    """
    url = f"https://en.wiktionary.org/wiki/{greek_word}"
    headers = {
        'User-Agent': 'GeminiCodeAssist/1.0 (VerbScraper; +http://example.com/botinfo)'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    conjugation_table = None

    # 1. Try to find the Greek language section, then "Conjugation" header, then table
    header = soup.find("h4", id="Conjugation")
    if header:
        conjugation_heading_element = header.parent.find_next_sibling()
        conjugation_table = conjugation_heading_element.find("table")

        # if conjugation_heading_element:
        #     nav_frame = conjugation_heading_element.find_next_sibling("div", class_="NavFrame")
        #     if nav_frame:
        #         conjugation_table = nav_frame.find("table")
        #     else: # Sometimes table is not in NavFrame but directly after
        #         conjugation_table = conjugation_heading_element.find_next_sibling("table")

    # 2. If the above fails, fall back to the user's specific selector
    if not conjugation_table:
        print(f"Could not find conjugation table via semantic search for '{greek_word}'. Trying direct selector...")
        # Selector: "#mw-content-text > div.mw-content-ltr.mw-parser-output > div.NavFrame.notheme > div.NavContent > table"
        # BeautifulSoup's select_one is generally good with CSS selectors.
        # The provided selector has ">" which means direct child.
        # Let's make it slightly more flexible by replacing ">" with " " for descendant.
        # However, sticking to the user's exact selector first:
        user_selector = "#mw-content-text > div.mw-content-ltr.mw-parser-output > div.NavFrame.notheme > div.NavContent > table"
        conjugation_table = soup.select_one(user_selector)

    if not conjugation_table:
        print(f"Could not find conjugation table for '{greek_word}' using any method.")
        return None

    # Initialize data structure for results
    data = {
        "Present": {"Imperfective": {}},
        "Past": {"Imperfective": {}, "Perfective": {}},
        "Future": {"Imperfective": {}, "Perfective": {}}
    }

    current_tense_context = None  # Stores "Present", "Imperfect", "Aorist", "Future" from Wiktionary headers

    # Indices for "imperfective aspect" and "perfective aspect" columns within active voice
    # These are 0-indexed relative to the start of the table columns.
    active_imperfective_col_idx = -1
    active_perfective_col_idx = -1

    # Person mapping: Wiktionary table header text to (person_base, number_key)
    person_map_keys = {
        "1st sg": ("1st", "Singular"), "1st pl": ("1st", "Plural"),
        "2nd sg": ("2nd", "Singular"), "2nd pl": ("2nd", "Plural"),
        "3rd sg": ("3rd", "Singular"), "3rd pl": ("3rd", "Plural"),
        "first singular": ("1st", "Singular"), "first plural": ("1st", "Plural"),
        "second singular": ("2nd", "Singular"), "second plural": ("2nd", "Plural"),
        "third singular": ("3rd", "Singular"), "third plural": ("3rd", "Plural"),
    }
    # Output keys for the final dictionary
    person_output_keys = {
        ("1st", "Singular"): "1st Singular", ("1st", "Plural"): "1st Plural",
        ("2nd", "Singular"): "2nd Singular", ("2nd", "Plural"): "2nd Plural",
        ("3rd", "Singular"): "3rd Singular", ("3rd", "Plural"): "3rd Plural",
    }

    rows = conjugation_table.find_all("tr")

    # # Pass 1: Identify aspect column indices if this table structure is used
    # # Looks for a header row like: <th>...</th><th>imperfective aspect</th><th>perfective aspect</th>...
    # for row in rows:
    #     th_cells = row.find_all("td")
    #     if len(th_cells) >= 2: # Need at least two th cells for this pattern
    #         texts = [th.get_text(strip=True).lower() for th in th_cells]
    #         print(texts)
    #         try:
    #             # Find the column index for imperfective and perfective aspects
    #             # These indices are relative to the start of the row's cells (th_cells list)
    #             imp_idx_in_ths = texts.index("imperfective aspect")
    #             perf_idx_in_ths = texts.index("perfective aspect")
    #
    #             # The actual column index in the table is based on the position of these th cells
    #             active_imperfective_col_idx = imp_idx_in_ths
    #             active_perfective_col_idx = perf_idx_in_ths
    #
    #             # Correct indices to be relative to the start of the table, assuming these th define columns
    #             # This requires knowing how many th cells precede these aspect headers in *that specific row*.
    #             # For simplicity, if "imperfective aspect" is the text of th_cells[i], its column index is i.
    #             # This assumes the aspect headers are themselves columns.
    #             # Example: [th, th_imp_aspect, th_perf_aspect] -> imp_idx=1, perf_idx=2
    #
    #             # Let's refine: the index in `texts` (which is from `th_cells`) is the column index
    #             # *if* all cells in that row are `<th>`.
    #             # This is a common pattern for header rows defining aspect columns.
    #             break # Found aspect columns, assume this structure
    #         except ValueError:
    #             continue # Keywords not found in this row

    imp_idx_in_ths = 1
    perf_idx_in_ths = 2

    # Pass 2: Extract data
    for row in rows:
        # th_cells = row.find_all("th")
        td_cells = row.find_all("td")

        # if not th_cells: # Skip rows without any header cells
        #     continue

        # Get text from the first header cell in the row
        # first_th_text = th_cells[0].get_text(strip=True)
        # first_th_text_lower = first_th_text.lower()
        #
        # # A. Identify Tense Context Rows (e.g., "Present (ενεστώτας)", "Imperfect (παρατατικός)")
        # # These rows establish the current_tense_context for subsequent person rows.
        # is_tense_context_row = False
        # if "present" in first_th_text_lower or "ενεστώτας" in first_th_text_lower:
        #     current_tense_context = "Present"
        #     is_tense_context_row = True
        # elif "imperfect" in first_th_text_lower or "παρατατικός" in first_th_text_lower:
        #     current_tense_context = "Imperfect" # Maps to Past Imperfective
        #     is_tense_context_row = True
        # elif "aorist" in first_th_text_lower or "αόριστος" in first_th_text_lower:
        #     current_tense_context = "Aorist"    # Maps to Past Perfective
        #     is_tense_context_row = True
        # elif "future" in first_th_text_lower or "μέλλοντας" in first_th_text_lower:
        #     current_tense_context = "Future"
        #     is_tense_context_row = True
        #
        # if is_tense_context_row:
        #     # This row's purpose was to set the tense context.
        #     # If it also contains data cells, it might be a combined header/data row,
        #     # but typically these are separate. We'll rely on person rows below.
        #     continue # Move to the next row

        # B. Identify Person Rows (e.g., "1st sg", "2nd pl") using the established current_tense_context
        person_info = person_map_keys.get(first_th_text_lower)

        if current_tense_context and person_info:
            person_base, number_key = person_info
            output_person_key = person_output_keys[(person_base, number_key)]

            if not td_cells: continue # Person row must have data cells for forms

            # Determine target dictionary keys based on Wiktionary's tense naming
            target_tense_dict_key = None
            target_aspect_dict_key = None
            form_to_store_single = None # For Present, Imperfect, Aorist

            # Column index within td_cells for imperfective and perfective forms.
            # This assumes the person th (first_th_text) is the first column,
            # and subsequent td_cells align with aspect columns identified.
            # If active_..._col_idx are 0-indexed from table start, and th_cells[0] is person:
            # td_idx_imp = active_imperfective_col_idx - 1 (if person is col 0, imp is col 1)
            # td_idx_perf = active_perfective_col_idx - 1 (if person is col 0, perf is col 2)

            # Number of th cells in the current row before data cells start
            num_leading_th = len(th_cells)

            if current_tense_context == "Present":
                target_tense_dict_key = "Present"
                target_aspect_dict_key = "Imperfective"
                td_idx = active_imperfective_col_idx - num_leading_th
                if active_imperfective_col_idx != -1 and 0 <= td_idx < len(td_cells):
                    form_to_store_single = get_first_word(td_cells[td_idx].get_text(strip=True))
                elif len(td_cells) > 0: # Fallback: take first td cell
                    form_to_store_single = get_first_word(td_cells[0].get_text(strip=True))

            elif current_tense_context == "Imperfect": # Wiktionary's "Imperfect" is Past Imperfective
                target_tense_dict_key = "Past"
                target_aspect_dict_key = "Imperfective"
                td_idx = active_imperfective_col_idx - num_leading_th
                if active_imperfective_col_idx != -1 and 0 <= td_idx < len(td_cells):
                    form_to_store_single = get_first_word(td_cells[td_idx].get_text(strip=True))
                elif len(td_cells) > 0:
                    form_to_store_single = get_first_word(td_cells[0].get_text(strip=True))

            elif current_tense_context == "Aorist": # Wiktionary's "Aorist" is Past Perfective
                target_tense_dict_key = "Past"
                target_aspect_dict_key = "Perfective"
                td_idx = active_perfective_col_idx - num_leading_th
                if active_perfective_col_idx != -1 and 0 <= td_idx < len(td_cells):
                    form_to_store_single = get_first_word(td_cells[td_idx].get_text(strip=True))
                # Fallback for Aorist if aspect columns not clearly ID'd:
                # Aorist forms are often in the second data cell if the first is for imperfective (marked '—')
                elif len(td_cells) > 1 and get_first_word(td_cells[0].get_text(strip=True)) == "": # Check if first td is empty/dash
                    form_to_store_single = get_first_word(td_cells[1].get_text(strip=True))
                elif len(td_cells) > 0:
                    form_to_store_single = get_first_word(td_cells[0].get_text(strip=True))


            elif current_tense_context == "Future":
                form_future_imp = None
                form_future_perf = None

                td_idx_imp = active_imperfective_col_idx - num_leading_th
                td_idx_perf = active_perfective_col_idx - num_leading_th

                if active_imperfective_col_idx != -1 and 0 <= td_idx_imp < len(td_cells):
                    form_future_imp = get_first_word(td_cells[td_idx_imp].get_text(strip=True))
                elif len(td_cells) > 0 and active_imperfective_col_idx == -1 : # Fallback if no aspect col defined
                     form_future_imp = get_first_word(td_cells[0].get_text(strip=True))


                if active_perfective_col_idx != -1 and 0 <= td_idx_perf < len(td_cells):
                    form_future_perf = get_first_word(td_cells[td_idx_perf].get_text(strip=True))
                elif len(td_cells) > 1 and active_perfective_col_idx == -1: # Fallback if no aspect col defined
                     form_future_perf = get_first_word(td_cells[1].get_text(strip=True))

                if form_future_imp:
                    data["Future"]["Imperfective"][output_person_key] = form_future_imp
                if form_future_perf:
                    data["Future"]["Perfective"][output_person_key] = form_future_perf
                continue # Handled Future, move to next row

            # Store the single form if found (for Present, Past Imperfective, Past Perfective)
            if target_tense_dict_key and target_aspect_dict_key and form_to_store_single:
                data[target_tense_dict_key][target_aspect_dict_key][output_person_key] = form_to_store_single

    # Clean up any empty tense/aspect entries
    final_data = {}
    for tense, aspects_data in data.items():
        cleaned_aspects = {}
        for aspect, persons_data in aspects_data.items():
            if persons_data: # Only include if there are actual person entries
                cleaned_aspects[aspect] = persons_data
        if cleaned_aspects: # Only include if there are actual aspect entries
            final_data[tense] = cleaned_aspects

    return final_data

if __name__ == "__main__":
    # word_to_lookup = input("Enter a Greek verb to look up (e.g., γράφω, τρέχω, αγαπώ): ")
    # if word_to_lookup:
    #     conjugations = extract_verb_conjugations(word_to_lookup)
    #     if conjugations:
    #         print(f"\nConjugations for {word_to_lookup}:")
    #         # Pretty print the JSON output
    #         print(json.dumps(conjugations, indent=2, ensure_ascii=False))
    #     else:
    #         print(f"Could not extract conjugations for {word_to_lookup}.")
    # else:
    #     print("No word entered.")

    # Example test cases you can uncomment for quick testing:
    for test_word in ["γράφω"]: #, "τρέχω", "αγαπώ", "κάνω", "λέγω", "πλένω"]:
        print(f"\n--- Testing: {test_word} ---")
        conjugations = extract_verb_conjugations(test_word)
        if conjugations:
            print(json.dumps(conjugations, indent=2, ensure_ascii=False))
        else:
            print(f"No results for {test_word}")
        print("-------------------------\n")



rows = t.find_all("tr")
data = {}
i = 0
current_section = None
while i < len(rows):
    row = rows[i]
    print(row)
    if row.find("td").text.startswith("Non-past tenses"):
        current_section = "present"
    elif row.find("td").text.startswith("Past tenses"):
        current_section = "past"

    if current_section not in ["present", "past"]:
        i += 1
        continue

    for p in range(3):
        i += 1
        try:
            row = rows[i]
        except IndexError:
            break
        tds = row.find_all("td")
        if len(tds) < 2:
            continue
        td = tds[1]
        try:
            word = td.find("a").text
        except:
            word = td.text
        print(current_section, str(p+1), word)
    i += 1
