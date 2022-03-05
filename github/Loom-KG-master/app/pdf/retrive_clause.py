import json
from difflib import SequenceMatcher


def similarity_score(a, b):
    return SequenceMatcher(None, a, b).ratio()


def extract_clause(match_string, filename):
    with open("./outputFormatted/" + filename, encoding="utf8") as f:
        extractedJSON = json.load(f)
        elements = extractedJSON["clauses"]
        elements = dict(elements)
        max_prob = 0
        str_val = ""
        for key in elements.keys():
            if len(elements[key]) == 1:
                score = similarity_score(elements[key]["info"], match_string)
                if score > max_prob:
                    str_val = elements[key]["info"]
                    max_prob = score
            else:
                temp = ""
                flag = 0
                for key2 in elements[key].keys():
                    score = similarity_score(elements[key][key2], match_string)
                    label = "" if key2 == "info" else key2 + ") "
                    temp = temp + label + elements[key][key2] + "\n"
                    if score > max_prob:
                        max_prob = score
                        flag = 1
                if flag == 1:
                    str_val = temp
        return str_val
