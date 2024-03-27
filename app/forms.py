from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateField, FloatField, FieldList, FormField
from wtforms.validators import DataRequired, EqualTo, Length




class ImplicadosForm(FlaskForm):
	rut = StringField('Rut', validators=[DataRequired(), Length(min=9, max=12)])
	porcentaje_derecho = FloatField('Porcentaje de Derecho', validators=[DataRequired()])





class MyForm(FlaskForm):
	numero_atencion = IntegerField('Número de Atención', validators=[DataRequired()])
	cne = IntegerField('CNE', validators=[DataRequired()])
	rol = StringField('ROL', validators=[DataRequired()])
	fojas = IntegerField('Fojas', validators=[DataRequired()])
	fecha_inscripcion = DateField('Fecha de Inscripción', format='%Y-%m-%d', validators=[DataRequired()])
	numero_inscripcion = IntegerField('Número de Inscripción', validators=[DataRequired()])
	
	adquirientes = FieldList(FormField(ImplicadosForm), min_entries=1)
	enajenantes = FieldList(FormField(ImplicadosForm))

	submit = SubmitField('Enviar')


