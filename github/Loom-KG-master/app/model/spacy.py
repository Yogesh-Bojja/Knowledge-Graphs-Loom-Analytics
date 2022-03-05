import os
import json
import spacy

from app.database.create import *
from app.pdf.formatter import extract_citation_number


def model_spacy():
    filenames = os.listdir("./outputFormatted/")
    nlp_static = spacy.load("./models/model-spacy")
    citation_list = []

    for filename in filenames:
        with open("./outputFormatted/" + filename, encoding="utf8") as f:
            extracted_JSON = json.load(f)

        citation = extract_static_entities(filename, extracted_JSON, nlp_static)
        citation_list.append({"filename": filename, "citation": citation})

    return citation_list


def extract_static_entities(filename, extracted_JSON, nlp):
    print("Extracting Static Entities ")
    print("=============static entites==========")
    metadata = extracted_JSON["metadata"]
    print(metadata)

    citation_complete = metadata["CITATION"] if "CITATION" in metadata else None
    court_file_no = metadata["COURT_FILE_NO"] if "COURT_FILE_NO" in metadata else None
    date = metadata["DATE"] if "DATE" in metadata else None
    province = metadata["PROVINCE"] if "PROVINCE" in metadata else None
    case_info = metadata["CASE_INFO"] if "CASE_INFO" in metadata else None
    doc = nlp(case_info)

    info = extract_court_participants(doc)
    appli_plain = info["Applicant/Plaintiff"] if "Applicant/Plaintiff" in info else None
    appli_plain = ", ".join([a for a in appli_plain]) if appli_plain != None else "None"
    respo_defen = (
        info["Respondent/Defendant"] if "Respondent/Defendant" in info else None
    )
    respo_defen = ", ".join([a for a in respo_defen]) if respo_defen != None else "None"
    judge = info["Judge"] if "Judge" in info else None
    judge = ", ".join([a for a in judge]) if judge != None else "None"
    counsel_ap = info["Counsel(A/P)"] if "Counsel(A/P)" in info else None
    counsel_ap = ", ".join([a for a in counsel_ap]) if counsel_ap != None else "None"
    counsel_rd = info["Counsel(R/D)"] if "Counsel(R/D)" in info else None
    counsel_rd = ", ".join([a for a in counsel_rd]) if counsel_rd != None else "None"
    heard_date = info["Heard_date"] if "Heard_date" in info else None
    heard_date = ", ".join([a for a in heard_date]) if heard_date != None else "None"
    print("citation - ", citation_complete)
    print("court file num - ", court_file_no)
    print("date - ", date)
    print("province - ", province)
    print("applicant/plaintiff - ", appli_plain)
    print("respondent/defendant - ", respo_defen)
    print("judge - ", judge)
    print("counsel(Appli/plaint) - ", counsel_ap)
    print("counsel(resp/defen) - ", counsel_rd)
    print("heard date - ", heard_date)

    # Code to make new dictionary
    # Appending the filename at end of citation number in case the pdf doc doesn't have complete citation number
    # Example doc : OSC2020_04_00001, this code is just a workaround. A better
    # solution is required
    citation_no = extract_citation_number(
        citation_complete.rstrip() + " " + filename.split("_", 2)[0]
    )[0]
    print(citation_no)
    court_doc = {
        "filename": filename,
        "court_file_no": court_file_no,
        "citation_full": citation_complete,
        "court_date": date,
        "court_location": province,
        "count_medium": heard_date,
    }

    # Chnage
    person_relation = [
        {"name": appli_plain, "relation": "applicant"},
        {"name": respo_defen, "relation": "respondent"},
        {"name": counsel_ap, "relation": "counsel_applicant"},
        {"name": counsel_rd, "relation": "counsel_respondent"},
        {"name": judge, "relation": "judge"},
    ]

    # write code to push fixed entities in neo4j
    db_create_node("File", {"name": citation_no}, court_doc)

    for prop in person_relation:
        db_create_relations(
            citation_no, "Person", {"name": prop["name"]}, {}, prop["relation"]
        )

    return citation_no


def extract_court_participants(doc):
    ent_list = dict()
    for i in doc.ents:
        if i.label_ in ent_list:
            temp = ent_list[i.label_]
            entity = ""
            for d in i:
                if str(d) != ",":
                    entity = entity + " " + str(d)
            temp.append(entity.strip())
            ent_list[i.label_] = temp
        else:
            entity = ""
            temp = list()
            for d in i:
                if str(d) != ",":
                    entity = entity + " " + str(d)
            temp.append(entity.strip())
            ent_list[i.label_] = temp
    return ent_list
