from .....table_handlers.multipropietario import MultipropietarioTableHandler

class HandleScenario2:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def handle(self, form_data, current_propietarios):
        self._update_previous_forms(current_propietarios, form_data)
        temp_storage = self._prepare_temp_storage(form_data, current_propietarios)
        temp_storage = self._adjust_percentages(temp_storage, form_data)
        temp_storage = self._finalize_entries(temp_storage, form_data)
        return temp_storage
    
    def _update_previous_forms(self, prev_storage, form_data):
        for entry in prev_storage:
            self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data['fecha_inscripcion'].year - 1)

    def _prepare_temp_storage(self, form_data, current_propietarios):
        temp_storage = self._initialize_temp_storage(form_data)
        self._populate_temp_storage(temp_storage, form_data, current_propietarios)
        return temp_storage
    
    def _initialize_temp_storage(self, form_data):
        temp_storage = []

        for enajenante in form_data.get('enajenantes', []):
            temp_storage.append(self._create_temp_entry(enajenante, form_data, False))

        for adquiriente in form_data.get('adquirientes', []):
            temp_storage.append(self._create_temp_entry(adquiriente, form_data, True))

        return temp_storage
    
    def _create_temp_entry(self, person_data, form_data, adquiriente_flag):
        return {
            'rut': person_data['rut'],
            'porcentaje_derecho': person_data['porcentaje_derecho'] if adquiriente_flag else 0,
            'id': None,
            'rol': form_data['rol'],
            'fecha_inscripcion': form_data['fecha_inscripcion'] if adquiriente_flag else None,
            'ano_inscripcion': form_data['fecha_inscripcion'].year if adquiriente_flag else None,
            'fojas': form_data['fojas'] if adquiriente_flag else None,
            'nro_inscripcion': form_data['nro_inscripcion'] if adquiriente_flag else None,
            'ano_vigencia_inicial': form_data['fecha_inscripcion'].year,
            'ano_vigencia_final': None
        }

    def _populate_temp_storage(self, temp_storage, form_data, current_propietarios):
        enajenantes_ruts = [enajenante['rut'] for enajenante in form_data.get('enajenantes', [])]
        adquirientes_ruts = [adquiriente['rut'] for adquiriente in form_data.get('adquirientes', [])]

        for propietario in current_propietarios:
            if propietario['rut'] in enajenantes_ruts or propietario['rut'] in adquirientes_ruts:
                for entry in temp_storage:
                    if entry['rut'] == propietario['rut']:
                        entry['porcentaje_derecho'] += propietario['porcentaje_derecho']
                        break
            else:
                temp_storage.append(propietario)

    def _adjust_percentages(self, temp_storage, form_data):
        enajenantes_ruts = [enajenante['rut'] for enajenante in form_data.get('enajenantes', [])]
        adquirientes_ruts = [adquiriente['rut'] for adquiriente in form_data.get('adquirientes', [])]

        suma_porcentaje_derecho_enajenantes = sum(entry['porcentaje_derecho'] for entry in temp_storage if entry['rut'] in enajenantes_ruts and not entry['fecha_inscripcion'])
        if not suma_porcentaje_derecho_enajenantes:
            suma_porcentaje_derecho_enajenantes = 100
        
        suma_porcentaje_derecho_adquirientes = sum(entry['porcentaje_derecho'] for entry in temp_storage if entry['rut'] in adquirientes_ruts)
        if suma_porcentaje_derecho_adquirientes:
            for entry in temp_storage:
                if entry['rut'] in adquirientes_ruts:
                    entry['porcentaje_derecho'] *= suma_porcentaje_derecho_enajenantes / 100
        else:
            porcentaje_derecho_adquirientes = suma_porcentaje_derecho_enajenantes / len(adquirientes_ruts)
            for entry in temp_storage:
                if entry['rut'] in adquirientes_ruts:
                    entry['porcentaje_derecho'] += porcentaje_derecho_adquirientes
        
        return temp_storage

    def _finalize_entries(self, temp_storage, form_data):
        temp_storage = [entry for entry in temp_storage if entry['fecha_inscripcion']]
        temp_storage = [entry for entry in temp_storage if entry['porcentaje_derecho'] > 0]
        for entry in temp_storage:
            if 'multipropietario_id' in entry:
                del entry['multipropietario_id']
            entry['ano_vigencia_inicial'] = form_data['fecha_inscripcion'].year
            entry['ano_vigencia_final'] = None
            
        return temp_storage
