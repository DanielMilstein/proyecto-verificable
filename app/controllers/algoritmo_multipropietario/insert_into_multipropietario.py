from .algoritmos.regularizacion_patrimonio.algoritmo_regularizacion_patrimonio import AlgoritmoRegularizacionPatrimonio
from .algoritmos.compraventa.algoritmo_compraventa import AlgoritmoCompraventa
from .algoritmos.enajenantes_inexistentes.algoritmo_enajenantes_inexistentes import AlgoritmoEnajenantesInexistentes
from ...models import Formulario, Implicados
from ..table_handlers.multipropietario import MultipropietarioTableHandler

REGULARIZACION_DE_PATRIMONIO = 99
COMPRAVENTA = 8
class ExecuteAlgoritmoMultipropietario:
    def __init__(self):
        self.regularizacion_algorithm = AlgoritmoRegularizacionPatrimonio()
        self.compraventa_algorithm = AlgoritmoCompraventa()
        self.enajenantes_inexistentes_algorithm = AlgoritmoEnajenantesInexistentes()
        self.multipropietario_handler = MultipropietarioTableHandler()

    def execute(self, cne_code, form_data, processed_entries):
        form_data = self._merge_repeated_propietarios(form_data)

        current_propietarios = self._find_current_propietarios(form_data)
        if cne_code == REGULARIZACION_DE_PATRIMONIO:
            return self.regularizacion_algorithm.apply_algorithm_on(form_data, current_propietarios, processed_entries)
        elif cne_code == COMPRAVENTA:
            if self._has_enajenantes_inexistentes(form_data['enajenantes'], current_propietarios):
                return self.enajenantes_inexistentes_algorithm.apply_algorithm_on(form_data, current_propietarios)
            else:
                return self.compraventa_algorithm.apply_algorithm_on(form_data, current_propietarios)
        else:
            return False

    def _merge_repeated_propietarios(self, form_data):
        adquirientes_storage = {}
        enajenantes_storage = {}

        for adquiriente in form_data['adquirientes']:
            rut = adquiriente['rut']
            if rut in adquirientes_storage:
                adquirientes_storage[rut]['porcentaje_derecho'] += adquiriente['porcentaje_derecho']
            else:
                adquirientes_storage[rut] = adquiriente

        for enajenante in form_data['enajenantes']:
            rut = enajenante['rut']
            if rut in enajenantes_storage:
                enajenantes_storage[rut]['porcentaje_derecho'] += enajenante['porcentaje_derecho']
            else:
                enajenantes_storage[rut] = enajenante

        form_data['adquirientes'] = list(adquirientes_storage.values())
        form_data['enajenantes'] = list(enajenantes_storage.values())
        return form_data
    
    def _find_current_propietarios(self, form_data):
        rol = form_data['rol']
        all_forms = self.multipropietario_handler.get_forms_by_rol(rol)
        previous_forms = self._filter_previous_forms(all_forms, form_data['fecha_inscripcion'])
        temp_storage = self._extract_propietarios_from_forms(previous_forms)
        return temp_storage

    def _filter_previous_forms(self, all_forms, current_fecha_inscripcion):
        return [
            form for form in all_forms
            if (form.fecha_inscripcion is None or form.fecha_inscripcion < current_fecha_inscripcion)
        ]

    def _extract_propietarios_from_forms(self, previous_forms):
        temp_storage = []
        for previous_form in previous_forms:
            if not previous_form.ano_vigencia_final:
                propietarios = self.multipropietario_handler.propietario_handler.get_by_multipropietario_id(previous_form.id)
                temp_storage.extend(self._create_propietario_entries(previous_form, propietarios))
        return temp_storage

    def _create_propietario_entries(self, previous_form, propietarios):
        entries = []
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
            entries.append(entry)
        return entries

    def _has_enajenantes_inexistentes(self, enajenantes, current_propietarios):
        current_propietarios_ruts = {p['rut'] for p in current_propietarios}
        for enajenante in enajenantes:
            if enajenante['rut'] not in current_propietarios_ruts:
                return True
        return False

class HandleAlgoritmoMultipropietario:
    def __init__(self):
        self.algorithm_executor = ExecuteAlgoritmoMultipropietario()

    def insert_into_multipropietario(self, form_data, processed_entries):
        return self.execute_algorithm_on(form_data, processed_entries)

    def execute_algorithm_on(self, form_data, processed_entries):
        cne_code = form_data.get('cne', None)

        if cne_code is None:
            matching_formulario = fetch_matching_formulario(form_data)

            if matching_formulario:
                form_data['cne'] = matching_formulario.cne
                if matching_formulario.cne in [COMPRAVENTA, REGULARIZACION_DE_PATRIMONIO]:
                    numero_atencion = matching_formulario.numero_atencion
                    adquirientes, enajenantes = fetch_and_parse_implicados(numero_atencion)
                    form_data['adquirientes'] = adquirientes
                    form_data['enajenantes'] = enajenantes

        cne_code = form_data.get('cne', None)
        return self.algorithm_executor.execute(cne_code, form_data, processed_entries)

def fetch_matching_formulario(form_data):
    return Formulario.query.filter_by(
        fecha_inscripcion=form_data['fecha_inscripcion'],
        rol=form_data['rol'],
        fojas=form_data['fojas'],
        numero_inscripcion=form_data['nro_inscripcion']
    ).first()

def fetch_and_parse_implicados(numero_atencion):
    implicados = Implicados.query.filter_by(numero_atencion=numero_atencion).all()
    adquirientes = []
    enajenantes = []

    for implicado in implicados:
        implicado_dict = {
            'rut': implicado.rut,
            'porcentaje_derecho': implicado.porcentaje_derecho
        }
        if implicado.adquiriente == 1:
            adquirientes.append(implicado_dict)
        else:
            enajenantes.append(implicado_dict)

    return adquirientes, enajenantes