from app.models import *
from datetime import datetime

REGULARIZACION_DE_PATRIMONIO = 99
COMPRAVENTA = 8

from app.models import Multipropietario, Propietario

class AlgoritmoMultipropietario:
    def insert_into_multipropietario(self, form_data):
        self.execute_algorithm_on(form_data)

    def execute_algorithm_on(self, form_data):
        cne_code = form_data.get('cne', None)
        if cne_code == REGULARIZACION_DE_PATRIMONIO:  # REGULARIZACION_DE_PATRIMONIO
            regularization_algorithm = AlgoritmoRegularizacionPatrimonio()
            regularization_algorithm.execute(form_data)
        elif cne_code == COMPRAVENTA:  # COMPRAVENTA
            # Logic for other CNE codes
            pass
        return True

class AlgoritmoRegularizacionPatrimonio:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def execute(self, form_data):
        rol = form_data.get('rol', None)
        fecha_inscripcion = form_data.get('fecha_inscripcion', None)
        nro_inscripcion = form_data.get('nro_inscripcion', None)
        fojas = form_data.get('fojas', None)
        adquirientes = form_data.get('adquirientes', [])

        existing_forms = self.get_existing_forms(rol)
        if not existing_forms:
            self.upload_new_form(rol, fecha_inscripcion, fojas, nro_inscripcion, adquirientes)
        else:
            prev_form = self.get_latest_form(existing_forms)
            if fecha_inscripcion > prev_form.fecha_inscripcion:
                """if fecha_inscripcion.year == prev_form.ano_inscripcion:
                    self.delete_previous_form(prev_form)
                else:"""
                self.update_previous_form(prev_form, fecha_inscripcion)
                self.upload_new_form(rol, fecha_inscripcion, fojas, nro_inscripcion, adquirientes)
            else:   
                self.reupload_forms(form_data)

    def get_existing_forms(self, rol):
        return self.multipropietario_handler.get_forms_by_rol(rol)

    def get_latest_form(self, forms):
        return max(forms, key=lambda x: x.fecha_inscripcion)

    def upload_new_form(self, rol, fecha_inscripcion, fojas, nro_inscripcion, adquirientes):
        ano_vigencia_inicial = fecha_inscripcion.year
        ano_inscripcion = fecha_inscripcion.year
        ano_vigencia_final = None
        multipropietario_id = self.multipropietario_handler.upload_form(rol, fecha_inscripcion, fojas, nro_inscripcion, ano_inscripcion, ano_vigencia_inicial, ano_vigencia_final)
        self.multipropietario_handler.upload_propietarios(adquirientes, multipropietario_id)

    def update_previous_form(self, prev_form, fecha_inscripcion):
        ano_vigencia_final = fecha_inscripcion.year - 1
        self.multipropietario_handler.update_form(prev_form.id, ano_vigencia_final)

    def delete_previous_form(self, prev_form):
        self.multipropietario_handler.delete(prev_form.id)

    def reupload_forms(self, new_form_data):
        new_form_data['id'] = 0

        posterior_forms = self.multipropietario_handler.get_posterior_forms(new_form_data)
        forms_to_reupload = [new_form_data] + [self.multipropietario_handler.multipropietario_to_dict(form) for form in posterior_forms]

        forms_to_reupload.sort(key=lambda x: x['fecha_inscripcion'])

        for form_data in forms_to_reupload:
            form_id = form_data['id']

            if form_id:
                form_data['adquirientes'] = self.multipropietario_handler.get_linked_propietarios(form_id)
                self.multipropietario_handler.delete(form_id)

        for form_data in forms_to_reupload:
            self.execute(form_data)
            print(form_data['id'])
            db.session.commit()

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
    
    def upload_propietarios(self, adquirientes, multipropietario_id):
        self.propietario_handler.upload_propietario(adquirientes, multipropietario_id)

    def update_form(self, form_id, ano_vigencia_final):
        form = Multipropietario.query.get(form_id)
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

class PropietarioTableHandler:
    def upload_propietario(self, adquirientes, multipropietario_id):
        for adquiriente in adquirientes:
            propietario = Propietario(rut=adquiriente['rut'], porcentaje_derecho=adquiriente['pctje_derecho'], multipropietario_id=multipropietario_id)
            db.session.add(propietario)
        db.session.commit()

    def get_by_multipropietario_id(self, multipropietario_id):
        return Propietario.query.filter_by(multipropietario_id=multipropietario_id).all()

    def delete(self, propietario):
        db.session.delete(propietario)
        db.session.commit()
