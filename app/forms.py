from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateField, FloatField, FieldList, FormField, ValidationError, SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, EqualTo, Length
from app.models import CNE, Comuna
from datetime import date
import re

def validate_rut(rut):
    rut = rut.replace(".", "").replace("-", "")
    rut_body = rut[:-1]
    given_verifier = rut[-1].upper()

    reversed_rut_body = rut_body[::-1]

    series = [2, 3, 4, 5, 6, 7]

    total_sum = 0
    for i, digit in enumerate(reversed_rut_body):
        total_sum += int(digit) * series[i % len(series)]

    remainder = total_sum % 11

    verifier_digit = 11 - remainder
    if verifier_digit == 11:
        computed_verifier = '0'
    elif verifier_digit == 10:
        computed_verifier = 'K'
    else:
        computed_verifier = str(verifier_digit)

    return given_verifier == computed_verifier

def rol_validator(field):
	triplet_regex = re.compile(r'^\d+-\d+-\d+$')
	if not triplet_regex.match(field.data):
		raise ValidationError('El ROL debe tener el formato XXX-XXX-XXX')

def rut_validator(field):
	rut_regex = re.compile(r'^\d{7,8}-[\dkK]$')
	if not rut_regex.match(field.data):
		raise ValidationError('El RUT debe tener el formato XXXXXXXX-X')

def porcentaje_validator(field):
	if not field.data:
		raise ValidationError('El porcentaje debe tomar una valor numérico.')
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