# app/mod_main/forms.py


from flask_wtf import FlaskForm
from wtforms import TextField
from wtforms.validators import DataRequired, Email, length


class SignUpForm(FlaskForm):
    email = TextField(
        '',
        validators=[DataRequired(), Email(), length(min=3)])
