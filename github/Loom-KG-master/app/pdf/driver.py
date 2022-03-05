import os
import shutil
from app.pdf.scraper import scrape_pdf
from app.pdf.formatter import format_json
from app.model.spacy import model_spacy
from app.model.bert import model_bert


# from app.model.bow import model_bow


def process_documents(files_list):
    try:
        print("Calling Scraper")
        if scrape_pdf(files_list):
            os.mkdir("./outputFormatted/")

            print("Calling formatter")
            format_json()

            print("Calling Spacy model for creating static nodes")
            citation_list = model_spacy()

            print("Calling bert model for dynamic node creation")
            model_bert(0.5, citation_list)

    finally:
        # cleanup
        if os.path.exists("./outputZip/"):
            shutil.rmtree("./outputZip/")

        if os.path.exists("./outputFormatted/"):
            shutil.rmtree("./outputFormatted/")
