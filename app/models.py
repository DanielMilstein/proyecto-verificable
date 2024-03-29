from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date, Float, Boolean

db = SQLAlchemy()




class persona(db.Model):
	rut = db.Column(db.String(10), primary_key=True)

	# implicados = db.relationship('implicados', back_populates='persona')
	# propietarios = db.relationship('propietario', back_populates='persona')


	def __init__(self, rut):
		self.rut = rut

	def __repr__(self):
		return f'{self.rut}'

class bienRaiz(db.Model):
	comune = db.Column(db.Integer, db.ForeignKey('comuna.codigo_comuna'))
	manzana = db.Column(db.Integer)
	predio = db.Column(db.Integer)
	rol = db.Column(db.String(20), primary_key=True)

	# comuna = db.relationship('comuna', back_populates='bienes_raices')
	# multipropietario = db.relationship('multipropietario', back_populates='bienRaiz')

	def __init__(self, rol):
		rolList = rol.split('-')
		self.comune = rolList[0]
		self.manzana = rolList[1]
		self.predio = rolList[2]
		self.rol = rol
		


class CNE(db.Model):
	codigo_cne = db.Column(db.Integer, primary_key=True)
	nombre_cne = db.Column(db.String(30))

	# formulario = db.relationship('formulario', back_populates='cene')

	def __init__(self, codigo_cne, nombre_cne):
		self.codigo_cne = codigo_cne
		self.nombre_cne = nombre_cne


class comuna(db.Model):
	codigo_comuna = db.Column(db.Integer, primary_key=True)
	nombre_comuna = db.Column(db.String(30))

	# bienes_raices = db.relationship('bienRaiz', back_populates='comuna')

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
	# formulario = db.relationship('formulario', back_populates='implicados')


	def __init__(self, numero_atencion, rut, adquiriente, porcentaje_derecho):
		self.numero_atencion = numero_atencion
		self.rut = rut
		self.adquiriente = adquiriente
		self.porcentaje_derecho = porcentaje_derecho


class propietario(db.Model):
	propietario_id = db.Column(db.Integer, primary_key=True)
	multipropietario_id = db.Column(db.Integer, db.ForeignKey('multipropietario.id'))
	rut = db.Column(db.String(10), db.ForeignKey('persona.rut'))
	porcentaje_derecho = db.Column(db.Float)

	
	# persona = db.relationship('persona', back_populates='propietarios')
	# multipropietario = db.relationship('multipropietario', back_populates='propietarios')


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


	# bienRaiz = db.relationship('bienRaiz', back_populates='multipropietario')
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
	cne = db.Column(db.Integer, db.ForeignKey('cne.codigo_cne'))
	rol = db.Column(db.String(20), db.ForeignKey('bien_raiz.rol'))
	fojas = db.Column(db.Integer)
	fecha_inscripcion = db.Column(db.Date)
	numero_inscripcion = db.Column(db.Integer)


	# bienRaiz = db.relationship('bienRaiz', back_populates='formulario')
	# implicados = db.relationship('implicados', back_populates='formulario')
	# cene = db.relationship('CNE', back_populates='formulario')

	def __init__(self, cne, rol, fojas, fecha_inscripcion, numero_inscripcion):
		self.cne = cne
		self.rol = rol
		self.fojas = fojas
		self.fecha_inscripcion = fecha_inscripcion
		self. numero_inscripcion = numero_inscripcion

	def __repr__(self):
		return f'{self.numero_atencion}\n{self.cne}\n {self.rol}\n {self.fojas}\n {self.fecha_inscripcion}\n {self.numero_inscripcion}'

