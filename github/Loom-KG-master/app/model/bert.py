import os
import json
import numpy as np
import torch

from json.encoder import JSONEncoder
from transformers import AutoTokenizer, AutoModelForSequenceClassification, logging
from app.database.create import *
from app.pdf.formatter import extract_citation_number
from app.pdf.formatter import preprocess
from app.pdf.retrive_clause import extract_clause

# not sure about it's purpose. Can be removed
logging.set_verbosity_error()


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def model_bert(threshold, citation_list):
    filenames = os.listdir("./outputZip/")
    new_data = []
    extracted_citation = []
    for filename in filenames:
        with open("./outputZip/" + filename, encoding="utf8") as f:
            extracted_data = json.load(f)

        elements = extracted_data["elements"]

        for element in elements:
            try:
                if "Text" in element:
                    temp = extract_citation_number(element["Text"])
                    if temp:
                        extracted_citation.append(temp)
                    new_data.append(preprocess(element["Text"]))
            except:
                print(" Error while reading file : {} !!!", filename)

        citation = list(filter(lambda d: d["filename"] in filename, citation_list))
        result = classify_dynamic_entities(
            new_data, threshold, citation[0]["citation"], filename
        )

        if result:
            print("BERT output successful!!")
        else:
            print("Classification model failed!!")

        print(extracted_citation)
        for citation_no in extracted_citation[1:]:
            # Serach if node already exists
            # if yes then create relation of is_mentioned
            # if no then create a node with the citation number
            db_return = db_create_relations(
                citation[0]["citation"],
                "File",
                {"name": citation_no[0]},
                {},
                "is_mentioned",
            )
            print(citation_no[0])
            print(db_return)
        new_data.clear()
        extracted_citation.clear()


def classify_dynamic_entities(data, threshold, citation, filename):
    # Bert Json file
    predictions = open("bert_output.json", "w", encoding="utf-8")

    # Call the model and tokenizer
    model_name = "nlpaueb/legal-bert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    label_names = ["dec_name", "counsel", "court", "facts", "judge", "outcome"]
    loaded_model = AutoModelForSequenceClassification.from_pretrained(
        "models/model-bert"
    )

    facts = []
    outcome = []

    fact_prop = {"name": "fact"}
    outcome_prop = {"name": "outcome"}

    # Predict for each sentence in the data
    for d in data:
        word_list = d.split()

        # Clean string and keep only sentences with words greater than 1
        if len(word_list) > 1:

            inputs = tokenizer(
                d, padding="max_length", truncation=True, return_tensors="pt"
            )

            outputs = loaded_model(**inputs)
            probs = torch.nn.functional.softmax(outputs["logits"], dim=1)
            probs = probs.detach().numpy().flatten()
            sort_probs = np.sort(probs)[::-1]
            ordered_labels = []
            for prob in sort_probs:
                x = np.array(np.where(probs == prob)).flatten()
                ordered_labels.append(label_names[x[0]])

            if sort_probs[0] >= threshold:
                x = {
                    "text": d,
                    "label": ordered_labels[0],
                    "probability": str(sort_probs[0]),
                }
                json.dump(x, predictions, cls=NumpyArrayEncoder)
                predictions.write("\n")

                if ordered_labels[0] == "facts":
                    facts.append(x)

                if ordered_labels[0] == "outcome":
                    outcome.append(x)

    facts.sort(key=lambda element: element.get("probability"))
    outcome.sort(key=lambda element: element.get("probability"))

    for i, data in enumerate(facts[:5]):
        prop_id = "relation" + str(i)
        fact_prop[prop_id] = extract_clause(data["text"], filename)

    for i, data in enumerate(outcome[:2]):
        prop_id = "relation" + str(i)
        outcome_prop[prop_id] = extract_clause(data["text"], filename)

    # Clearing duplicate value from the fact and outcome dictionary
    temp_dict = {val: key for key, val in fact_prop.items()}
    fact_prop_clean = {val: key for key, val in temp_dict.items()}

    temp_dict = {val: key for key, val in outcome_prop.items()}
    outcome_prop_clean = {val: key for key, val in temp_dict.items()}

    # writing to the database
    create_fact_node(fact_prop_clean, citation)
    create_outcome_node(outcome_prop_clean, citation)

    return True
