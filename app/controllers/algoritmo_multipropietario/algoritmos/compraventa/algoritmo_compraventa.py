from ....table_handlers.multipropietario import MultipropietarioTableHandler
from .scenarios_compraventa.handle_scenario1 import HandleScenario1
from .scenarios_compraventa.handle_scenario2 import HandleScenario2
from .scenarios_compraventa.handle_scenario3 import HandleScenario3
from .scenarios_compraventa.handle_scenario4 import HandleScenario4
from app.models import db

class AlgoritmoCompraventa:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def apply_algorithm_on(self, form_data):
        adquirientes = form_data.get('adquirientes', [])
        enajenantes = form_data.get('enajenantes', [])

        if self.is_scenario_1(adquirientes):
            handler = HandleScenario1()
        elif self.is_scenario_2(adquirientes):
            handler = HandleScenario2()
        elif self.is_scenario_3(adquirientes, enajenantes):
            handler = HandleScenario3()
        else:
            handler = HandleScenario4()

        handler.handle(form_data)

    def is_scenario_1(self, adquirientes):
        return sum(adquiriente.get('pctje_derecho', 0) for adquiriente in adquirientes) == 100

    def is_scenario_2(self, adquirientes):
        return sum(adquiriente.get('pctje_derecho', 0) for adquiriente in adquirientes) == 0

    def is_scenario_3(self, adquirientes, enajenantes):
        return 0 < sum(adquiriente.get('pctje_derecho', 0) for adquiriente in adquirientes) < 100 and len(adquirientes) == 1 and len(enajenantes) == 1

    def get_existing_forms(self, rol):
        return self.multipropietario_handler.get_forms_by_rol(rol)

    def get_latest_form(self, forms, propietarios):
        for form in sorted(forms, key=lambda x: x.fecha_inscripcion, reverse=True):
            propietarios_linked_to_form = self.get_linked_propietario(form)
            ruts_linked_to_form = {propietario['rut'] for propietario in propietarios_linked_to_form}
            propietarios_ruts = {propietario['rut'] for propietario in propietarios}

            if propietarios_ruts.issubset(ruts_linked_to_form):
                return form

        return None  # Return None if no matching form is found

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

    def find_porcentaje_derecho(self, rut, rol):
        return self.multipropietario_handler.get_pctje_derecho_propietario(rut, rol)

    def upload_multipropietario(self, entry):
        new_form = self.multipropietario_handler.upload_form(
            entry['rol'], 
            entry['fecha_inscripcion'], 
            entry['fojas'], 
            entry['nro_inscripcion'], 
            entry['ano_inscripcion'], 
            entry['ano_vigencia_inicial'], 
            entry['ano_vigencia_final']
        )
        entry['id'] = new_form
        return entry['id']

    def upload_propietario(self, entry):
        new_multipropietario_id = self.upload_multipropietario(entry)
        self.multipropietario_handler.upload_propietario(
            {'rut': entry['rut'], 'porcentaje_derecho': entry['porcentaje_derecho']}, 
            new_multipropietario_id
        )

    def check_if_repeated_enajenante(self, rut, rol, ano_vigencia_inicial):
        self.multipropietario_handler.check_if_repeated_enajenante(rut, rol, ano_vigencia_inicial)
        
