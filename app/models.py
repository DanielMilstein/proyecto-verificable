from app import app

from sqlalchemy import Column, Integer, String, Date, Float, Boolean
db = SQLAlchemy(app)




class persona(db.Model):
	rut = db.Column(db.String(10), primary_key=True)

	def __init__(self, rut):
		self.rut = rut

class bienRaiz(db.Model):
	comuna = db.Column(db.Integer)
	manzana = db.Column(db.Integer)
	predio = db.Column(db.Integer)
	rol = db.Column(db.String(20), primary_key=True)

	def __init__(self, comuna, manzana, predio):
		self.comuna = comuna
		self.manzana = mazana
		self.predio = predio
		self.rol = f'{comuna}-{mazana}-{predio}'


class CNE(db.Model):
	codigo_cne = db.Column(db.Integer)
	nombre_cne = db.Column(db.String(30))

	
	def __init__(self, codigo_cne, nombre_cne):
		self.codigo_cne = codigo_cne
		self.nombre_cne = nombre_cne


class comuna(db.Model):
	codigo_comuna = db.Column(db.Integer)
	nombre_comuna = db.Column(db.String(30))

	def __init__(self, codigo_comuna, nombre_comuna):
		self.codigo_comuna = codigo_comuna
		self.nombre_comuna = nombre_comuna


class implicados(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	numero_atencion = db.Column(db.Integer, primary_key=True)
	rut = db.Column(db.String(10), primary_key=True)
	adquirient = db.Column(db.Boolean)
	porcentaje_derecho = db.Column(db.Float)

	def __init__(self, id, numero_atencion, rut, adquirient, porcentaje_derecho):
		self.id = id
		self.numero_atencion = numero_atencion
		self.rut = rut
		self.adquirient = adquirient
		self.porcentaje_derecho = porcentaje_derecho


class propietario(db.Model):
	rut = db.Column(db.String(10), primary_key=True)
	multipropietario_id = db.Column(db.Integer, primary_key=True)

	def __init__(self, rut, multipropietario_id):
		self.rut = rut
		self.multipropietario_id = multipropietario_id

class multipropietario(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	rol = db.Column(db.String(20), primary_key=True)
	fojas = db.Column(db.Integer)
	fecha_inscripcion = db.Column(db.Date)
	numero_inscripcion = db.Column(db.Integer)
	ano_vigencia_inicial = db.Column(db.Integer)
	ano_vigencia_final = db.Column(db.Integer)

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
	rol = db.Column(db.String(20), primary_key=True)
	fojas = db.Column(db.Integer)
	fecha_inscripcion = db.Column(db.Date)
	numero_inscripcion = db.Column(db.Integer)

	def __init__(self, numero_atencion, cne, rol, fojas, fecha_inscripcion, numero_inscripcion):
		self.numero_atencion = numero_atencion
		self.cne = cne
		self.rol = rol
		self.fojas = fojas
		self.fecha_inscripcion = fecha_inscripcion
		self. numero_inscripcion = numero_inscripcion




db.create_all()