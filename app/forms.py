from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateField
from wtforms.validators import DataRequired, EqualTo, Length

class MyForm(FlaskForm):
	numero_atencion = IntegerField('Número de Atención', validators=[DataRequired()])
	cne = IntegerField('CNE', validators=[DataRequired()])
	rol = StringField('ROL', validators=[DataRequired()])
	fojas = IntegerField('Fojas', validators=[DataRequired()])
	fecha_inscripcion = DateField('Fecha de Inscripción', format='%Y-%m-%d', validators=[DataRequired()])
	numero_inscripcion = IntegerField('Número de Inscripción', validators=[DataRequired()])
	submit = SubmitField('Enviar')
