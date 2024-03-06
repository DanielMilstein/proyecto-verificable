from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class MyForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	last_name = StringField('Last Name', validators=[DataRequired()])
	submit = SubmitField('Submit')
