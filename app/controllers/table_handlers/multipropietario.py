from app.models import Multipropietario, db
from .propietario import PropietarioTableHandler

class MultipropietarioTableHandler:
    def __init__(self) :
        self.propietario_handler = PropietarioTableHandler()

    def get_forms_by_rol(self, rol):
        return Multipropietario.query.filter_by(rol=rol).all()
    
    def upload_form(self, rol, fecha_inscripcion, fojas, nro_inscripcion, ano_inscripcion, ano_vigencia_inicial, ano_vigencia_final):
        new_form = Multipropietario(rol=rol, fecha_inscripcion=fecha_inscripcion, fojas=fojas, numero_inscripcion=nro_inscripcion, ano_inscripcion=ano_inscripcion, ano_vigencia_inicial=ano_vigencia_inicial, ano_vigencia_final=ano_vigencia_final)
        db.session.add(new_form)
        db.session.commit()
        return new_form.id
    
    def upload_propietario(self, propietario, multipropietario_id):
        self.propietario_handler.upload_propietario(propietario, multipropietario_id)

    def check_if_propietario_exists(self, rut, rol, ano_vigencia_inicial):
        propietarios = self.propietario_handler.check_if_propietario_exists(rut)
        for propietario in propietarios:
            multipropietario = Multipropietario.query.filter((Multipropietario.id == propietario.multipropietario_id),
            (Multipropietario.ano_vigencia_inicial == ano_vigencia_inicial),
            (Multipropietario.rol == rol)).all()
            if multipropietario:
                return multipropietario
        return False
        
    def upload_adquirientes(self, adquirientes, multipropietario_id):
        self.propietario_handler.upload_adquirientes(adquirientes, multipropietario_id)

    def update_form(self, form_id, ano_vigencia_final):
        form = Multipropietario.query.get(form_id)
        if not form:
            return        
        form.ano_vigencia_final = ano_vigencia_final
        db.session.commit()
    
    def delete(self, multipropietario_id):
        self.delete_linked_propietarios(multipropietario_id)
        self.delete_multipropietario(multipropietario_id)

    def delete_multipropietario(self, multipropietario_id):
        multipropietario = Multipropietario.query.get(multipropietario_id)
        db.session.delete(multipropietario)
        db.session.commit()

    def delete_linked_propietarios(self, multipropietario_id):
        propietarios = self.propietario_handler.get_by_multipropietario_id(multipropietario_id)
        for propietario in propietarios:
            self.propietario_handler.delete(propietario)
    
    def get_linked_propietarios(self, multipropietario_id):
        propietarios = self.propietario_handler.get_by_multipropietario_id(multipropietario_id)
        adquirientes = []
        for propietario in propietarios:
            adquiriente = {}
            adquiriente['rut'] = propietario.rut
            adquiriente['pctje_derecho'] = propietario.porcentaje_derecho
            adquirientes.append(adquiriente)
        return adquirientes

    def get_posterior_forms(self, new_form_data):
        return Multipropietario.query.filter(
            (Multipropietario.fecha_inscripcion > new_form_data['fecha_inscripcion']) &
            (Multipropietario.rol == new_form_data['rol'])
        ).all()

    def multipropietario_to_dict(self, multipropietario):
        return {
            'id': multipropietario.id,
            'rol': multipropietario.rol,
            'fecha_inscripcion': multipropietario.fecha_inscripcion,
            'ano_inscripcion': multipropietario.ano_inscripcion,
            'fojas': multipropietario.fojas,
            'nro_inscripcion': multipropietario.numero_inscripcion
        }

