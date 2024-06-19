from ....table_handlers.multipropietario import MultipropietarioTableHandler
from app.models import db

class AlgoritmoRegularizacionPatrimonio:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def apply_algorithm_on(self, new_form):
        rol = new_form.get('rol', None)
        fecha_inscripcion = new_form.get('fecha_inscripcion', None)

        existing_forms = self.get_existing_forms(rol)
        if not existing_forms:
            self.upload_new_form(new_form)
        else:
            same_year_forms = [self.multipropietario_handler.multipropietario_to_dict(form) for form in existing_forms if form.fecha_inscripcion.year == fecha_inscripcion.year]
            if same_year_forms:
                for form in same_year_forms:
                    self.multipropietario_handler.delete(form['id'])
                db.session.commit()
                forms_to_reupload = same_year_forms + [new_form]
                forms_to_reupload.sort(key=lambda x: x['fecha_inscripcion'])
                for form in forms_to_reupload:
                    self.recurse_algorithm(form)
            else:
                self.recurse_algorithm(new_form)

    def recurse_algorithm(self, form_data):
        rol = form_data.get('rol', None)
        fecha_inscripcion = form_data.get('fecha_inscripcion', None)

        existing_forms = self.get_existing_forms(rol)
        if not existing_forms:
            self.upload_new_form(form_data)
        else:
            prev_form = self.get_most_recent_previous_form(existing_forms, fecha_inscripcion)
            if not self.check_posterior_forms(existing_forms, fecha_inscripcion) and prev_form:
                self.update_previous_form(prev_form, fecha_inscripcion)
                self.upload_new_form(form_data)

            elif self.check_posterior_forms(existing_forms, fecha_inscripcion) and prev_form:
                self.update_previous_form(prev_form, fecha_inscripcion)
                self.reupload_forms(form_data)

            else:
                self.reupload_forms(form_data)

    def get_existing_forms(self, rol):
        return self.multipropietario_handler.get_forms_by_rol(rol)

    def get_latest_form(self, forms):
        return max(forms, key=lambda x: x.fecha_inscripcion)

    def get_most_recent_previous_form(self, forms, target_fecha_inscripcion):
        previous_forms = [form for form in forms if form.fecha_inscripcion < target_fecha_inscripcion]
        if previous_forms:
            return max(previous_forms, key=lambda x: x.fecha_inscripcion)
        return None

    def check_posterior_forms(self, forms, target_fecha_inscripcion):
        posterior_forms = [form for form in forms if form.fecha_inscripcion > target_fecha_inscripcion]
        if posterior_forms:
            return True
        return None

    def upload_new_form(self, form_data):
        rol = form_data.get('rol', None)
        fecha_inscripcion = form_data.get('fecha_inscripcion', None)
        nro_inscripcion = form_data.get('nro_inscripcion', None)
        fojas = form_data.get('fojas', None)
        adquirientes = form_data.get('adquirientes', [])
        ano_vigencia_inicial = fecha_inscripcion.year
        ano_inscripcion = fecha_inscripcion.year
        ano_vigencia_final = None
        multipropietario_id = self.multipropietario_handler.upload_form(
            rol, fecha_inscripcion, fojas, nro_inscripcion,
            ano_inscripcion, ano_vigencia_inicial, ano_vigencia_final
        )
        self.multipropietario_handler.upload_adquirientes(adquirientes, multipropietario_id)

    def upload_json_form(self, form_data):
        rol = form_data["rol"]
        fecha_inscripcion = form_data['fecha_inscripcion']
        nro_inscripcion = form_data['nro_inscripcion']
        fojas = form_data['fojas']
        adquirientes = form_data['adquirientes']
        ano_vigencia_inicial = form_data['fecha_inscripcion'].year
        ano_inscripcion = form_data['fecha_inscripcion'].year
        ano_vigencia_final = None
        multipropietario_id = self.multipropietario_handler.upload_form(
            rol, fecha_inscripcion, fojas, nro_inscripcion,
            ano_inscripcion, ano_vigencia_inicial, ano_vigencia_final
        )
        print("nro_inscripcion", nro_inscripcion, adquirientes)
        self.multipropietario_handler.upload_adquirientes(adquirientes, multipropietario_id)

    def update_previous_form(self, prev_form, fecha_inscripcion):
        ano_vigencia_final = fecha_inscripcion.year - 1
        self.multipropietario_handler.update_form(prev_form.id, ano_vigencia_final)

    def reupload_forms(self, new_form_data):
        new_form_data['id'] = 0

        posterior_forms = self.multipropietario_handler.get_posterior_forms(new_form_data)
        forms_to_reupload = [new_form_data] + [self.multipropietario_handler.multipropietario_to_dict(form) for form in posterior_forms]
        forms_to_reupload.sort(key=lambda x: x['fecha_inscripcion'])
        for form_data in forms_to_reupload:
            if form_data['id']:
                form_data['adquirientes'] = self.multipropietario_handler.get_linked_propietarios(form_data['id'])
                self.multipropietario_handler.delete(form_data['id'])
        
        self.upload_json_form(forms_to_reupload[0])
        for form_data in forms_to_reupload[1:]:
            existing_forms = self.get_existing_forms(form_data["rol"])
            prev_form = self.get_latest_form(existing_forms)
            self.update_previous_form(prev_form, form_data["fecha_inscripcion"])
            self.upload_json_form(form_data)
            db.session.commit()

