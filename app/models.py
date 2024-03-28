from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date, Float, Boolean

db = SQLAlchemy()




class persona(db.Model):
	rut = db.Column(db.String(10), primary_key=True)


	def __init__(self, rut):
		self.rut = rut

	def __repr__(self):
		return f'{self.rut}'

class bienRaiz(db.Model):
	comuna = db.Column(db.Integer)
	manzana = db.Column(db.Integer)
	predio = db.Column(db.Integer)
	rol = db.Column(db.String(20), primary_key=True)

	# propietarios = db.relationship('propietario', back_populates='bienRaiz')

	def __init__(self, rol):
		rolList = rol.split('-')
		self.comuna = rolList[0]
		self.manzana = rolList[1]
		self.predio = rolList[2]
		self.rol = rol
		


class CNE(db.Model):
	codigo_cne = db.Column(db.Integer, primary_key=True)
	nombre_cne = db.Column(db.String(30))

	
	def __init__(self, codigo_cne, nombre_cne):
		self.codigo_cne = codigo_cne
		self.nombre_cne = nombre_cne


class comuna(db.Model):
	codigo_comuna = db.Column(db.Integer, primary_key=True)
	nombre_comuna = db.Column(db.String(30))

	def __init__(self, codigo_comuna, nombre_comuna):
		self.codigo_comuna = codigo_comuna
		self.nombre_comuna = nombre_comuna


class implicados(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	numero_atencion = db.Column(db.Integer, db.ForeignKey('formulario.numero_atencion'))
	rut = db.Column(db.String(10), db.ForeignKey('persona.rut'))
	adquiriente = db.Column(db.Boolean)
	porcentaje_derecho = db.Column(db.Float)
	# persona = db.relationship('persona', back_populates='implicados')


	def __init__(self, id, numero_atencion, rut, adquiriente, porcentaje_derecho):
		self.id = id
		self.numero_atencion = numero_atencion
		self.rut = rut
		self.adquiriente = adquiriente
		self.porcentaje_derecho = porcentaje_derecho


class propietario(db.Model):
	multipropietario_id = db.Column(db.Integer, primary_key=True)
	rut = db.Column(db.String(10), db.ForeignKey('persona.rut'))
	rol = db.Column(db.String(20), db.ForeignKey('bien_raiz.rol'))
	porcentaje_derecho = db.Column(db.Float)

	# bienes_raices = db.relationship('bienRaiz', back_populates='propietarios')


	def __init__(self, rut, multipropietario_id, porcentaje_derecho):
		self.rut = rut
		self.multipropietario_id = multipropietario_id
		self.porcentaje_derecho = porcentaje_derecho

class multipropietario(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	rol = db.Column(db.String(20), db.ForeignKey('bien_raiz.rol') , primary_key=True)
	fojas = db.Column(db.Integer)
	fecha_inscripcion = db.Column(db.Date)
	numero_inscripcion = db.Column(db.Integer)
	ano_vigencia_inicial = db.Column(db.Integer)
	ano_vigencia_final = db.Column(db.Integer)

	# propietarios = db.relationship('propietario', back_populates='multipropietario')

	def __init__(self, id, rol, fojas, fecha_inscripcion, numero_inscripcion, ano_vigencia_inicial, ano_vigencia_final):
		self.id = id
		self.rol = rol
		self.fojas = fojas
		self.fecha_inscripcion = fecha_inscripcion
		self.numero_inscripcion = numero_inscripcion
		self.ano_vigencia_inicial = ano_vigencia_inicial
		self.ano_vigencia_final = ano_vigencia_final





class formulario(db.Model):
	numero_atencion = db.Column(db.Integer, primary_key=True)
	cne = db.Column(db.Integer)
	rol = db.Column(db.String(20))
	fojas = db.Column(db.Integer)
	fecha_inscripcion = db.Column(db.Date)
	numero_inscripcion = db.Column(db.Integer)

	# implicados = db.relationship('implicados', back_populates='formulario')
	# multipropietario = db.relationship('multipropietario', back_populates='formulario')

	def __init__(self, numero_atencion, cne, rol, fojas, fecha_inscripcion, numero_inscripcion):
		self.numero_atencion = numero_atencion
		self.cne = cne
		self.rol = rol
		self.fojas = fojas
		self.fecha_inscripcion = fecha_inscripcion
		self. numero_inscripcion = numero_inscripcion

	def __repr__(self):
		return f'{self.numero_atencion}\n{self.cne}\n {self.rol}\n {self.fojas}\n {self.fecha_inscripcion}\n {self.numero_inscripcion}'

