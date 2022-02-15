def get_article_row(article_id, csv_file):
    counter = 0
    for i in csv_file.Artikelnr:
        if i == article_id:
            return counter
            break
        counter += 1

m_j_dict = {
    "961": 1,
    "969": 1,
    "964": 1,
    "972": 1,
    "967": 1,
    "421": 1,
    "429": 1,
    "968": 1,
    "978": 1,
    "973": 1,
    "970": 1,
    "963": 1,
    "422": 1,
    "971": 1,
    "965": 1,
    "962": 1,
    "979": 1,
    "975": 1,
    "974": 0,
    "977": 0,
    "420": 0,
    "976": 0,
    "741": 0,
    "740": 0,
    "966": 0,
}

