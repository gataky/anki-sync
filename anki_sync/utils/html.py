def get_article_for_case(case, number, base_article):
    """
    Determine the appropriate article for a given case and number.

    Args:
        case: The grammatical case ("nominative", "accusative", "genitive")
        number: The grammatical number ("singular", "plural")
        base_article: The base article ("ο", "η", "το")

    Returns:
        The appropriate article for the given case and number
    """
    if not base_article:
        return ""

    # Masculine articles (ο)
    if base_article == "ο":
        if case == "nominative":
            return "ο" if number == "singular" else "οι"
        elif case == "accusative":
            return "τον" if number == "singular" else "τους"
        elif case == "genitive":
            return "του" if number == "singular" else "των"

    # Feminine articles (η)
    elif base_article == "η":
        if case == "nominative":
            return "η" if number == "singular" else "οι"
        elif case == "accusative":
            return "την" if number == "singular" else "τις"
        elif case == "genitive":
            return "της" if number == "singular" else "των"

    # Neuter articles (το)
    elif base_article == "το":
        if case == "nominative":
            return "το" if number == "singular" else "τα"
        elif case == "accusative":
            return "το" if number == "singular" else "τα"
        elif case == "genitive":
            return "του" if number == "singular" else "των"

    return ""


def create_declension_table_for_adj(declensions):
    """
    Creates an HTML declension table for adjectives with the new structure.

    Args:
        declensions: List of lists where each inner list contains [n_s, n_p, a_s, a_p, g_s, g_p]
                    representing nominative singular, nominative plural, accusative singular,
                    accusative plural, genitive singular, genitive plural for each gender
                    The order is: masculine, feminine, neuter

    Returns:
        HTML table string with the new structure
    """
    if not declensions or len(declensions) < 3:
        return ""

    # Extract the declension data for each gender
    masc_data = declensions[0] if len(declensions) > 0 else ["-"] * 6
    fem_data = declensions[1] if len(declensions) > 1 else ["-"] * 6
    neut_data = declensions[2] if len(declensions) > 2 else ["-"] * 6

    # Map the data to the correct positions for each gender
    # Each data array = [n_s, n_p, a_s, a_p, g_s, g_p]

    # Masculine
    m_n_s = masc_data[0] if len(masc_data) > 0 else "-"
    m_n_p = masc_data[1] if len(masc_data) > 1 else "-"
    m_a_s = masc_data[2] if len(masc_data) > 2 else "-"
    m_a_p = masc_data[3] if len(masc_data) > 3 else "-"
    m_g_s = masc_data[4] if len(masc_data) > 4 else "-"
    m_g_p = masc_data[5] if len(masc_data) > 5 else "-"

    # Feminine
    f_n_s = fem_data[0] if len(fem_data) > 0 else "-"
    f_n_p = fem_data[1] if len(fem_data) > 1 else "-"
    f_a_s = fem_data[2] if len(fem_data) > 2 else "-"
    f_a_p = fem_data[3] if len(fem_data) > 3 else "-"
    f_g_s = fem_data[4] if len(fem_data) > 4 else "-"
    f_g_p = fem_data[5] if len(fem_data) > 5 else "-"

    # Neuter
    n_n_s = neut_data[0] if len(neut_data) > 0 else "-"
    n_n_p = neut_data[1] if len(neut_data) > 1 else "-"
    n_a_s = neut_data[2] if len(neut_data) > 2 else "-"
    n_a_p = neut_data[3] if len(neut_data) > 3 else "-"
    n_g_s = neut_data[4] if len(neut_data) > 4 else "-"
    n_g_p = neut_data[5] if len(neut_data) > 5 else "-"

    # Create the HTML table with the new structure grouped by gender
    html_table = f"""
    <table border="1" class="table table-striped table-bordered table-centered">
        <thead>
            <tr>
                <th rowspan="1">Γένος</th>
                <th class="case-header">Ονομαστική</th>
                <th class="case-header">Αιτιατική</th>
                <th class="case-header">Γενική</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>masculine</td>
                <td>
                    <span class="greek-text">-{m_n_s}</span><br>
                    <span class="greek-text">-{m_n_p}</span>
                </td>
                <td>
                    <span class="greek-text">-{m_a_s}</span><br>
                    <span class="greek-text">-{m_a_p}</span>
                </td>
                <td>
                    <span class="greek-text">-{m_g_s}</span><br>
                    <span class="greek-text">-{m_g_p}</span>
                </td>
            </tr>
            <tr>
                <td>feminine</td>
                <td>
                    <span class="greek-text">-{f_n_s}</span><br>
                    <span class="greek-text">-{f_n_p}</span>
                </td>
                <td>
                    <span class="greek-text">-{f_a_s}</span><br>
                    <span class="greek-text">-{f_a_p}</span>
                </td>
                <td>
                    <span class="greek-text">-{f_g_s}</span><br>
                    <span class="greek-text">-{f_g_p}</span>
                </td>
            </tr>
            <tr>
                <td>neuter</td>
                <td>
                    <span class="greek-text">-{n_n_s}</span><br>
                    <span class="greek-text">-{n_n_p}</span>
                </td>
                <td>
                    <span class="greek-text">-{n_a_s}</span><br>
                    <span class="greek-text">-{n_a_p}</span>
                </td>
                <td>
                    <span class="greek-text">-{n_g_s}</span><br>
                    <span class="greek-text">-{n_g_p}</span>
                </td>
            </tr>
        </tbody>
    </table>
    """

    return html_table


def create_declension_table_for_noun(declensions, article=""):
    """
    Creates an HTML declension table for nouns with the new structure.

    Args:
        declensions: List of lists where each inner list contains [n_s, n_p, a_s, a_p, g_s, g_p]
                    representing nominative singular, nominative plural, accusative singular,
                    accusative plural, genitive singular, genitive plural
        article: The nominative singular article (e.g., "ο", "η", "το")

    Returns:
        HTML table string with the new structure
    """
    if not declensions or not declensions[0]:
        return ""

    # Extract the declension data (first row)
    declension_data = declensions[0]

    # Map the data to the correct positions
    # declension_data = [n_s, n_p, a_s, a_p, g_s, g_p]
    n_s = declension_data[0] if len(declension_data) > 0 else "-"
    n_p = declension_data[1] if len(declension_data) > 1 else "-"
    a_s = declension_data[2] if len(declension_data) > 2 else "-"
    a_p = declension_data[3] if len(declension_data) > 3 else "-"
    g_s = declension_data[4] if len(declension_data) > 4 else "-"
    g_p = declension_data[5] if len(declension_data) > 5 else "-"

    # Get articles for each case and number
    n_s_article = get_article_for_case("nominative", "singular", article)
    n_p_article = get_article_for_case("nominative", "plural", article)
    a_s_article = get_article_for_case("accusative", "singular", article)
    a_p_article = get_article_for_case("accusative", "plural", article)
    g_s_article = get_article_for_case("genitive", "singular", article)
    g_p_article = get_article_for_case("genitive", "plural", article)

    # Create the HTML table with the new structure
    html_table = f"""
    <table border="1" class="table table-striped table-bordered table-centered">
        <thead>
            <tr>
                <th rowspan="1"></th>
                <th class="case-header">Ενικός</th>
                <th class="case-header">Πληθυντικός</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Ονομαστική</td>
                <td><span class="greek-text">{n_s_article}  -{n_s}</span></td>
                <td><span class="greek-text">{n_p_article}  -{n_p}</span></td>
            </tr>
            <tr>
                <td>Αιτιατική</td>
                <td><span class="greek-text">{a_s_article}  -{a_s}</span></td>
                <td><span class="greek-text">{a_p_article}  -{a_p}</span></td>
            </tr>
            <tr>
                <td>Γενική</td>
                <td><span class="greek-text">{g_s_article}  -{g_s}</span></td>
                <td><span class="greek-text">{g_p_article}  -{g_p}</span></td>
            </tr>
        </tbody>
    </table>
    """

    return html_table
