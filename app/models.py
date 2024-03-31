from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Persona(db.Model):
    rut = db.Column(db.String(10), primary_key=True)

    def __init__(self, rut):
        self.rut = rut

class BienRaiz(db.Model):
    comuna = db.Column(db.Integer, db.ForeignKey('comuna.codigo_comuna'))
    manzana = db.Column(db.Integer)
    predio = db.Column(db.Integer)
    rol = db.Column(db.String(20), primary_key=True)

    def __init__(self, comuna, manzana, predio):
        self.comuna = comuna
        self.manzana = manzana
        self.predio = predio
        self.rol = f'{comuna}-{manzana}-{predio}'

class Comuna(db.Model):
    codigo_comuna = db.Column(db.Integer, primary_key=True)
    nombre_comuna = db.Column(db.String(30))
    codigo_region = db.Column(db.Integer)
    nombre_region = db.Column(db.String(50))

    def __init__(self, codigo_comuna, nombre_comuna, codigo_region, nombre_region):
        self.codigo_comuna = codigo_comuna
        self.nombre_comuna = nombre_comuna
        self.codigo_region = codigo_region
        self.nombre_region = nombre_region

class CNE(db.Model):
    codigo_cne = db.Column(db.Integer, primary_key=True)
    nombre_cne = db.Column(db.String(30))

    def __init__(self, codigo_cne, nombre_cne):
        self.codigo_cne = codigo_cne
        self.nombre_cne = nombre_cne

class Implicados(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_atencion = db.Column(db.Integer, db.ForeignKey('formulario.numero_atencion'))
    rut = db.Column(db.String(10), db.ForeignKey('persona.rut'))
    adquiriente = db.Column(db.Boolean)
    porcentaje_derecho = db.Column(db.Float)

    def __init__(self, numero_atencion, rut, adquiriente, porcentaje_derecho):
        self.numero_atencion = numero_atencion
        self.rut = rut
        self.adquiriente = adquiriente
        self.porcentaje_derecho = porcentaje_derecho

class Propietario(db.Model):
    propietario_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    multipropietario_id = db.Column(db.Integer, db.ForeignKey('multipropietario.id'), nullable=False)
    rut = db.Column(db.String(10), db.ForeignKey('persona.rut'))
    porcentaje_derecho = db.Column(db.Float, nullable=True)

    def __init__(self, rut, multipropietario_id, porcentaje_derecho):
        self.rut = rut
        self.multipropietario_id = multipropietario_id
        self.porcentaje_derecho = porcentaje_derecho

class Multipropietario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rol = db.Column(db.String(20), db.ForeignKey('bien_raiz.rol'), primary_key=True)
    fojas = db.Column(db.Integer, nullable=True)
    fecha_inscripcion = db.Column(db.Date, nullable=True)
    numero_inscripcion = db.Column(db.Integer, nullable=True)
    ano_vigencia_inicial = db.Column(db.Integer, nullable=True)
    ano_vigencia_final = db.Column(db.Integer, nullable=True)

    def __init__(self, id, rol, fojas, fecha_inscripcion, numero_inscripcion, ano_vigencia_inicial, ano_vigencia_final):
        self.id = id
        self.rol = rol
        self.fojas = fojas
        self.fecha_inscripcion = fecha_inscripcion
        self.numero_inscripcion = numero_inscripcion
        self.ano_vigencia_inicial = ano_vigencia_inicial
        self.ano_vigencia_final = ano_vigencia_final

class Formulario(db.Model):
    numero_atencion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cne = db.Column(db.Integer, db.ForeignKey('cne.codigo_cne'))
    rol = db.Column(db.String(20), db.ForeignKey('bien_raiz.rol'))
    fojas = db.Column(db.Integer, nullable=True)
    fecha_inscripcion = db.Column(db.Date, nullable=True)
    numero_inscripcion = db.Column(db.Integer, nullable=True)

    def __init__(self, cne, rol, fojas, fecha_inscripcion, numero_inscripcion):
        self.cne = cne
        self.rol = rol
        self.fojas = fojas
        self.fecha_inscripcion = fecha_inscripcion
        self. numero_inscripcion = numero_inscripcion
