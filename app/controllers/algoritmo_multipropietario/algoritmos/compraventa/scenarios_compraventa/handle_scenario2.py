from ..algoritmo_compraventa import AlgoritmoCompraventa

class HandleScenario2(AlgoritmoCompraventa):
    def handle(self, form_data):
        rol = form_data.get('rol')
        all_forms = self.get_existing_forms(rol)
        previous_form = self.get_latest_form(all_forms)
        prev_storage = self.store_form_data(previous_form)

        for entry in prev_storage:
            self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data.get('fecha_inscripcion').year - 1)

        enajenantes_ruts = [enajenante.get('rut') for enajenante in form_data.get('enajenantes', [])]

        sum_porcentaje_enajenantes = sum([self.find_porcentaje_derecho(rut, rol) for rut in enajenantes_ruts])
        temp_storage = [entry for entry in prev_storage if entry['rut'] not in enajenantes_ruts]
        for rut in enajenantes_ruts:
            self.check_if_repeated_enajenante(rut, rol, form_data.get('fecha_inscripcion').year)

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
            self.upload
