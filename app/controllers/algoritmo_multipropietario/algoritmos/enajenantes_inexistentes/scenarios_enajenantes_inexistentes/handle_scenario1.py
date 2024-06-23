from .....table_handlers.multipropietario import MultipropietarioTableHandler
class HandleScenario1:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def handle(self, form_data, current_propietarios):
        self._update_previous_forms(current_propietarios, form_data)
        temp_storage = self._prepare_temp_storage(form_data, current_propietarios)
        temp_storage = self._adjust_percentages(temp_storage)
        temp_storage = self._finalize_entries(temp_storage, form_data)
        return temp_storage
    
    def _update_previous_forms(self, prev_storage, form_data):
        for entry in prev_storage:
            self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data['fecha_inscripcion'].year - 1)
    
    def _prepare_temp_storage(self, form_data, current_propietarios):
        temp_storage = []
        enajenantes_ruts = []
        adquirientes_ruts = []

        for enajenante in form_data.get('enajenantes', []):
            enajenantes_ruts.append(enajenante['rut'])
            temp_storage.append(self._create_temp_entry(enajenante, form_data, False))

        for adquiriente in form_data.get('adquirientes', []):
            adquirientes_ruts.append(adquiriente['rut'])
            temp_storage.append(self._create_temp_entry(adquiriente, form_data, True))
        
        for propietario in current_propietarios:
            if propietario['rut'] in enajenantes_ruts or propietario['rut'] in adquirientes_ruts:
                for entry in temp_storage:
                    if entry['rut'] == propietario['rut']:
                        entry['porcentaje_derecho'] += propietario['porcentaje_derecho']
                        break
            else: 
                temp_storage.append(propietario)

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

    def _adjust_percentages(self, temp_storage):
        total_porcentaje_derecho = sum(entry['porcentaje_derecho'] for entry in temp_storage)

        if total_porcentaje_derecho < 100:
            remaining_porcentaje = 100 - total_porcentaje_derecho
            zero_porcentaje_entries = [entry for entry in temp_storage if entry['porcentaje_derecho'] == 0]
            if zero_porcentaje_entries:
                share = remaining_porcentaje / len(zero_porcentaje_entries)
                for entry in zero_porcentaje_entries:
                    entry['porcentaje_derecho'] = share
        
        elif total_porcentaje_derecho >= 100:
            scale_factor = 100 / total_porcentaje_derecho
            for entry in temp_storage:
                entry['porcentaje_derecho'] *= scale_factor
        
        return temp_storage

    def _finalize_entries(self, temp_storage, form_data):
        temp_storage = [entry for entry in temp_storage if entry['porcentaje_derecho'] > 0]
        for entry in temp_storage:
            entry.pop('multipropietario_id', None)
            entry['ano_vigencia_inicial'] = form_data['fecha_inscripcion'].year if 'fecha_inscripcion' in form_data else None
            entry['ano_vigencia_final'] = None
            
        return temp_storage