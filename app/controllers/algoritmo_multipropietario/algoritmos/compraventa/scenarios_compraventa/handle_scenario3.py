from ..algoritmo_compraventa import AlgoritmoCompraventa

class HandleScenario3(AlgoritmoCompraventa):
    def handle(self, form_data):
        rol = form_data.get('rol')
        all_forms = self.get_existing_forms(rol)
        previous_form = self.get_latest_form(all_forms)
        temp_storage = self.store_form_data(previous_form)

        for entry in temp_storage:
            if entry['ano_inscripcion'] < form_data.get('fecha_inscripcion').year - 1:
                self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data.get('fecha_inscripcion').year - 1)

        enajenante_rut = [enajenante.get('rut') for enajenante in form_data.get('enajenantes', [])][0]
        enajenante_pctje = [enajenante.get('pctje_derecho') for enajenante in form_data.get('enajenantes', [])][0]
        
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

        if self.find_porcentaje_derecho(enajenante_rut, rol):
            prev_porcentaje_derecho = self.find_porcentaje_derecho(enajenante_rut, rol)
        
        final_porcentaje_derecho_enajenante = prev_porcentaje_derecho - (enajenante_pctje / 100 * prev_porcentaje_derecho)
        entry['porcentaje_derecho'] = final_porcentaje_derecho_enajenante
        
        for entry in temp_storage:
            if entry["rut"] == adquiriente_rut:
                final_porcentaje_derecho_adquiriente = entry['porcentaje_derecho'] / 100 * prev_porcentaje_derecho
                entry['porcentaje_derecho'] = final_porcentaje_derecho_adquiriente
                break

        for entry in temp_storage:
            if entry['rut'] == adquiriente_rut:
                entry['ano_inscripcion'] = form_data.get('fecha_inscripcion').year
            else:
                del entry['multipropietario_id']
                entry['id'] = None
            entry['ano_vigencia_inicial'] = form_data.get('fecha_inscripcion').year
            entry['ano_vigencia_final'] = None

        for entry in temp_storage:
            self.upload_propietario(entry)
