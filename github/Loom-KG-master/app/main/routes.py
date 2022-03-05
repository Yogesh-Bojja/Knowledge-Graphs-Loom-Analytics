from app.main import bp
from flask import render_template
from wtforms import SubmitField, MultipleFileField
from flask_wtf import FlaskForm


class UploadForm(FlaskForm):
    file = MultipleFileField()
    submit = SubmitField("submit")


@bp.route("/")
@bp.route("/index")
def index():
    form = UploadForm()
    return render_template("graph.html", form=form)
