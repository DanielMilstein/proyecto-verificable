from ..table_handlers.multipropietario import MultipropietarioTableHandler
from app.models import db

class AlgoritmoCompraventa:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def apply_algorithm_on(self, form_data):
        adquirientes = form_data.get('adquirientes', [])
        enajenantes = form_data.get('enajenantes', [])
        
        if self.is_scenario_1(adquirientes):

            self.handle_scenario_1(form_data)
        elif self.is_scenario_2(adquirientes):
            self.handle_scenario_2(form_data)
        elif self.is_scenario_3(adquirientes, enajenantes):
            self.handle_scenario_3(form_data)
        else:
            self.handle_scenario_4(form_data)

    def is_scenario_1(self, adquirientes):
        return sum(adquiriente.get('pctje_derecho', 0) for adquiriente in adquirientes) == 100

    def handle_scenario_1(self, form_data):
        rol = form_data.get('rol')

        all_forms = self.get_existing_forms(rol)
        previous_form = self.get_latest_form(all_forms)
        prev_storage = self.store_form_data(previous_form)

        for entry in prev_storage:
            self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data.get('fecha_inscripcion').year - 1)

        enajenantes_ruts = [enajenante.get('rut') for enajenante in form_data.get('enajenantes', [])]
        sum_porcentaje_enajenantes = sum([self.find_porcentaje_derecho(previous_form.id, rut) for rut in enajenantes_ruts])
        temp_storage = [entry for entry in prev_storage if entry['rut'] not in enajenantes_ruts]
        
        adquirientes_ruts = []
        for adquiriente in form_data.get('adquirientes', []):
            adquirientes_ruts.append(adquiriente.get("rut", None))
            entry = {
                    'id': None,
                    'rol': rol,
                    'fecha_inscripcion': form_data.get("fecha_inscripcion"),
                    'fojas': form_data.get("fojas", None),
                    'nro_inscripcion': form_data.get("nro_inscripcion"),
                    'rut': adquiriente.get("rut", None),
                    'porcentaje_derecho': adquiriente.get("pctje_derecho")*sum_porcentaje_enajenantes/100,
                    'ano_vigencia_final': None
            }
            temp_storage.append(entry)

        for entry in temp_storage:
            if (entry['rut'] in enajenantes_ruts) or (entry['rut'] in adquirientes_ruts):
                entry['ano_inscripcion'] = form_data.get('fecha_inscripcion').year
            else:
                del entry['multipropietario_id']
                entry['id'] = None
            entry['ano_vigencia_inicial'] = form_data.get('fecha_inscripcion').year
            entry['ano_vigencia_final'] = None

        for entry in temp_storage:
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
                    'id': propietario.propietario_id,
                    'multipropietario_id': previous_form.id,
                    'rol': previous_form.rol,
                    'fecha_inscripcion': previous_form.fecha_inscripcion,
                    'fojas': previous_form.fojas,
                    'nro_inscripcion': previous_form.numero_inscripcion,
                    'rut': propietario.rut,
                    'porcentaje_derecho': propietario.porcentaje_derecho,
                    'ano_inscripcion': previous_form.ano_inscripcion,
                    'ano_vigencia_inicial': previous_form.ano_vigencia_inicial,
                    'ano_vigencia_final': previous_form.ano_vigencia_final
                }
                temp_storage.append(entry)
        return temp_storage

    def find_porcentaje_derecho(self, previous_form_id, rut):
        propietarios = self.multipropietario_handler.get_linked_propietarios(previous_form_id)
        for propietario in propietarios:
            if propietario.get("rut") == rut:
                return propietario.get("pctje_derecho")
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
        repeated_multipropietarios = self.multipropietario_handler.check_if_propietario_exists(entry['rut'], entry['rol'], entry['ano_vigencia_inicial'])
        if repeated_multipropietarios:
            for multipropietario in repeated_multipropietarios:
                self.multipropietario_handler.delete(multipropietario.id)
        new_multipropietario_id = self.upload_multipropietario(entry)
        self.multipropietario_handler.upload_propietario(
            {'rut': entry['rut'], 'porcentaje_derecho': entry['porcentaje_derecho']}, 
            new_multipropietario_id
        )

    def is_scenario_2(self, adquirientes):
        return sum(adquiriente.get('pctje_derecho', 0) for adquiriente in adquirientes) == 0
    
    def handle_scenario_2(self, form_data):
        rol = form_data.get('rol')
        all_forms = self.get_existing_forms(rol)
        previous_form = self.get_latest_form(all_forms)
        prev_storage = self.store_form_data(previous_form)

        for entry in prev_storage:
            self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data.get('fecha_inscripcion').year - 1)

        enajenantes_ruts = [enajenante.get('rut') for enajenante in form_data.get('enajenantes', [])]
        sum_porcentaje_enajenantes = sum([self.find_porcentaje_derecho(previous_form.id, rut) for rut in enajenantes_ruts])
        temp_storage = [entry for entry in prev_storage if entry['rut'] not in enajenantes_ruts]

        num_adquirientes = len(form_data.get('adquirientes', []))
        new_porcentaje_derecho = sum_porcentaje_enajenantes / num_adquirientes

        adquirientes_ruts = []
        for adquiriente in form_data.get('adquirientes', []):
            adquirientes_ruts.append(adquiriente.get("rut", None))
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
            if (entry['rut'] in enajenantes_ruts) or (entry['rut'] in adquirientes_ruts):
                entry['ano_inscripcion'] = form_data.get('fecha_inscripcion').year
            else:
                del entry['multipropietario_id']
                entry['id'] = None
            entry['ano_vigencia_inicial'] = form_data.get('fecha_inscripcion').year
            entry['ano_vigencia_final'] = None

        for entry in temp_storage:
            self.upload_propietario(entry)


    def is_scenario_3(self, adquirientes, enajenantes):
        return 0 < sum(adquiriente.get('pctje_derecho', 0) for adquiriente in adquirientes) < 100 and len(adquirientes) == 1 and len(enajenantes) == 1

    def handle_scenario_3(self, form_data):
        rol = form_data.get('rol')
        all_forms = self.get_existing_forms(rol)
        previous_form = self.get_latest_form(all_forms)
        temp_storage = self.store_form_data(previous_form)

        for entry in temp_storage:
            self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data.get('fecha_inscripcion').year - 1)

        enajenante_rut = [enajenante.get('rut') for enajenante in form_data.get('enajenantes', [])][0]
        
        for adquiriente in form_data.get('adquirientes', []):
            adquiriente_rut = adquiriente.get("rut", None)
            entry = {
                'id': None,
                'rol': form_data.get("rol", None),
                'fecha_inscripcion': form_data.get("fecha_inscripcion"),
                'fojas': form_data.get("fojas", None),
                'nro_inscripcion': form_data.get("nro_inscripcion"),
                'rut': adquiriente.get("rut", None),
                'porcentaje_derecho': adquiriente.get("pctje_derecho"),
                'ano_vigencia_final': None
            }
            temp_storage.append(entry)
        
        for entry in temp_storage:
            if entry['rut'] == enajenante_rut:
                prev_porcentaje_derecho = entry['porcentaje_derecho']
                for enajenante in form_data.get('enajenantes', []):
                    if enajenante.get('rut') == entry['rut']:
                        enajenante_porcentaje = enajenante.get('pctje_derecho')
                        final_porcentaje_derecho_enajenante = prev_porcentaje_derecho - (enajenante_porcentaje/100 * prev_porcentaje_derecho)
                        entry['porcentaje_derecho'] = final_porcentaje_derecho_enajenante
                        break
        
        for entry in temp_storage:
            if entry["rut"] == adquiriente_rut:
                final_porcentaje_derecho_adquiriente = entry['porcentaje_derecho'] /100 * prev_porcentaje_derecho
                entry['porcentaje_derecho'] = final_porcentaje_derecho_adquiriente
                break

        temp_storage = [entry for entry in temp_storage if entry['porcentaje_derecho'] != 0]

        for entry in temp_storage:
            if (entry['rut'] == adquiriente_rut):
                entry['ano_inscripcion'] = form_data.get('fecha_inscripcion').year
            else:
                del entry['multipropietario_id']
                entry['id'] = None
            entry['ano_vigencia_inicial'] = form_data.get('fecha_inscripcion').year
            entry['ano_vigencia_final'] = None

        for entry in temp_storage:
            self.upload_propietario(entry)


    def handle_scenario_4(self, form_data):
        rol = form_data.get('rol')
        all_forms = self.get_existing_forms(rol)
        previous_form = self.get_latest_form(all_forms)
        temp_storage = self.store_form_data(previous_form)

        for entry in temp_storage:
            self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data.get('fecha_inscripcion').year - 1)

        adquirientes_ruts = []
        for adquiriente in form_data.get('adquirientes', []):
            adquirientes_ruts.append(adquiriente.get("rut", None))
            entry = {
                'id': None,
                'rol': form_data.get("rol", None),
                'fecha_inscripcion': form_data.get("fecha_inscripcion"),
                'fojas': form_data.get("fojas", None),
                'nro_inscripcion': form_data.get("nro_inscripcion"),
                'rut': adquiriente.get("rut", None),
                'porcentaje_derecho': adquiriente.get("pctje_derecho"),
                'ano_vigencia_final': None
            }
            temp_storage.append(entry)

        enajenantes_ruts = [enajenante.get('rut') for enajenante in form_data.get('enajenantes', [])]
        for entry in temp_storage:
            if entry['rut'] in enajenantes_ruts:
                prev_porcentaje_derecho = entry['porcentaje_derecho']
                for enajenante in form_data.get('enajenantes', []):
                    if enajenante.get('rut') == entry['rut']:
                        enajenante_porcentaje = enajenante.get('pctje_derecho')
                        final_porcentaje_derecho_enajenante = prev_porcentaje_derecho - enajenante_porcentaje
                        entry['porcentaje_derecho'] = final_porcentaje_derecho_enajenante
            
        temp_storage = [entry for entry in temp_storage if entry['porcentaje_derecho'] > 0]

        for entry in temp_storage:
            if (entry['rut'] in enajenantes_ruts) or (entry['rut'] in adquirientes_ruts):
                entry['ano_inscripcion'] = form_data.get('fecha_inscripcion').year
            else:
                del entry['multipropietario_id']
                entry['id'] = None
            entry['ano_vigencia_inicial'] = form_data.get('fecha_inscripcion').year
            entry['ano_vigencia_final'] = None
        print(temp_storage)
        for entry in temp_storage:
            self.upload_propietario(entry)

