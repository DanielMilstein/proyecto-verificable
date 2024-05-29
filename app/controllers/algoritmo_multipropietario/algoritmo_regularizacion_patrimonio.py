from ..table_handlers.multipropietario import MultipropietarioTableHandler
from app.models import db

class AlgoritmoRegularizacionPatrimonio:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def apply_algorithm_on(self, form_data):
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
        self.multipropietario_handler.upload_adquirientes(adquirientes, multipropietario_id)

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
            self.apply_algorithm_on(form_data)
            print(form_data['id'])
            db.session.commit()