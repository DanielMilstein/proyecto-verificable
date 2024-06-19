from .....table_handlers.multipropietario import MultipropietarioTableHandler
class HandleScenario2():
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def handle(self, form_data):
        rol = form_data['rol']
        all_forms = self.multipropietario_handler.get_forms_by_rol(rol)
        previous_forms = [form for form in all_forms if form.fecha_inscripcion < form_data['fecha_inscripcion']]
        #previous_form = max(previous_forms, key=lambda x: x.fecha_inscripcion) if previous_forms else None
        #prev_storage = self.store_form_data(previous_form)
        
        prev_storage = []
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
                    prev_storage.append(entry)
        enajenantes_ruts = [enajenante['rut'] for enajenante in form_data['enajenantes']]

        sum_porcentaje_enajenantes = sum([self.multipropietario_handler.get_pctje_derecho_propietario(rut, rol) for rut in enajenantes_ruts])
        temp_storage = [entry for entry in prev_storage if entry['rut'] not in enajenantes_ruts]
        print(temp_storage)
        for rut in enajenantes_ruts:
            self.check_if_repeated_enajenante(rut, rol, form_data['fecha_inscripcion'].year)

        num_adquirientes = len(form_data['adquirientes'])
        new_porcentaje_derecho = sum_porcentaje_enajenantes / num_adquirientes

        for entry in prev_storage:
            self.multipropietario_handler.update_form(entry['multipropietario_id'], form_data.get('fecha_inscripcion').year - 1)

        adquirientes_ruts = []
        for adquiriente in form_data['adquirientes']:
            adquirientes_ruts.append(adquiriente['rut'])
            entry = {
                'id': None,
                'rol': rol,
                'fecha_inscripcion': form_data['fecha_inscripcion'],
                'fojas': form_data['fojas'],
                'nro_inscripcion': form_data['nro_inscripcion'],
                'rut': adquiriente['rut'],
                'porcentaje_derecho': new_porcentaje_derecho,
                'ano_vigencia_inicial': form_data['fecha_inscripcion'].year,
                'ano_vigencia_final': None
            }
            temp_storage.append(entry)

        for entry in temp_storage:
            if (entry['rut'] in enajenantes_ruts) or (entry['rut'] in adquirientes_ruts):
                entry['ano_inscripcion'] = form_data.get('fecha_inscripcion').year
            else:
                del entry['multipropietario_id']
                entry['id'] = None
            #entry['ano_vigencia_inicial'] = form_data.get('fecha_inscripcion').year
            #entry['ano_vigencia_final'] = None
        return temp_storage
    
    def store_form_data(self, previous_form):
        temp_storage = []
        if previous_form:
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
    
    def check_if_repeated_enajenante(self, rut, rol, ano_vigencia_inicial):
        self.multipropietario_handler.check_if_repeated_enajenante(rut, rol, ano_vigencia_inicial)
