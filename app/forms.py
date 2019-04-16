from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class ReccomendationForm(FlaskForm):
    show_title = StringField('Show Title', validators=[DataRequired()])
    submit = SubmitField('Estimate Audience Score')
