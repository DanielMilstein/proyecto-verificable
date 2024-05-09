from ..table_handlers.multipropietario import MultipropietarioTableHandler
from app.models import db

class AlgoritmoCompraventa:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def apply_algorithm_on(self, form_data):
        rol = form_data.get('rol', None)
        fecha_inscripcion = form_data.get('fecha_inscripcion', None)
        nro_inscripcion = form_data.get('nro_inscripcion', None)
        fojas = form_data.get('fojas', None)
        adquirientes = form_data.get('adquirientes', [])
        enajenantes = form_data.get('enajenantes', [])
        
        if self.is_scenario_1(adquirientes):
            self.handle_scenario_1(form_data)
        elif self.is_scenario_2(adquirientes):
            pass
        elif self.is_scenario_3(adquirientes, enajenantes):
            pass
        else:
            pass

    def is_scenario_1(self, adquirientes):
        return sum(adquiriente.get('pctje_derecho', 0) for adquiriente in adquirientes) == 100

    def handle_scenario_1(self, form_data):
        rol = form_data.get('rol')
        all_forms = self.get_existing_forms(rol)
        previous_form = self.get_latest_form(all_forms)
        temp_storage = self.store_form_data(previous_form)

        # THIS IS WRONG, NEED TO UPDATE THEIR PREVIOUS ANO_VIGENCIA_FINAL 
        # => Method 'update_form' from multipropietarioTableHandler should do the trick.
        # Current one should be None
        for entry in temp_storage:
            entry['ano_vigencia_final'] = form_data.get('fecha_inscripcion').year - 1

        enajenantes_ruts = [enajenante.get('rut') for enajenante in form_data.get('enajenantes', [])]
        sum_porcentaje_enajenantes = sum([self.find_porcentaje_derecho(previous_form, rut) for rut in enajenantes_ruts])

        temp_storage = [entry for entry in temp_storage if entry['rut'] not in enajenantes_ruts]

        for adquiriente in form_data.get('adquirientes', []):
            entry = {
                    'id': None,
                    'rol': form_data.get("rol", None),
                    'fecha_inscripcion': form_data.get("fecha_inscripcion"),
                    'fojas': form_data.get("fojas", None),
                    'nro_inscripcion': form_data.get("nro_inscripcion"),
                    'rut': adquiriente.get("rut", None),
                    'porcentaje_derecho': adquiriente.get("pctje_derecho")*sum_porcentaje_enajenantes,
                    'ano_vigencia_final': None
            }
            temp_storage.append(entry)

        for entry in temp_storage:
            entry['ano_inscripcion'] = form_data.get('fecha_inscripcion').year
            if entry['id'] is None:
                entry['ano_vigencia_inicial'] = form_data.get('fecha_inscripcion').year

        for entry in temp_storage:
            if entry['id'] is None:
                self.upload_multipropietario(entry)
            else:
                self.upload_propietario(entry)

    def get_existing_forms(self, rol):
        return self.multipropietario_handler.get_forms_by_rol(rol)

    def get_latest_form(self, forms):
        return max(forms, key=lambda x: x.fecha_inscripcion)

    def store_form_data(self, previous_form):
        temp_storage = []
        if previous_form:
            propietarios = self.multipropietario_handler.propietario_handler.get_by_multipropietario_id(previous_form.id)
            for propietario in propietarios:
                entry = {
                    'id': propietario.id,
                    'multipropietario_id': previous_form.id,
                    'rol': previous_form.rol,
                    'fecha_inscripcion': previous_form.fecha_inscripcion,
                    'fojas': previous_form.fojas,
                    'nro_inscripcion': previous_form.nro_inscripcion,
                    'rut': propietario.rut,
                    'porcentaje_derecho': propietario.porcentaje_derecho,
                    'ano_inscripcion': previous_form.ano_inscripcion,
                    'ano_vigencia_inicial': previous_form.ano_vigencia_inicial,
                    'ano_vigencia_final': previous_form.ano_vigencia_final
                }
                temp_storage.append(entry)
        return temp_storage

    def find_porcentaje_derecho(self, previous_form, rut):
        for propietario in previous_form.propietarios:
            if propietario.rut == rut:
                return propietario.porcentaje_derecho
        return 0

    def upload_multipropietario(self, entry):
        new_form = self.multipropietario_handler.upload_form(
            entry['rol'], 
            entry['fecha_inscripcion'], 
            entry['fojas'], 
            entry['nro_inscripcion'], 
            entry['ano_inscripcion'], 
            entry['ano_vigencia_inicial'], 
            entry['ano_vigencia_final']
        )
        entry['id'] = new_form
        return entry['id']

    def upload_propietario(self, entry):
        self.upload_multipropietario(entry)
        self.multipropietario_handler.upload_propietario(
            {'rut': entry['rut'], 'porcentaje_derecho': entry['porcentaje_derecho']}, 
            entry['id']
        )

    def is_scenario_2(self, adquirientes):
        return sum(adquiriente.get('pctje_derecho', 0) for adquiriente in adquirientes) == 0
    
    def handle_scenario_2(self, form_data):
        rol = form_data.get('rol')
        all_forms = self.get_existing_forms(rol)
        previous_form = self.get_latest_form(all_forms)
        temp_storage = self.store_form_data(previous_form)

        # THIS IS WRONG, NEED TO UPDATE THEIR PREVIOUS ANO_VIGENCIA_FINAL 
        # => Method 'update_form' from multipropietarioTableHandler should do the trick.
        # Current one should be None
        for entry in temp_storage:
            entry['ano_vigencia_final'] = form_data.get('fecha_inscripcion').year - 1

        enajenantes_ruts = [enajenante.get('rut') for enajenante in form_data.get('enajenantes', [])]
        sum_porcentaje_enajenantes = sum([self.find_porcentaje_derecho(previous_form, rut) for rut in enajenantes_ruts])

        temp_storage = [entry for entry in temp_storage if entry['rut'] not in enajenantes_ruts]

        num_adquirientes = len(form_data.get('adquirientes', []))
        new_porcentaje_derecho = sum_porcentaje_enajenantes / num_adquirientes

        for adquiriente in form_data.get('adquirientes', []):
            entry = {
                'id': None,
                'rol': form_data.get("rol", None),
                'fecha_inscripcion': form_data.get("fecha_inscripcion"),
                'fojas': form_data.get("fojas", None),
                'nro_inscripcion': form_data.get("nro_inscripcion"),
                'rut': adquiriente.get("rut", None),
                'porcentaje_derecho': new_porcentaje_derecho,
                'ano_vigencia_final': None
            }
            temp_storage.append(entry)

        for entry in temp_storage:
            entry['ano_inscripcion'] = form_data.get('fecha_inscripcion').year
            if entry['id'] is None:
                entry['ano_vigencia_inicial'] = form_data.get('fecha_inscripcion').year

        for entry in temp_storage:
            if entry['id'] is None:
                self.upload_multipropietario(entry)
            else:
                self.upload_propietario(entry)


    def is_scenario_3(self, adquirientes, enajenantes):
        return 0 < sum(adquiriente.get('pctje_derecho', 0) for adquiriente in adquirientes) < 100 and len(adquirientes) == 1 and len(enajenantes) == 1

    def handle_scenario_3(self, form_data):
        rol = form_data.get('rol')
        all_forms = self.get_existing_forms(rol)
        previous_form = self.get_latest_form(all_forms)
        temp_storage = self.store_form_data(previous_form)

        # THIS IS WRONG, NEED TO UPDATE THEIR PREVIOUS ANO_VIGENCIA_FINAL 
        # => Method 'update_form' from multipropietarioTableHandler should do the trick.
        # Current one should be None
        for entry in temp_storage:
            entry['ano_vigencia_final'] = form_data.get('fecha_inscripcion').year - 1

        enajenantes_ruts = [enajenante.get('rut') for enajenante in form_data.get('enajenantes', [])]

        for adquiriente in form_data.get('adquirientes', []):
            entry = {
                'id': None,
                'rol': form_data.get("rol", None),
                'fecha_inscripcion': form_data.get("fecha_inscripcion"),
                'fojas': form_data.get("fojas", None),
                'nro_inscripcion': form_data.get("nro_inscripcion"),
                'rut': adquiriente.get("rut", None),
                'ano_vigencia_final': None
            }
            temp_storage.append(entry)

        for entry in temp_storage:
            if entry['rut'] in enajenantes_ruts:
                prev_porcentaje_derecho = entry['porcentaje_derecho']
                for enajenante in form_data.get('enajenantes', []):
                    if enajenante.get('rut') == entry['rut']:
                        enajenante_porcentaje = enajenante.get('pctje_derecho')
                        final_porcentaje_derecho_enajenante = prev_porcentaje_derecho - (enajenante_porcentaje * prev_porcentaje_derecho)
                        entry['porcentaje_derecho'] = final_porcentaje_derecho_enajenante
            else:
                for adquiriente in form_data.get('adquirientes', []):
                    if adquiriente.get('rut') == entry['rut']:
                        adquiriente_porcentaje = adquiriente.get('pctje_derecho')
                        final_porcentaje_derecho_adquiriente = adquiriente_porcentaje * entry['porcentaje_derecho']
                        entry['porcentaje_derecho'] = final_porcentaje_derecho_adquiriente

        temp_storage = [entry for entry in temp_storage if entry['porcentaje_derecho'] != 0]

        for entry in temp_storage:
            entry['ano_inscripcion'] = form_data.get('fecha_inscripcion').year
            if entry['id'] is None:
                entry['ano_vigencia_inicial'] = form_data.get('fecha_inscripcion').year

        for entry in temp_storage:
            if entry['id'] is None:
                self.upload_multipropietario(entry)
            else:
                self.upload_propietario(entry)


    def handle_scenario_4(self, form_data):
        rol = form_data.get('rol')
        all_forms = self.get_existing_forms(rol)
        previous_form = self.get_latest_form(all_forms)
        temp_storage = self.store_form_data(previous_form)

        for entry in temp_storage:
            if entry['rut'] in [enajenante.get('rut') for enajenante in form_data.get('enajenantes', [])]:
                prev_porcentaje_derecho = entry['porcentaje_derecho']
                for enajenante in form_data.get('enajenantes', []):
                    if enajenante.get('rut') == entry['rut']:
                        enajenante_porcentaje = enajenante.get('pctje_derecho')
                        final_porcentaje_derecho_enajenante = prev_porcentaje_derecho - enajenante_porcentaje
                        entry['porcentaje_derecho'] = final_porcentaje_derecho_enajenante
            else:
                for adquiriente in form_data.get('adquirientes', []):
                    if adquiriente.get('rut') == entry['rut']:
                        if entry['id'] is None:
                            entry['porcentaje_derecho'] = adquiriente.get('pctje_derecho')
                        else:
                            entry['porcentaje_derecho'] += adquiriente.get('pctje_derecho')

        temp_storage = [entry for entry in temp_storage if entry['porcentaje_derecho'] > 0]

        for entry in temp_storage:
            entry['ano_vigencia_final'] = form_data.get('fecha_inscripcion').year - 1

        for entry in temp_storage:
            entry['ano_inscripcion'] = form_data.get('fecha_inscripcion').year
            if entry['id'] is None:
                entry['ano_vigencia_inicial'] = form_data.get('fecha_inscripcion').year

        for entry in temp_storage:
            if entry['id'] is None:
                self.upload_multipropietario(entry)
            else:
                self.upload_propietario(entry)

