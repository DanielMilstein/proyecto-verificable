from .....table_handlers.multipropietario import MultipropietarioTableHandler
class HandleScenario3():
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def handle(self, form_data, current_propietarios):
        rol = form_data['rol'] 
        temp_storage = current_propietarios

        enajenante_rut = [enajenante['rut'] for enajenante in form_data['enajenantes']][0]
        enajenante_porcentaje = [enajenante['porcentaje_derecho'] for enajenante in form_data['enajenantes']][0]

        self._update_previous_forms(temp_storage, form_data)

        for adquiriente in form_data['adquirientes']:
            adquiriente_rut = adquiriente['rut']
            adquiriente_porcentaje = adquiriente['porcentaje_derecho']
            entry = {
                'id': None,
                'rol': rol,
                'fecha_inscripcion': form_data['fecha_inscripcion'],
                'fojas': form_data['fojas'],
                'nro_inscripcion': form_data['nro_inscripcion'],
                'rut': adquiriente['rut'],
                'porcentaje_derecho':  adquiriente['porcentaje_derecho'],
                'ano_vigencia_inicial': form_data['fecha_inscripcion'].year,
                'ano_vigencia_final': None
            }
            temp_storage.append(entry)
        
        # Realmente intenté abstraerlo, pero no hubo caso :(
        #temp_storage = temp_storage + self._process_adquirientes(form_data)    
        

        temp_storage, prev_porcentaje_derecho = self._find_porcentaje_enajenante(temp_storage, enajenante_rut, enajenante_porcentaje, rol)

        adquiriente_porcentaje = adquiriente_porcentaje / 100 * prev_porcentaje_derecho
        temp_storage = self._find_porcentaje_adquiriente(temp_storage, adquiriente_rut, adquiriente_porcentaje)

        for entry in temp_storage:
            if entry['rut'] == adquiriente_rut:
               entry['ano_inscripcion'] = form_data['fecha_inscripcion'].year
            else:
                del entry['multipropietario_id']
                entry['id'] = None
            
            entry['ano_vigencia_inicial'] = form_data['fecha_inscripcion'].year
            entry['ano_vigencia_final'] = None
        return temp_storage
    
    def _update_previous_forms(self, temp_storage, form_data):
        for entry in temp_storage:
            self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data['fecha_inscripcion'].year - 1)
    
    def _find_porcentaje_enajenante(self, temp_storage, enajenante_rut, enajenante_porcentaje, rol):
        prev_porcentaje_derecho = 0
        for entry in temp_storage:
            if entry['rut'] == enajenante_rut:
                prev_porcentaje_derecho = entry['porcentaje_derecho']
                final_porcentaje_derecho_enajenante = prev_porcentaje_derecho - (enajenante_porcentaje / 100 * prev_porcentaje_derecho)
                entry['porcentaje_derecho'] = final_porcentaje_derecho_enajenante
                break

        if not prev_porcentaje_derecho and self.multipropietario_handler.get_porcentaje_derecho_propietario(enajenante_rut, rol):
            prev_porcentaje_derecho = self.multipropietario_handler.get_porcentaje_derecho_propietario(enajenante_rut, rol)
        
        return temp_storage, prev_porcentaje_derecho
    
    def _find_porcentaje_adquiriente(self, temp_storage, adquiriente_rut, adquiriente_porcentaje):
        for entry in temp_storage:
            if entry["rut"] == adquiriente_rut and not entry['id']:
                final_porcentaje_derecho_adquiriente = adquiriente_porcentaje
                entry['porcentaje_derecho'] = final_porcentaje_derecho_adquiriente
                break
        return temp_storage
    