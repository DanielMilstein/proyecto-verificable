from .....table_handlers.multipropietario import MultipropietarioTableHandler

class HandleScenario4:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def handle(self, form_data, current_propietarios):
        temp_storage = current_propietarios
        self._update_previous_forms(temp_storage, form_data)

        self._process_enajenantes(temp_storage, form_data)
        self._add_adquirientes(temp_storage, form_data)

        temp_storage = [entry for entry in temp_storage if entry['porcentaje_derecho'] > 0]
        self._finalize_entries(temp_storage, form_data)

        return temp_storage

    def _update_previous_forms(self, temp_storage, form_data):
        for entry in temp_storage:
            self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data.get('fecha_inscripcion').year - 1)

    def _process_enajenantes(self, temp_storage, form_data):
        enajenantes_ruts = [enajenante['rut'] for enajenante in form_data['enajenantes']]
        for entry in temp_storage:
            if entry['rut'] in enajenantes_ruts:
                prev_porcentaje_derecho = entry['porcentaje_derecho']
                for enajenante in form_data['enajenantes']:
                    if enajenante['rut'] == entry['rut']:
                        enajenante_porcentaje = enajenante['porcentaje_derecho']
                        final_porcentaje_derecho_enajenante = prev_porcentaje_derecho - enajenante_porcentaje
                        entry['porcentaje_derecho'] = final_porcentaje_derecho_enajenante

    def _add_adquirientes(self, temp_storage, form_data):
        for adquiriente in form_data['adquirientes']:
            entry = {
                'id': None,
                'rol': form_data['rol'],
                'fecha_inscripcion': form_data['fecha_inscripcion'],
                'fojas': form_data['fojas'],
                'nro_inscripcion': form_data['nro_inscripcion'],
                'rut': adquiriente['rut'],
                'porcentaje_derecho': adquiriente['porcentaje_derecho'],
                'ano_vigencia_inicial': form_data['fecha_inscripcion'].year,
                'ano_vigencia_final': None
            }
            temp_storage.append(entry)

    def _finalize_entries(self, temp_storage, form_data):
        adquirientes_ruts = [adquiriente['rut'] for adquiriente in form_data['adquirientes']]
        for entry in temp_storage:
            if entry['rut'] in adquirientes_ruts:
                entry['ano_inscripcion'] = form_data['fecha_inscripcion'].year
            else:
                del entry['multipropietario_id']
                entry['id'] = None

            entry['ano_vigencia_inicial'] = form_data.get('fecha_inscripcion').year
            entry['ano_vigencia_final'] = None
