from .....table_handlers.multipropietario import MultipropietarioTableHandler
class HandleScenario3():
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def handle(self, form_data):
        rol = form_data['rol']
        all_forms = self.multipropietario_handler.get_forms_by_rol(rol)
        previous_forms = [form for form in all_forms if form.fecha_inscripcion < form_data['fecha_inscripcion']]

        enajenante_rut = [enajenante['rut'] for enajenante in form_data['enajenantes']][0]
        enajenante_porcentaje = [enajenante['porcentaje_derecho'] for enajenante in form_data['enajenantes']][0]
        
        temp_storage = self._find_current_propietarios(form_data, previous_forms)

        self._update_previous_forms(temp_storage, form_data)

        for adquiriente in form_data['adquirientes']:
            adquiriente_rut = adquiriente['rut']
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

        adquiriente_porcentaje = enajenante_porcentaje / 100 * prev_porcentaje_derecho
        temp_storage = self._find_porcentaje_adquiriente(temp_storage, adquiriente_rut, adquiriente_porcentaje)

        temp_storage = self._finalize_entries(temp_storage, form_data, enajenante_rut, adquiriente_rut)
        return temp_storage
    
    def _find_current_propietarios(self, form_data, previous_forms):
        temp_storage = []
        for previous_form in previous_forms:
            if previous_form.fecha_inscripcion < form_data['fecha_inscripcion'] and not previous_form.ano_vigencia_final:
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
    
    def _update_previous_forms(self, temp_storage, form_data):
        for entry in temp_storage:
            self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data['fecha_inscripcion'].year - 1)

    def _process_adquirientes(self, form_data, adquiriente):
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
        return entry
    
    def _find_porcentaje_enajenante(self, temp_storage, enajenante_rut, enajenante_porcentaje, rol):
        prev_porcentaje_derecho = 0
        for entry in temp_storage:
            if entry['rut'] == enajenante_rut:
                prev_porcentaje_derecho = entry['porcentaje_derecho']
                final_porcentaje_derecho_enajenante = prev_porcentaje_derecho - (enajenante_porcentaje / 100 * prev_porcentaje_derecho)
                entry['porcentaje_derecho'] = final_porcentaje_derecho_enajenante
                break

        if not prev_porcentaje_derecho and self.multipropietario_handler.get_pctje_derecho_propietario(enajenante_rut, rol):
            prev_porcentaje_derecho = self.multipropietario_handler.get_pctje_derecho_propietario(enajenante_rut, rol)
        
        return temp_storage, prev_porcentaje_derecho
    
    def _find_porcentaje_adquiriente(self, temp_storage, adquiriente_rut, adquiriente_porcentaje):
        for entry in temp_storage:
            if entry["rut"] == adquiriente_rut:
                final_porcentaje_derecho_adquiriente = adquiriente_porcentaje
                entry['porcentaje_derecho'] = final_porcentaje_derecho_adquiriente
                break
        return temp_storage
    
    def _finalize_entries(self, temp_storage, form_data, enajenante_rut, adquiriente_rut):
        for entry in temp_storage:
            if entry['rut'] == enajenante_rut:
                continue
            if entry['rut'] == adquiriente_rut:
                entry['ano_inscripcion'] = form_data['fecha_inscripcion'].year
            else:
                del entry['multipropietario_id']
                entry['id'] = None
            entry['ano_vigencia_inicial'] = form_data['fecha_inscripcion'].year
            entry['ano_vigencia_final'] = None
        
        return temp_storage