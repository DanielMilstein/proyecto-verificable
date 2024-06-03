class HandleScenario4():
    def handle(self, form_data):
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
        for entry in temp_storage:
            self.upload_propietario(entry)
