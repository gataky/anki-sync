import pandas as pd

def create_declension_table_for_adj(declensions):
    # 1. Define row index (as a list)
    index_labels = ["m", "f", "n"]

    # 2. Define column MultiIndex levels
    # First level: Column sections ("nom", "acc", "gen")
    col_sections = ["nom", "acc", "gen"]
    # Second level: Sub-columns ("sg", "pl")
    sub_cols = ["sg", "pl"]

    # Create a list of tuples for the MultiIndex
    # This effectively flattens the two levels into pairs
    multi_index_tuples = []
    for section in col_sections:
        for sub in sub_cols:
            multi_index_tuples.append((section, sub))

    # Create the Pandas MultiIndex object
    columns = pd.MultiIndex.from_tuples(multi_index_tuples, names=['case', 'number'])

    # 3. Populate data
    # The data should be a list of lists (or a NumPy array) where
    # each inner list corresponds to a row, and the elements
    # correspond to the flattened columns in the MultiIndex order.

    # Create the Pandas DataFrame
    df = pd.DataFrame(declensions, index=index_labels, columns=columns)

    # Generate the HTML table string
    # .to_html() method generates a complete HTML table
    # You can add styling classes using the 'classes' argument if needed
    html_table = df.to_html(classes=['table', 'table-striped', 'table-bordered'])
    return html_table


def create_declension_table_for_noun(declensions):
    # 1. Define row index (as a list)
    index_labels = [" "]

    # 2. Define column MultiIndex levels
    # First level: Column sections ("nom", "acc", "gen")
    col_sections = ["nom", "acc", "gen"]
    # Second level: Sub-columns ("sg", "pl")
    sub_cols = ["sg", "pl"]

    # Create a list of tuples for the MultiIndex
    # This effectively flattens the two levels into pairs
    multi_index_tuples = []
    for section in col_sections:
        for sub in sub_cols:
            multi_index_tuples.append((section, sub))

    # Create the Pandas MultiIndex object
    columns = pd.MultiIndex.from_tuples(multi_index_tuples, names=['case', 'number'])

    # Create the Pandas DataFrame
    df = pd.DataFrame(declensions, index=index_labels, columns=columns)

    # Generate the HTML table string
    # .to_html() method generates a complete HTML table
    # You can add styling classes using the 'classes' argument if needed
    html_table = df.to_html(classes=['table', 'table-striped', 'table-bordered', 'table-centered'])
    return html_table
