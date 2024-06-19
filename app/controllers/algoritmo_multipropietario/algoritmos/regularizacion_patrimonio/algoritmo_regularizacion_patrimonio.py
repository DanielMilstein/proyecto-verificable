from ....table_handlers.multipropietario import MultipropietarioTableHandler
from app.models import db

class AlgoritmoRegularizacionPatrimonio:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def apply_algorithm_on(self, new_form):
        rol = new_form.get('rol')
        fecha_inscripcion = new_form.get('fecha_inscripcion')

        existing_forms = self.get_existing_forms(rol)
        if not existing_forms:
            self.upload_form(new_form)
        else:
            same_year_forms = self.get_forms_by_year(existing_forms, fecha_inscripcion.year)
            if same_year_forms:
                self.handle_same_year_forms(same_year_forms, new_form)
            else:
                self.recurse_algorithm(new_form)

    def get_existing_forms(self, rol):
        return self.multipropietario_handler.get_forms_by_rol(rol)

    def get_forms_by_year(self, forms, year):
        return [self.multipropietario_handler.multipropietario_to_dict(form) for form in forms if form.fecha_inscripcion.year == year]

    def get_most_recent_previous_form(self, forms, target_fecha_inscripcion):
        previous_forms = [form for form in forms if form.fecha_inscripcion < target_fecha_inscripcion]
        return max(previous_forms, key=lambda x: x.fecha_inscripcion) if previous_forms else None

    def check_posterior_forms(self, forms, target_fecha_inscripcion):
        return any(form for form in forms if form.fecha_inscripcion > target_fecha_inscripcion)

    def recurse_algorithm(self, form_data):
        rol = form_data.get('rol')
        fecha_inscripcion = form_data.get('fecha_inscripcion')

        existing_forms = self.get_existing_forms(rol)
        if not existing_forms:
            self.upload_form(form_data)
        else:
            prev_form = self.get_most_recent_previous_form(existing_forms, fecha_inscripcion)
            if prev_form:
                self.update_previous_form(prev_form, fecha_inscripcion)
            if self.check_posterior_forms(existing_forms, fecha_inscripcion):
                self.reupload_forms(form_data)
            else:
                self.upload_form(form_data)

    def upload_form(self, form_data):
        rol = form_data.get('rol')
        fecha_inscripcion = form_data.get('fecha_inscripcion')
        nro_inscripcion = form_data.get('nro_inscripcion')
        fojas = form_data.get('fojas')
        adquirientes = form_data.get('adquirientes', [])
        ano_vigencia_inicial = fecha_inscripcion.year
        ano_inscripcion = fecha_inscripcion.year
        ano_vigencia_final = None

        multipropietario_id = self.multipropietario_handler.upload_form(
            rol, fecha_inscripcion, fojas, nro_inscripcion,
            ano_inscripcion, ano_vigencia_inicial, ano_vigencia_final
        )
        self.multipropietario_handler.upload_adquirientes(adquirientes, multipropietario_id)

    def update_previous_form(self, prev_form, fecha_inscripcion):
        ano_vigencia_final = fecha_inscripcion.year - 1
        self.multipropietario_handler.update_form(prev_form.id, ano_vigencia_final)

    def handle_same_year_forms(self, same_year_forms, new_form):
        for form in same_year_forms:
            self.multipropietario_handler.delete(form['id'])
        db.session.commit()

        forms_to_reupload = same_year_forms + [new_form]
        forms_to_reupload.sort(key=lambda x: x['fecha_inscripcion'])

        for form in forms_to_reupload:
            self.recurse_algorithm(form)

    def reupload_forms(self, new_form_data):
        new_form_data['id'] = 0
        posterior_forms = self.multipropietario_handler.get_posterior_forms(new_form_data)

        forms_to_reupload = [new_form_data] + [self.multipropietario_handler.multipropietario_to_dict(form) for form in posterior_forms]
        forms_to_reupload.sort(key=lambda x: x['fecha_inscripcion'])

        for form_data in forms_to_reupload:
            if form_data['id']:
                form_data['adquirientes'] = self.multipropietario_handler.get_linked_propietarios(form_data['id'])
                self.multipropietario_handler.delete(form_data['id'])

        for form_data in forms_to_reupload:
            self.upload_form(form_data)
            db.session.commit()
