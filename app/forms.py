from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateField, FloatField, FieldList, FormField, ValidationError, SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, EqualTo, Length
from app.models import CNE, Comuna
from datetime import date
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
	if not field.data:
		raise ValidationError('El porcentaje debe tomar una valor númerico.')
	if field.data < 0 or field.data > 100:
		raise ValidationError('El porcentaje debe estar entre 0 y 100')

def positive_integer_validator(form, field):
    if field.data <= 0:
        raise ValidationError('Este campo debe ser mayor que 0')
	
def validate_past_date(form, field):
    if field.data >= date.today():
        raise ValidationError('La fecha debe ser anterior a hoy.')


class MyForm(FlaskForm):
    cne = QuerySelectField(query_factory=lambda: CNE.query.all(), get_label='nombre_cne')
    comuna = QuerySelectField(query_factory=lambda: Comuna.query.all(), get_label='nombre_comuna')
    manzana = IntegerField('Manzana', validators=[DataRequired(), positive_integer_validator])
    predio = IntegerField('Predio', validators=[DataRequired(), positive_integer_validator])
    fojas = IntegerField('Fojas', validators=[DataRequired(), positive_integer_validator])
    fecha_inscripcion = DateField('Fecha de Inscripción', format='%Y-%m-%d', validators=[DataRequired(), validate_past_date])
    numero_inscripcion = IntegerField('Número de Inscripción', validators=[DataRequired(), positive_integer_validator])
    
    submit = SubmitField('Enviar')

