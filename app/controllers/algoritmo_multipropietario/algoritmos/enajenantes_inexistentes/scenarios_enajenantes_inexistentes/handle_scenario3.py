from .....table_handlers.multipropietario import MultipropietarioTableHandler

class HandleScenario3:
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
        temp_storage = self._initialize_temp_storage(form_data, current_propietarios)
        self._adjust_temp_storage(temp_storage, form_data, current_propietarios)
        return temp_storage
    
    def _initialize_temp_storage(self, form_data, current_propietarios):
        temp_storage = []

        temp_storage.extend(self._initialize_enajenantes(form_data, current_propietarios))
        temp_storage.extend(self._initialize_adquirientes(form_data, current_propietarios))
        
        return temp_storage

    def _initialize_enajenantes(self, form_data, current_propietarios):
        enajenantes = form_data.get('enajenantes', [])
        current_propietarios_ruts = [propietario['rut'] for propietario in current_propietarios]

        temp_storage = []
        for enajenante in enajenantes:
            if enajenante['rut'] in current_propietarios_ruts:
                for propietario in current_propietarios:
                    if enajenante['rut'] == propietario['rut']:
                        temp_storage.append({
                            'rut': propietario['rut'],
                            'porcentaje_derecho': enajenante['porcentaje_derecho'],
                            'id': None,
                            'rol': propietario['rol'],
                            'fecha_inscripcion': propietario['fecha_inscripcion'],
                            'ano_inscripcion': propietario['fecha_inscripcion'].year,
                            'fojas': propietario['fojas'],
                            'nro_inscripcion': propietario['nro_inscripcion'],
                            'ano_vigencia_inicial': propietario['fecha_inscripcion'].year,
                            'ano_vigencia_final': None
                        })
                        break
            else:
                temp_storage.append({
                    'rut': enajenante['rut'],
                    'porcentaje_derecho': 0, 
                    'id': None,
                    'rol': form_data['rol'],
                    'fecha_inscripcion': None,
                    'ano_inscripcion': None,
                    'fojas': None,
                    'nro_inscripcion': None,
                    'ano_vigencia_inicial': form_data['fecha_inscripcion'].year,
                    'ano_vigencia_final': None
                })
        
        return temp_storage

    def _initialize_adquirientes(self, form_data, current_propietarios):
        adquirientes = form_data.get('adquirientes', [])
        current_propietarios_ruts = [propietario['rut'] for propietario in current_propietarios]

        temp_storage = []
        for adquiriente in adquirientes:
            if adquiriente['rut'] in current_propietarios_ruts:
                for propietario in current_propietarios:
                    if adquiriente['rut'] == propietario['rut']:
                        temp_storage.append({
                            'rut': propietario['rut'],
                            'porcentaje_derecho': adquiriente['porcentaje_derecho'],
                            'id': None,
                            'rol': propietario['rol'],
                            'fecha_inscripcion': propietario['fecha_inscripcion'],
                            'ano_inscripcion': propietario['fecha_inscripcion'].year,
                            'fojas': propietario['fojas'],
                            'nro_inscripcion': propietario['nro_inscripcion'],
                            'ano_vigencia_inicial': propietario['fecha_inscripcion'].year,
                            'ano_vigencia_final': None
                        })
                        break
            else:
                temp_storage.append({
                    'rut': adquiriente['rut'],
                    'porcentaje_derecho': adquiriente['porcentaje_derecho'],
                    'id': None,
                    'rol': form_data['rol'],
                    'fecha_inscripcion': form_data['fecha_inscripcion'],
                    'ano_inscripcion': form_data['fecha_inscripcion'].year,
                    'fojas': form_data['fojas'],
                    'nro_inscripcion': form_data['nro_inscripcion'],
                    'ano_vigencia_inicial': form_data['fecha_inscripcion'].year,
                    'ano_vigencia_final': None
                })
        
        return temp_storage

    def _adjust_temp_storage(self, temp_storage, form_data, current_propietarios):
        enajenantes_ruts = {enajenante['rut'] for enajenante in form_data.get('enajenantes', [])}
        adquirientes_ruts = {adquiriente['rut'] for adquiriente in form_data.get('adquirientes', [])}
        
        for propietario in current_propietarios:
            if propietario['rut'] in enajenantes_ruts or propietario['rut'] in adquirientes_ruts:
                for entry in temp_storage:
                    if entry['rut'] == propietario['rut'] and propietario['rut'] in enajenantes_ruts:
                        entry['porcentaje_derecho'] -= propietario['porcentaje_derecho']
                        entry['porcentaje_derecho'] *= -1
                        entry['porcentaje_derecho'] = max(entry['porcentaje_derecho'], 0)
                        break
                    elif entry['rut'] == propietario['rut'] and propietario['rut'] in adquirientes_ruts:
                        entry['porcentaje_derecho'] += propietario['porcentaje_derecho']
                        break
            else: 
                temp_storage.append(propietario)

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
            if 'multipropietario_id' in entry:
                del entry['multipropietario_id']
            entry['ano_vigencia_inicial'] = form_data['fecha_inscripcion'].year
            entry['ano_vigencia_final'] = None
            
        return temp_storage
