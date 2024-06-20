from .....table_handlers.multipropietario import MultipropietarioTableHandler

class HandleScenario4:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def handle(self, form_data):
        rol = form_data['rol']
        all_forms = self.multipropietario_handler.get_forms_by_rol(rol)
        previous_forms = [form for form in all_forms if form.fecha_inscripcion < form_data['fecha_inscripcion']]

        temp_storage = self._find_current_propietarios(form_data, previous_forms)
        self._update_previous_forms(temp_storage, form_data)
        self._process_enajenantes(temp_storage, form_data)
        self._add_adquirientes(temp_storage, form_data)

        temp_storage = [entry for entry in temp_storage if entry['porcentaje_derecho'] > 0]
        self._finalize_entries(temp_storage, form_data)

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
