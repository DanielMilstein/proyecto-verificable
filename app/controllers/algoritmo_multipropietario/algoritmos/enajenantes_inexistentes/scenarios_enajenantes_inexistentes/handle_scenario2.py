from .....table_handlers.multipropietario import MultipropietarioTableHandler

class HandleScenario2:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def handle(self, form_data, current_propietarios):
        self._update_previous_forms(current_propietarios, form_data)

        temp_storage = []
        adquirientes = form_data.get('adquirientes', [])
        enajenantes = form_data.get('enajenantes', [])
        enajenantes_ruts = []
        for enajenante in enajenantes:
            enajenantes_ruts.append(enajenante['rut'])
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

        adquirientes_ruts = []
        for adquiriente in adquirientes:
            adquirientes_ruts.append(adquiriente['rut'])
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
        
        for propietario in current_propietarios:
            if propietario['rut'] in enajenantes_ruts or propietario['rut'] in adquirientes_ruts:
                for entry in temp_storage:
                    if entry['rut'] == propietario['rut']:
                        entry['porcentaje_derecho'] += propietario['porcentaje_derecho']
                        break
            else: 
                temp_storage.append(propietario)

        suma_porcentaje_derecho_enajenantes = sum(entry['porcentaje_derecho'] for entry in temp_storage if entry['rut'] in enajenantes_ruts)
        if not suma_porcentaje_derecho_enajenantes:
            suma_porcentaje_derecho_enajenantes = 100

        suma_porcentaje_derecho_adquirientes = sum(entry['porcentaje_derecho'] for entry in temp_storage if entry['rut'] in adquirientes_ruts)
        if suma_porcentaje_derecho_adquirientes:
            for entry in temp_storage:
                if entry['rut'] in adquirientes_ruts:
                    entry['porcentaje_derecho'] *= suma_porcentaje_derecho_enajenantes
        else:
            porcentaje_derecho_adquirientes = suma_porcentaje_derecho_enajenantes / len(adquirientes_ruts)
            for entry in temp_storage:
                if entry['rut'] in adquirientes_ruts:
                    entry['porcentaje_derecho'] += porcentaje_derecho_adquirientes

        temp_storage = [entry for entry in temp_storage if entry['rut'] not in enajenantes_ruts]
        temp_storage = self._finalize_entries(temp_storage, form_data)
        return temp_storage
    
    def _update_previous_forms(self, prev_storage, form_data):
        for entry in prev_storage:
            self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data['fecha_inscripcion'].year - 1)

    def _finalize_entries(self, temp_storage, form_data):
        temp_storage = [entry for entry in temp_storage if entry['porcentaje_derecho'] > 0]
        for entry in temp_storage:
            if 'multipropietario_id' in entry:
                del entry['multipropietario_id']
            entry['ano_vigencia_inicial'] = form_data['fecha_inscripcion'].year
            entry['ano_vigencia_final'] = None
            
        return temp_storage


