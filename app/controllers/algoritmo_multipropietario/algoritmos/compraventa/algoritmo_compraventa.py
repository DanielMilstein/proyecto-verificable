from ....table_handlers.multipropietario import MultipropietarioTableHandler
from .scenarios_compraventa.handle_scenario1 import HandleScenario1
from .scenarios_compraventa.handle_scenario2 import HandleScenario2
from .scenarios_compraventa.handle_scenario3 import HandleScenario3
from .scenarios_compraventa.handle_scenario4 import HandleScenario4
from app.models import db

class AlgoritmoCompraventa:
    def __init__(self):
        self.multipropietario_handler = MultipropietarioTableHandler()

    def apply_algorithm_on(self, form_data, current_propietarios):
        adquirientes = form_data['adquirientes']
        enajenantes = form_data['enajenantes']

        if self.is_scenario_1(adquirientes):
            handler = HandleScenario1()
        elif self.is_scenario_2(adquirientes):
            handler = HandleScenario2()
        elif self.is_scenario_3(adquirientes, enajenantes):
            handler = HandleScenario3()
        else:
            handler = HandleScenario4()
        
        temp_storage = handler.handle(form_data, current_propietarios)

        grouped_entries = self.group_entries(temp_storage)

        for key, entries in grouped_entries.items():
            self.upload_entries(entries)


    def group_entries(self, entries):
        grouped_entries = {}
        for entry in entries:
            key = (entry['fecha_inscripcion'], entry['fojas'], entry['nro_inscripcion'])
            if key not in grouped_entries:
                grouped_entries[key] = []
            grouped_entries[key].append(entry)
        return grouped_entries

    def is_scenario_1(self, adquirientes):
        return sum(adquiriente['porcentaje_derecho'] for adquiriente in adquirientes) == 100

    def is_scenario_2(self, adquirientes):
        return sum(adquiriente['porcentaje_derecho'] for adquiriente in adquirientes) == 0

    def is_scenario_3(self, adquirientes, enajenantes):
        return 0 < sum(adquiriente['porcentaje_derecho'] for adquiriente in adquirientes) < 100 and len(adquirientes) == 1 and len(enajenantes) == 1
    
    def upload_entries(self, entries):
        multipropietario_id = self.upload_multipropietario(entries[0])
        for entry in entries:
            self.upload_propietario(entry, multipropietario_id)

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

    def upload_propietario(self, entry, multipropietario_id):
        self.multipropietario_handler.upload_propietario(
            {'rut': entry['rut'], 'porcentaje_derecho': entry['porcentaje_derecho']}, 
            multipropietario_id
        )
        
