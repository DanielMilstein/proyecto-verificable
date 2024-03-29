from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateField, FloatField, FieldList, FormField, ValidationError, SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, EqualTo, Length
from app.models import CNE
import re


def rol_validator(form, field):
	triplet_regex = re.compile(r'^\d+-\d+-\d+$')
	if not triplet_regex.match(field.data):
		raise ValidationError('El ROL debe tener el formato XXX-XXX-XXX')

def rut_validator(form, field):
	rut_regex = re.compile(r'^\d{7,8}-\d$')
	if not rut_regex.match(field.data):
		raise ValidationError('El RUT debe tener el formato XXXXXXXX-X')

def porcentaje_validator(form, field):
	if field.data < 0 or field.data > 100:
		raise ValidationError('El porcentaje debe estar entre 0 y 100')



class MyForm(FlaskForm):
	cne = QuerySelectField(query_factory=lambda: CNE.query.all(), get_label='nombre_cne')
	rol = StringField('ROL', validators=[DataRequired(), rol_validator])
	fojas = IntegerField('Fojas', validators=[DataRequired()])
	fecha_inscripcion = DateField('Fecha de Inscripción', format='%Y-%m-%d', validators=[DataRequired()])
	numero_inscripcion = IntegerField('Número de Inscripción', validators=[DataRequired()])
	
	submit = SubmitField('Enviar')


