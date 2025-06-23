import os
import itertools
import modern_greek_inflexion as mgi

from anki_sync.core.gsheets import GoogleSheetsManager

gsheets = GoogleSheetsManager(os.environ.get("GOOGLE_SHEET_ID"))

def download_sheets():
    sheets = [
        "Nouns", "Adjectives", "Verbs", "Verbs Conjugated",
    ]
    for sheet in sheets:
        data = gsheets.get_rows(sheet)
        data.to_csv(f"{sheet}.csv")

def extract_declensions(data):
    l = []
    for k, v in data.items():
        if isinstance(v, dict):
            l.extend(extract_declensions(v))
        else:
            l.extend(list(v))
    return l

def get_stem(forms):
    iter = itertools.zip_longest(*forms, fillvalue="")
    common = list(map(lambda x: all(x), iter))
    try:
        end = common.index(False)-1
    except ValueError:
        end = len(common)
    return forms[0][:end]

def process_nouns():
    pass



def process_adjectives():
    data = gsheets.get_rows("Adjectives")

    lines = []
    for idx, row in data.iterrows():
        word = row["Greek"]
        adjectives = mgi.Adjective(word).all().get("adj", {})
        declensions = extract_declensions(adjectives)
        stem = get_stem(declensions)

        order = [
            "sg.masc.nom",
            "sg.fem.nom",
            "sg.neut.nom",
            "pl.masc.nom",
            "pl.fem.nom",
            "pl.neut.nom",

            "sg.masc.acc",
            "sg.fem.acc",
            "sg.neut.acc",
            "pl.masc.acc",
            "pl.fem.acc",
            "pl.neut.acc",

            "sg.masc.gen",
            "sg.fem.gen",
            "sg.neut.gen",
            "pl.masc.gen",
            "pl.fem.gen",
            "pl.neut.gen",
        ]

        endings = [word]
        for o in order:
            n, g, c = o.split(".")
            declension = adjectives[n][g][c]
            w: str = list(declension)[0]
            ending = w.replace(stem, "")
            endings.append(ending)

        lines.append( ",".join(endings))

    return lines


def process_nouns():

    data = gsheets.get_rows("Nouns")

    gen_map = {
        "neuter": "neut",
        "neuter pl.": "neut",
        "masculine": "masc",
        "masculine pl.": "masc",
        "feminine": "fem",
        "feminine pl.": "fem",
    }

    lines = []
    for idx, row in data.iterrows():
        word = row["Greek"]
        gend = gen_map[row["Gender"]]

        if word == 'χείλια':
            gend = "fem"
        if word == "δόντια":
            gend = "fem"
        if word == "πουλόβερ":
            gend = "masc"
        if word == "κρέας":
            gend = "neut"

        try:
            nouns = mgi.Noun(word).all()[gend]
        except KeyError:
            lines.append(word)
            continue

        declensions = extract_declensions(nouns)
        stem = get_stem(declensions)

        order = [
            "sg.nom",
            "pl.nom",

            "sg.acc",
            "pl.acc",

            "sg.gen",
            "pl.gen",
        ]

        endings = [word]
        print(idx, row)
        for o in order:
            n, c = o.split(".")
            declension = nouns[n].get(c, "")
            try:
                w: str = list(declension)[0]
            except IndexError:
                w = ""
            ending = w[len(stem):]
            endings.append(ending)

        lines.append(",".join(endings))

    return lines
