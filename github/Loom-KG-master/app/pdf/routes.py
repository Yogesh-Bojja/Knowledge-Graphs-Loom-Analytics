import os

from app.pdf import bp
from app.pdf.driver import process_documents
from app.model.bert import model_bert

from flask import redirect, render_template, abort, current_app
from wtforms import SubmitField, MultipleFileField
from flask_wtf import FlaskForm


class UploadForm(FlaskForm):
    file = MultipleFileField()
    submit = SubmitField("submit")


@bp.route("/upload", methods=["POST"])
def handle_upload():
    form = UploadForm()

    if form.validate_on_submit():
        files = form.file.data
        for file in files:
            file_ext = os.path.splitext(file.filename)[1]
            if file_ext not in current_app.config["UPLOAD_EXTENSIONS"]:
                abort(400)
        process_documents(files)
        return redirect("/graph/view")

    return render_template("index.html", form=form)
