from app import app


db = SQLAlchemy(app)




class persona(db.Model):
	rut = db.Column(db.String(10), primary_key=True)

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

class formulario(db.Model):
	numero_atencion = db.Column(db.Integer, primary_key=True)
	cne = db.Column(db.Integer)
	rol = db.Column(db.String(20), primary_key=True)
	# adquirientes
	# enajenantees
	fojas = db.Column(db.Integer)
	fecha_inscripcion = db.Column(db.Date)
	numero_inscripcion = db.Column(db.Integer)


