from .....table_handlers.multipropietario import MultipropietarioTableHandler

class HandleScenario1:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def handle(self, form_data, current_propietarios):
        rol = form_data['rol']
        prev_storage = current_propietarios

        enajenantes_ruts = [enajenante['rut'] for enajenante in form_data['enajenantes']]
        sum_porcentaje_enajenantes = self._calculate_sum_porcentaje_enajenantes(enajenantes_ruts, rol)
        temp_storage = [entry for entry in prev_storage if entry['rut'] not in enajenantes_ruts]

        self._update_previous_forms(prev_storage, form_data)
        temp_storage = temp_storage + self._add_adquirientes(form_data, sum_porcentaje_enajenantes, rol)
        temp_storage = self._finalize_entries(temp_storage, form_data, enajenantes_ruts)

        return temp_storage

    def _get_previous_forms(self, all_forms, form_data):
        return [form for form in all_forms if form.fecha_inscripcion < form_data['fecha_inscripcion']]

    def _calculate_sum_porcentaje_enajenantes(self, enajenantes_ruts, rol):
        return sum([self.multipropietario_handler.get_porcentaje_derecho_propietario(rut, rol) for rut in enajenantes_ruts])

    def _update_previous_forms(self, prev_storage, form_data):
        for entry in prev_storage:
            self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data['fecha_inscripcion'].year - 1)

    def _add_adquirientes(self, form_data, sum_porcentaje_enajenantes, rol):
        temp_storage = []
        for adquiriente in form_data['adquirientes']:
            entry = {
                'id': None,
                'rol': rol,
                'fecha_inscripcion': form_data['fecha_inscripcion'],
                'fojas': form_data['fojas'],
                'nro_inscripcion': form_data['nro_inscripcion'],
                'rut': adquiriente['rut'],
                'porcentaje_derecho': adquiriente['porcentaje_derecho'] * sum_porcentaje_enajenantes / 100,
                'ano_vigencia_inicial': form_data['fecha_inscripcion'].year,
                'ano_vigencia_final': None
            }
            temp_storage.append(entry)
        return temp_storage

    def _finalize_entries(self, temp_storage, form_data, enajenantes_ruts):
        adquirientes_ruts = [adquiriente['rut'] for adquiriente in form_data['adquirientes']]
        for entry in temp_storage:
            if (entry['rut'] in enajenantes_ruts) or (entry['rut'] in adquirientes_ruts):
                entry['ano_inscripcion'] = form_data['fecha_inscripcion'].year
            else:
                del entry['multipropietario_id']
            entry['ano_vigencia_inicial'] = form_data['fecha_inscripcion'].year
            entry['ano_vigencia_final'] = None
        
        return temp_storage
